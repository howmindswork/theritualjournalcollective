#!/usr/bin/env python3
"""
RJC Analyst: Pulls GSC data, scores clusters, generates new topic_queue.
Run by GitHub Actions every Sunday at 11pm UTC.
"""
import os
import json
import re
import datetime
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google import genai as google_genai
from google.genai import types as google_types

def call_llm(prompt, max_tokens=2048):
    # Try Gemini keys (primary + secondary)
    for gkey in filter(None, [os.environ.get("GEMINI_API_KEY"), os.environ.get("GEMINI_API_KEY_BLOG")]):
        for gmodel in ["gemini-2.0-flash", "gemini-2.0-flash-lite"]:
            try:
                client = google_genai.Client(api_key=gkey)
                response = client.models.generate_content(
                    model=gmodel,
                    contents=prompt,
                    config=google_types.GenerateContentConfig(max_output_tokens=max_tokens)
                )
                print(f"LLM: {gmodel} succeeded")
                return response.text
            except Exception as e:
                print(f"Gemini {gmodel} failed: {e}")

    # Try Cerebras via direct HTTP (1M tokens/day free)
    cerebras_key = os.environ.get("CEREBRAS_API_KEY")
    if cerebras_key:
        try:
            import urllib.request
            data = json.dumps({"model": "qwen-3-235b-a22b-instruct-2507", "messages": [{"role": "user", "content": prompt}], "max_tokens": min(max_tokens, 8192)}).encode()
            req = urllib.request.Request("https://api.cerebras.ai/v1/chat/completions", data=data,
                headers={"Authorization": f"Bearer {cerebras_key}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
            print("LLM: Cerebras succeeded")
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Cerebras failed: {e}")

    # Try Groq with key rotation (all 13 keys, two models each)
    groq_keys = [v for k, v in sorted(os.environ.items())
                 if k.startswith("GROQ_API_KEY") and v]
    for key in groq_keys:
        for gmodel in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
            try:
                from groq import Groq
                client = Groq(api_key=key)
                response = client.chat.completions.create(
                    model=gmodel,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                print(f"LLM: Groq {gmodel} succeeded")
                return response.choices[0].message.content
            except Exception as e:
                print(f"Groq {gmodel} failed: {e}")
                if "rate_limit" not in str(e).lower():
                    break

    raise RuntimeError("All LLM providers failed")

REPO_ROOT = Path(__file__).parent.parent
QUEUE_FILE = REPO_ROOT / "topic_queue.json"
LOG_FILE = REPO_ROOT / "published_log.json"
MEMORY_FILE = REPO_ROOT / "performance_memory.json"
BRAND_CONTEXT_FILE = REPO_ROOT / "brand-context.md"

SITE_URL = "https://theritualjournalcollective.com/"

def get_gsc_service():
    key_json = json.loads(os.environ["GSC_SERVICE_ACCOUNT_KEY"])
    creds = service_account.Credentials.from_service_account_info(
        key_json,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
    )
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)

def fetch_gsc_data(service, days=90):
    end_date = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
    start_date = (datetime.date.today() - datetime.timedelta(days=days+3)).isoformat()

    result = service.searchanalytics().query(
        siteUrl=SITE_URL,
        body={
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["page", "query"],
            "rowLimit": 5000
        }
    ).execute()

    return result.get("rows", [])

def score_cluster(clicks, impressions, avg_position, trend_multiplier, gap_count):
    click_score = min((clicks / 500) * 40, 40)
    trend_score = trend_multiplier * 20
    position_score = ((21 - min(avg_position or 21, 21)) / 21) * 30
    gap_score = gap_count * 2
    return round(click_score + trend_score + position_score + gap_score, 1)

def main():
    with open(LOG_FILE) as f:
        published_log = json.load(f)

    with open(QUEUE_FILE) as f:
        topic_queue = json.load(f)

    with open(MEMORY_FILE) as f:
        memory = json.load(f)

    # Build URL-to-article map
    url_to_article = {entry["url"]: entry for entry in published_log}

    # Fetch GSC data
    service = get_gsc_service()
    rows = fetch_gsc_data(service)

    # Aggregate per cluster
    cluster_data = {}
    gap_queries = []

    for row in rows:
        page = row["keys"][0].replace(SITE_URL, "")
        query = row["keys"][1]
        clicks = row.get("clicks", 0)
        impressions = row.get("impressions", 0)
        position = row.get("position", 21)

        article = url_to_article.get(page)
        cluster = article["cluster"] if article else "unknown"

        if cluster not in cluster_data:
            cluster_data[cluster] = {"clicks": 0, "impressions": 0, "positions": [], "gap_queries": []}

        cluster_data[cluster]["clicks"] += clicks
        cluster_data[cluster]["impressions"] += impressions
        cluster_data[cluster]["positions"].append(position)

        # Detect gap: high impressions, low clicks, no dedicated post
        if impressions > 500 and clicks < 20:
            has_dedicated_post = any(
                entry for entry in published_log
                if query.lower() in entry.get("target_query", "").lower()
            )
            if not has_dedicated_post:
                gap_queries.append({"query": query, "impressions": impressions, "clicks": clicks, "cluster": cluster})

    # Score clusters
    scored_clusters = {}
    for cluster, data in cluster_data.items():
        avg_pos = sum(data["positions"]) / len(data["positions"]) if data["positions"] else 21
        scored_clusters[cluster] = {
            "clicks_7d": data["clicks"],
            "impressions_7d": data["impressions"],
            "avg_position": round(avg_pos, 1),
            "gap_queries": data["gap_queries"][:5],
            "score": score_cluster(data["clicks"], data["impressions"], avg_pos, 1.0, len(data["gap_queries"]))
        }

    # Update memory
    memory["last_analysis"] = datetime.date.today().isoformat()
    memory["clusters"].update(scored_clusters)
    memory["gap_queries"] = sorted(gap_queries, key=lambda x: x["impressions"], reverse=True)[:20]

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

    # Call Claude to suggest new topics
    queued_count = len([t for t in topic_queue if t["status"] == "queued"])

    if queued_count < 6:
        brand_context = BRAND_CONTEXT_FILE.read_text()

        analysis_prompt = f"""
You are the editorial strategist for The Ritual Journal Collective.

BRAND CONTEXT:
{brand_context}

CURRENT PERFORMANCE (last 90 days):
{json.dumps(scored_clusters, indent=2)}

GAP QUERIES (high impressions, no dedicated article):
{json.dumps(gap_queries[:10], indent=2)}

ALREADY PUBLISHED:
{json.dumps([e["title"] for e in published_log], indent=2)}

ALREADY QUEUED:
{json.dumps([t["title"] for t in topic_queue if t["status"] == "queued"], indent=2)}

Generate 5 new article topics to add to the queue. Focus on:
1. Clusters scoring highest (more momentum there)
2. Gap queries with 500+ impressions
3. Topics we haven't covered yet

Return a JSON array of 5 objects with these fields:
- title (string)
- cluster (one of: grief-rituals, polyvagal, ifs, emotional-release, morning-rituals, healing-rituals)
- slug (kebab-case URL slug)
- target_query (the search query this article targets)
- author (one of: sable-march, eden-voss, m-ellis)

Return ONLY valid JSON. No explanation.
"""

        new_topics_json = call_llm(analysis_prompt, max_tokens=2048).strip()
        # Clean JSON
        new_topics_json = re.sub(r'^```json?\n', '', new_topics_json)
        new_topics_json = re.sub(r'\n```$', '', new_topics_json)

        new_topics = json.loads(new_topics_json)
        max_id = max((t["id"] for t in topic_queue), default=0)

        for i, topic in enumerate(new_topics):
            topic["id"] = max_id + i + 1
            topic["status"] = "queued"
            topic["priority"] = max_id + i + 1
            topic_queue.append(topic)

        with open(QUEUE_FILE, "w") as f:
            json.dump(topic_queue, f, indent=2)

        print(f"Added {len(new_topics)} new topics to queue.")

    print("Analysis complete.")

if __name__ == "__main__":
    main()

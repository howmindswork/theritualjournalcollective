#!/usr/bin/env python3
"""
RJC Publisher: Generates and publishes one article per run.
Run by GitHub Actions Mon/Wed/Fri at 8am UTC.
"""
import os
import json
import re
import sys
import datetime
from pathlib import Path
import anthropic

REPO_ROOT = Path(__file__).parent.parent
QUEUE_FILE = REPO_ROOT / "topic_queue.json"
LOG_FILE = REPO_ROOT / "published_log.json"
BRAND_CONTEXT_FILE = REPO_ROOT / "brand-context.md"
POSTS_DIR = REPO_ROOT / "posts"

ARTICLE_TEMPLATE_PROMPT = """
You are writing for The Ritual Journal Collective, an independent editorial publication.

BRAND CONTEXT:
{brand_context}

ARTICLE TO WRITE:
- Title: {title}
- Target query: {target_query}
- Author: {author_name} ({author_descriptor})
- Cluster: {cluster}
- Slug: {slug}

ARTICLE STRUCTURE (follow exactly):

1. OPENING (40-60 words EXACTLY): First sentence directly answers the target query. No hooks, no teasers. Sentences 2-3 explain the mechanism. Sentence 4 states what the reader will get.

2. Use these H2 sections in order:
   - "What is a [target term]?" (40-60 word paragraph)
   - "How does [target term] work?" (40-60 word paragraph)
   - "How to do [target term]: Step-by-Step" (numbered list, 5-8 steps, max 20 words each, bold the action verb)
   - "Signs it's working" (bullet list, 4-8 items)
   - "When to use it" (40-60 word paragraph)
   - "[Term] vs [related practice] vs [related practice]" (HTML table comparing 3 things)
   - "What the science says" (100-150 words, cite ONE real published study with PubMed/DOI link)
   - "My experience with this" (100-200 words, FIRST PERSON as the author)

3. FAQ (6-8 questions matching likely "People Also Ask" queries, 40-60 words each answer)

4. Related Practices (3-4 internal links as unordered list)

5. Sources (3-5 outbound links to real PubMed/NIH/APA papers)

WORD COUNT: 1,200-2,000 words total

OUTPUT: Return a complete, valid HTML document. Do not use markdown. Use these exact CSS classes:
- article-summary (on the opening paragraph)
- step-list (on the how-to ordered list)
- comparison-table (on the comparison table wrapper div)
- disclaimer-block (required disclaimer at end of article body)
- faq-section and faq-item and faq-question and faq-answer classes
- product-rec (for product recommendation callout — include naturally, 1 per article max)
- related-practices (on the internal links section)
- sources (on the citations section)

Include valid JSON-LD in <head>:
1. BlogPosting schema with author, datePublished, dateModified (today: {today}), speakable (cssSelector: [".article-summary", "h2"])
2. FAQPage schema with all FAQ questions and answers

CSS path: ../../assets/style.css (articles are 2 levels deep in posts/cluster/)
Tracking JS path: ../../assets/tracking.js

Full HTML document, starting with <!DOCTYPE html>, ending with </html>.
"""

def get_author_info(author_slug):
    authors = {
        "sable-march": {
            "name": "Sable March",
            "descriptor": "Somatic Grief Practitioner & Ritual Guide",
            "url": "../../authors/sable-march.html"
        },
        "eden-voss": {
            "name": "Eden Voss",
            "descriptor": "Trauma-Informed Wellness Writer",
            "url": "../../authors/eden-voss.html"
        },
        "m-ellis": {
            "name": "M. Ellis",
            "descriptor": "Psychology Researcher & Grief Writer",
            "url": "../../authors/m-ellis.html"
        }
    }
    return authors.get(author_slug, authors["sable-march"])

def validate_article(html):
    checks = {
        "word_count": len(re.findall(r'\b\w+\b', re.sub('<[^>]+>', '', html))),
        "has_faq": 'faq-section' in html,
        "has_schema": 'application/ld+json' in html,
        "has_author": 'article-meta' in html,
        "has_disclaimer": 'disclaimer-block' in html,
    }

    if checks["word_count"] < 1000:
        raise ValueError(f"Article too short: {checks['word_count']} words")
    if not checks["has_faq"]:
        raise ValueError("Missing FAQ section")
    if not checks["has_schema"]:
        raise ValueError("Missing JSON-LD schema")

    return checks

def regenerate_sitemap(published_log):
    """Regenerate sitemap.xml including all published articles."""
    static_pages = [
        ("", "weekly", "1.0"),
        ("about.html", "monthly", "0.8"),
        ("editorial-standards.html", "monthly", "0.7"),
        ("contact.html", "monthly", "0.5"),
        ("disclaimer.html", "monthly", "0.4"),
        ("privacy-policy.html", "monthly", "0.4"),
        ("authors/sable-march.html", "monthly", "0.7"),
        ("authors/eden-voss.html", "monthly", "0.7"),
        ("authors/m-ellis.html", "monthly", "0.7"),
    ]

    base = "https://theritualjournalcollective.com/"
    urls = []
    for path, freq, priority in static_pages:
        urls.append(f'  <url><loc>{base}{path}</loc><changefreq>{freq}</changefreq><priority>{priority}</priority></url>')

    for entry in published_log:
        urls.append(f'  <url><loc>{base}{entry["url"]}</loc><changefreq>monthly</changefreq><priority>0.9</priority><lastmod>{entry["published_date"]}</lastmod></url>')

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '\n'.join(urls)
    sitemap += '\n</urlset>'

    (REPO_ROOT / "sitemap.xml").write_text(sitemap)
    print("Sitemap regenerated.")

def main():
    with open(QUEUE_FILE) as f:
        queue = json.load(f)

    pending = [item for item in queue if item.get("status") == "queued"]
    if not pending:
        print("No queued articles. Exiting.")
        sys.exit(0)

    topic = pending[0]
    print(f"Publishing: {topic['title']}")

    brand_context = BRAND_CONTEXT_FILE.read_text()
    author_info = get_author_info(topic["author"])
    today = datetime.date.today().isoformat()

    prompt = ARTICLE_TEMPLATE_PROMPT.format(
        brand_context=brand_context,
        title=topic["title"],
        target_query=topic["target_query"],
        author_name=author_info["name"],
        author_descriptor=author_info["descriptor"],
        cluster=topic["cluster"],
        slug=topic["slug"],
        today=today
    )

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}]
    )

    html = message.content[0].text

    # Strip markdown code fences if present
    html = re.sub(r'^```html?\n', '', html, flags=re.MULTILINE)
    html = re.sub(r'\n```$', '', html, flags=re.MULTILINE)

    validation = validate_article(html)
    print(f"Validation passed: {validation}")

    out_dir = POSTS_DIR / topic["cluster"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{topic['slug']}.html"
    out_path.write_text(html)
    print(f"Written: {out_path}")

    # Update queue
    for item in queue:
        if item["id"] == topic["id"]:
            item["status"] = "published"
            item["published_date"] = today
            break

    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)

    # Update published log
    with open(LOG_FILE) as f:
        published_log = json.load(f)

    published_log.append({
        "id": topic["id"],
        "title": topic["title"],
        "url": f"posts/{topic['cluster']}/{topic['slug']}.html",
        "cluster": topic["cluster"],
        "target_query": topic["target_query"],
        "author": topic["author"],
        "published_date": today,
        "clicks_total": 0,
        "impressions_total": 0,
        "avg_position": None
    })

    with open(LOG_FILE, "w") as f:
        json.dump(published_log, f, indent=2)

    regenerate_sitemap(published_log)

    # Write title for commit message
    Path("/tmp/article_title.txt").write_text(topic["title"][:60])

    print("Done.")

if __name__ == "__main__":
    main()

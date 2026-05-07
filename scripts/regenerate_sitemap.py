#!/usr/bin/env python3
"""Regenerate sitemap.xml from published_log.json."""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

def main():
    with open(REPO_ROOT / "published_log.json") as f:
        published_log = json.load(f)

    base = "https://theritualjournalcollective.com/"
    static_pages = [
        ("", "weekly", "1.0"), ("about.html", "monthly", "0.8"),
        ("editorial-standards.html", "monthly", "0.7"), ("contact.html", "monthly", "0.5"),
        ("disclaimer.html", "monthly", "0.4"), ("privacy-policy.html", "monthly", "0.4"),
        ("authors/sable-march.html", "monthly", "0.7"), ("authors/eden-voss.html", "monthly", "0.7"),
        ("authors/m-ellis.html", "monthly", "0.7"),
    ]

    urls = []
    for path, freq, priority in static_pages:
        urls.append(f'  <url><loc>{base}{path}</loc><changefreq>{freq}</changefreq><priority>{priority}</priority></url>')

    for entry in published_log:
        urls.append(f'  <url><loc>{base}{entry["url"]}</loc><changefreq>monthly</changefreq><priority>0.9</priority><lastmod>{entry["published_date"]}</lastmod></url>')

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '\n'.join(urls) + '\n</urlset>'
    (REPO_ROOT / "sitemap.xml").write_text(sitemap)
    print("Done.")

if __name__ == "__main__":
    main()

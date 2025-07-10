# research.py

import requests
import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm

def crawl_and_save(urls, output_file="web_dataset.jsonl", max_pages=10, allowed_domain=None):
    """
    Crawl a list of URLs and save the cleaned content to a JSONL file.

    Each line in the output will contain:
    {
        "url": "<page_url>",
        "content": "<cleaned_text_content>"
    }
    """
    crawled = load_existing_urls(output_file)
    saved = 0
    visited = set()

    with open(output_file, "a", encoding="utf-8") as f_out:
        queue = list(urls)

        for url in tqdm(queue, desc="Crawling URLs"):
            if url in crawled or url in visited or saved >= max_pages:
                continue

            visited.add(url)

            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code != 200:
                    print(f"❌ Skipped {url} — Status Code: {resp.status_code}")
                    continue

                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    print(f"❌ Skipped {url} — Not HTML (Content-Type: {content_type})")
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                # Basic cleanup
                for tag in soup(["script", "style", "noscript"]):
                    tag.decompose()

                content = soup.get_text(separator="\n", strip=True)

                if not content:
                    print(f"❌ Skipped {url} — No usable content")
                    continue

                # Save
                entry = {"url": url, "content": content}
                f_out.write(json.dumps(entry, ensure_ascii=False) + "\n")
                saved += 1
                crawled.add(url)
                print(f"✅ Saved: {url}")

                # Optional: follow links on the same domain
                if allowed_domain:
                    for link_tag in soup.find_all("a", href=True):
                        full_url = urljoin(url, link_tag["href"])
                        if allowed_domain in full_url and full_url not in crawled and full_url not in visited:
                            queue.append(full_url)

            except Exception as e:
                print(f"❌ Failed to crawl {url}: {e}")

    print(f"✅ Done. Saved {saved} pages to {output_file}")

def load_existing_urls(output_file):
    if not os.path.exists(output_file):
        return set()
    with open(output_file, "r", encoding="utf-8") as f:
        return {json.loads(line).get("url") for line in f if line.strip()}


# Start crawling
start_urls = [
    "https://realpython.com/python-web-scraping-practical-introduction/",
    "https://www.geeksforgeeks.org/python-programming-language/"
]

crawl_and_save(
    start_urls,
    output_file="python_articles.jsonl",
    max_pages=5,
    allowed_domain="realpython.com"
)

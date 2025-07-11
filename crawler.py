# crawler.py

import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def crawl_and_save(start_urls, output_file="web_corpus.jsonl", max_pages=5, allowed_domain=None, append=True):
    saved = 0
    queue = list(dict.fromkeys(start_urls))
    visited = set()
    file_mode = "a" if append else "w"

    crawled = set()
    if append:
        crawled = load_existing_urls(output_file)

    with open(output_file, file_mode, encoding="utf-8") as f_out:
        from tqdm import tqdm

        while queue and saved < max_pages:
            url = queue.pop(0).split("#")[0].rstrip("/")
            if url in visited or url in crawled:
                continue

            visited.add(url)

            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code != 200 or "text/html" not in resp.headers.get("Content-Type", ""):
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                for tag in soup(["script", "style", "noscript"]):
                    tag.decompose()
                content = soup.get_text(separator="\n", strip=True)

                if not content or len(content) < 200:
                    continue

                f_out.write(json.dumps({"url": url, "content": content}, ensure_ascii=False) + "\n")
                saved += 1
                crawled.add(url)
                print(f"✅ Saved: {url}")

                if allowed_domain:
                    for tag in soup.find_all("a", href=True):
                        full_url = urljoin(url, tag["href"]).split("#")[0].rstrip("/")
                        if allowed_domain in urlparse(full_url).netloc:
                            if full_url not in crawled and full_url not in visited:
                                queue.append(full_url)

            except Exception as e:
                print(f"❌ Error on {url}: {e}")

    print(f"\n✅ Done. Saved {saved} new page(s) to {output_file}")

def load_existing_urls(output_file):
    if not os.path.exists(output_file):
        return set()
    with open(output_file, "r", encoding="utf-8") as f:
        return {
            item["url"]
            for line in f if line.strip()
            for item in [json.loads(line)]
            if isinstance(item, dict) and "url" in item
        }

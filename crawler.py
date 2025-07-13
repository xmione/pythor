import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

DISALLOWED_EXTENSIONS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg",
    ".zip", ".tar", ".gz", ".rar", ".exe", ".dmg",
    ".mp4", ".avi", ".mov", ".mp3", ".wav"
}

def crawl_and_save(
    start_urls,
    output_file="./datasets/web_corpus.jsonl",
    max_pages=10,
    allowed_domains=None,
    append=True,
    max_depth=2
):
    saved = 0
    visited = set()
    file_mode = "a" if append else "w"
    crawled = set()

    if append:
        crawled = load_existing_urls(output_file)

    # queue will contain tuples of (url, depth)
    queue = [(url, 0) for url in dict.fromkeys(start_urls)]

    with open(output_file, file_mode, encoding="utf-8") as f_out:
        while queue:
            if saved >= max_pages:
                break

            url, depth = queue.pop(0)
            url = url.split("#")[0].rstrip("/")

            if url in visited or url in crawled or has_disallowed_extension(url):
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

                # Expand links (if depth limit not exceeded)
                if depth < max_depth:
                    for tag in soup.find_all("a", href=True):
                        full_url = urljoin(url, tag["href"]).split("#")[0].rstrip("/")
                        domain = urlparse(full_url).netloc

                        if (
                            not has_disallowed_extension(full_url)
                            and full_url not in visited
                            and full_url not in crawled
                            and (
                                allowed_domains is None
                                or any(allowed in domain for allowed in allowed_domains)
                            )
                        ):
                            queue.append((full_url, depth + 1))

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

def has_disallowed_extension(url):
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in DISALLOWED_EXTENSIONS)

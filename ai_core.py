# ai_core.py

import os
import json
import traceback
import json
import os

from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "gpt2"
CACHE_DIR = os.path.expanduser("~/.cache/huggingface/transformers")
DATASET_FILE = "python_articles.jsonl"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)

def generate_response(prompt: str, max_tokens=150):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(
        input_ids,
        max_length=len(input_ids[0]) + max_tokens,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )
    return tokenizer.decode(output[0], skip_special_tokens=True)

def run_python_code(code: str):
    try:
        exec_locals = {}
        exec(code, {}, exec_locals)
        return True, exec_locals
    except Exception:
        error = traceback.format_exc()
        return False, error

def save_to_dataset(instruction: str, code: str):
    with open(DATASET_FILE, "a", encoding="utf-8") as f:
        json.dump({"instruction": instruction, "code": code}, f)
        f.write("\n")

def load_json_dataset(path=DATASET_FILE):
    if os.path.exists(path):
        try:
            texts = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        item = json.loads(line.strip())
                        if isinstance(item, dict) and "code" in item:
                            texts.append(item["code"])
                    except json.JSONDecodeError:
                        continue
            return "\n".join(texts)
        except Exception as e:
            print(f"⚠️ Failed to load dataset: {e}")
    return ""

# def crawl_and_save(start_urls, output_file="python_articles.jsonl", max_pages=5, allowed_domain=None, append=True):
#     saved = 0
#     queue = list(dict.fromkeys(start_urls))  # remove duplicates, keep order
#     visited = set()
#     file_mode = "a" if append else "w"

#     crawled = set()
#     if append:
#         crawled = load_existing_urls(output_file)

#     with open(output_file, file_mode, encoding="utf-8") as f_out:
#         from tqdm import tqdm
#         from bs4 import BeautifulSoup
#         from urllib.parse import urljoin, urlparse
#         import requests
#         import json

#         while queue and saved < max_pages:
#             url = queue.pop(0).split("#")[0].rstrip("/")

#             if url in visited or url in crawled:
#                 continue

#             visited.add(url)

#             try:
#                 response = requests.get(url, timeout=10)
#                 if response.status_code != 200:
#                     continue
#                 if "text/html" not in response.headers.get("Content-Type", ""):
#                     continue

#                 soup = BeautifulSoup(response.text, "html.parser")
#                 for tag in soup(["script", "style", "noscript"]):
#                     tag.decompose()
#                 content = soup.get_text(separator="\n", strip=True)

#                 if not content or len(content) < 200:
#                     continue

#                 f_out.write(json.dumps({"url": url, "content": content}, ensure_ascii=False) + "\n")
#                 saved += 1
#                 crawled.add(url)
#                 print(f"✅ Saved: {url}")

#                 # Expand crawl
#                 if allowed_domain:
#                     for tag in soup.find_all("a", href=True):
#                         full_url = urljoin(url, tag["href"]).split("#")[0].rstrip("/")
#                         if allowed_domain in urlparse(full_url).netloc:
#                             if full_url not in crawled and full_url not in visited:
#                                 queue.append(full_url)

#             except Exception as e:
#                 print(f"❌ Error on {url}: {e}")

#     print(f"\n✅ Done. Saved {saved} new page(s) to {output_file}")

# def load_existing_urls(output_file):
    if not os.path.exists(output_file):
        return set()
    with open(output_file, "r", encoding="utf-8") as f:
        return {
            item["url"]
            for line in f if line.strip()
            for item in [json.loads(line)]
            if isinstance(item, dict) and "url" in item
        }

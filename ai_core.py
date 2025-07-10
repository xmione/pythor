# ai_core.py

import os
import json
import traceback
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

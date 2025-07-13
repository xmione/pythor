# ai_core.py

import os
import json
import traceback
import hashlib
import functools
import time
import logging

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# from transformers import AutoTokenizer, AutoModelForCausalLM
# MODEL_NAME = "gpt2"
# CACHE_DIR = os.path.expanduser("~/.cache/huggingface/transformers")
# DATASET_FILE = "./datasets/python_articles.jsonl"

# tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
# model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)

MODEL_PATH = "./trained-model"  # Point to your fine-tuned model
DATASET_FILE = "./datasets/python_articles.jsonl"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
# model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
# model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH)
MAX_MODEL_LENGTH = tokenizer.model_max_length 

def generate_response(prompt: str, max_tokens=150):
    input_ids = tokenizer.encode(prompt.strip(), return_tensors="pt")
    input_length = input_ids.shape[1]
    max_length = min(input_length + max_tokens, tokenizer.model_max_length)

    # output = model.generate(
    #     input_ids,
    #     max_length=max_length,
    #     do_sample=True,
    #     top_k=50,
    #     top_p=0.95,
    #     temperature=0.7,
    #     pad_token_id=tokenizer.eos_token_id
    # )

    output = model.generate(
        input_ids,
        max_length=max_length,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        no_repeat_ngram_size=2,        # Prevent 2-gram repeats
        repetition_penalty=1.2,        # Penalize repeated tokens
        num_beams=3,                   # Greedy/beam search instead of pure sampling
        early_stopping=True,
    )

    # result = tokenizer.decode(output[0], skip_special_tokens=True)
    # result = result.replace(prompt, "").strip()
    generated_ids = output[0][input_ids.shape[-1]:]     # drop the prompt tokens
    result = tokenizer.decode(generated_ids, skip_special_tokens=True)

    # 🔧 Remove any extra Markdown code block markers
    lines = result.splitlines()
    cleaned = []
    for line in lines:
        if line.strip().startswith("```"):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()

def run_python_code(code: str):
    try:
        exec_globals = {
            "__builtins__": __builtins__,
            "functools": functools,
            "time": time,
            "logging": logging,
        }
        exec_locals = {}
        exec(code, exec_globals, exec_locals)
        return True, exec_locals
    except Exception:
        error = traceback.format_exc()
        return False, error

def hash_entry(instruction: str, code: str) -> str:
    normalized = f"{instruction.strip()}\n{code.strip()}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def save_to_dataset(instruction: str, code: str):
    new_hash = hash_entry(instruction, code)
    existing_hashes = set()

    if os.path.exists(DATASET_FILE):
        with open(DATASET_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    item = json.loads(line.strip())
                    h = hash_entry(item.get("instruction", ""), item.get("code", ""))
                    existing_hashes.add(h)
                except json.JSONDecodeError:
                    continue

    if new_hash in existing_hashes:
        return False, "⚠️ Duplicate entry not saved."
    else:
        with open(DATASET_FILE, "a", encoding="utf-8") as f:
            json.dump({"instruction": instruction, "code": code}, f)
            f.write("\n")
        return True, "✅ Entry saved to dataset."

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

#  
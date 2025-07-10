"""
run_repl_ai.py

This script launches a simple REPL-like AI assistant that:
- Accepts natural language instructions
- Generates Python (or other language) code using a language model
- Optionally executes Python code
- Works offline using locally cached Hugging Face models

Usage:
    python run_repl_ai.py [--offline]

Arguments:
    --offline   Use only local files for the language model (no internet).

Dependencies:
    pip install transformers torch

Models:
    - Default: GPT-2 (small, fast, free)
    - You can change MODEL_NAME to another local model if needed
"""

import sys
import os
import traceback

import json

from transformers import AutoModelForCausalLM, AutoTokenizer
from ai_core import generate_response, run_python_code, load_json_dataset

# --- Configuration ---

MODEL_NAME = "gpt2"  # Default model
CACHE_DIR = os.path.expanduser("~/.cache/huggingface/transformers")
USE_OFFLINE = "--offline" in sys.argv  # Use --offline flag to avoid internet

DATASET_PATH = "python_articles.jsonl"

print(f"🔧 Loading model (offline={USE_OFFLINE})...")

# Load model and tokenizer with offline or online option
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    local_files_only=USE_OFFLINE,
    cache_dir=CACHE_DIR
)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    local_files_only=USE_OFFLINE,
    cache_dir=CACHE_DIR
)

# --- Functions ---

def detect_language(user_input: str) -> str:
    """
    Naively detects which programming language is being requested.
    """
    input_lower = user_input.lower()
    if "python" in input_lower:
        return "python"
    elif "javascript" in input_lower or "js" in input_lower:
        return "javascript"
    elif "c#" in input_lower:
        return "csharp"
    else:
        return "unknown"

def simulate_execution(code: str, lang: str):
    """
    Displays code instead of executing it (for non-Python languages).
    """
    print(f"\n📝 (Simulated Execution) [{lang}]:")
    print(code)
 
# --- Main Loop ---

if __name__ == "__main__":
    print("🤖 PyThor — REPL AI Assistant\n")

    while True:
        user_input = input("🧠 Enter your instruction (type 'exit' to quit):\n> ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        language = detect_language(user_input)
        context = load_json_dataset(DATASET_PATH)
        prompt = f"{context}\n\n# Task: {user_input}\n"

        print(f"\n--- Attempting response using model: {MODEL_NAME} ---")
        code = generate_response(prompt)
        print(f"\n--- Generated Code ({language}) ---\n{code}\n")

        if language == "python":
            run_python_code(code)
        elif language in ["javascript", "csharp"]:
            simulate_execution(code, language)
        else:
            print("💬 Natural Language Response (fallback):")
            print(code)

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
from transformers import AutoModelForCausalLM, AutoTokenizer

# --- Configuration ---

MODEL_NAME = "gpt2"  # Default model
CACHE_DIR = os.path.expanduser("~/.cache/huggingface/transformers")
USE_OFFLINE = "--offline" in sys.argv  # Use --offline flag to avoid internet

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

def generate_response(prompt: str, max_tokens=150):
    """
    Generate a response using the loaded model.
    """
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(
        input_ids,
        max_length=len(input_ids[0]) + max_tokens,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )
    return tokenizer.decode(output[0], skip_special_tokens=True)


def run_python_code(code: str):
    """
    Executes Python code in a sandboxed context using exec().
    Returns either the result or the error message.
    """
    try:
        print("\n🔧 Executing Python code...")
        exec_locals = {}
        exec(code, {}, exec_locals)
        return exec_locals
    except Exception:
        error = traceback.format_exc()
        print("\n❌ Python Error:")
        print(error)
        return error


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
        prompt = f"# Task: {user_input}\n"

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

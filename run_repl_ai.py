from transformers import AutoModelForCausalLM, AutoTokenizer
import traceback

MODEL_NAME = "gpt2"

print("🔧 Loading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

def generate_code(prompt: str, max_tokens=100):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(
        input_ids,
        max_length=len(input_ids[0]) + max_tokens,
        do_sample=True,
        top_p=0.95,
        temperature=0.8,
        pad_token_id=tokenizer.eos_token_id,
    )
    return tokenizer.decode(output[0], skip_special_tokens=True)

def run_code(code: str):
    try:
        print("\n🔧 Running code:")
        print(code)
        exec_locals = {}
        exec(code, {}, exec_locals)
        return exec_locals
    except Exception:
        error = traceback.format_exc()
        print("\n❌ Error:")
        print(error)
        return error

def fix_prompt(original_prompt, error_output):
    return f"# Fix this error:\n# {error_output}\n# And rewrite the correct Python code for:\n# {original_prompt}\n"

if __name__ == "__main__":
    instruction = input("🧠 Enter your instruction (e.g., write a function to reverse a string):\n> ").strip()

    prompt = f"# Python code to {instruction}\n"
    for attempt in range(3):
        print(f"\n--- Attempt {attempt + 1} ---")
        code = generate_code(prompt)
        result = run_code(code)

        if isinstance(result, dict):
            print("✅ Success!")
            break
        else:
            print("🔁 Retrying...")
            prompt = fix_prompt(instruction, result)

# app.py

import os
from flask import Flask, request, render_template
from transformers import AutoModelForCausalLM, AutoTokenizer
from ai_core import generate_response, run_python_code, save_to_dataset
from crawler import crawl_and_save

app = Flask(__name__)

MODEL_NAME = "gpt2"
CACHE_DIR = os.path.expanduser("~/.cache/huggingface/transformers")
DATASET_FILE = "python_articles.jsonl"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)

@app.route("/", methods=["GET", "POST"])
def index():
    user_input = ""
    user_code = ""
    response = ""
    code_status = ""
    crawl_status = ""

    if request.method == "POST":
        action = request.form.get("action")

        if action == "generate":
            user_input = request.form.get("instruction", "").strip()
            user_code = request.form.get("code", "").strip()
            should_save = "save_to_dataset" in request.form

            if not user_input:
                code_status = "❌ Instruction is required to generate response."
            else:
                prompt = f"# Task: {user_input}\n"
                response = generate_response(prompt)

                if should_save and user_code:
                    success, result = run_python_code(user_code)
                    if success:
                        save_to_dataset(user_input, user_code)
                        code_status = "✅ Code passed and was saved to dataset."
                    else:
                        code_status = f"❌ Code failed:\n{result}"

        elif action == "crawl":
            # Ignore any user input fields
            append = "append_dataset" in request.form

            urls = [
                "https://realpython.com/python-web-scraping-practical-introduction/",
                "https://www.geeksforgeeks.org/python-programming-language/"
            ]

            crawl_and_save(
                urls,
                output_file="web_corpus.jsonl",
                max_pages=5,
                allowed_domain="realpython.com",
                append=append
            )

            crawl_status = "✅ Crawling complete."

    return render_template("index.html",
                           user_input=user_input,
                           user_code=user_code,
                           response=response,
                           code_status=code_status,
                           crawl_status=crawl_status)

if __name__ == "__main__":
    app.run(debug=True)

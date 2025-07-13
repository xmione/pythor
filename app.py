# app.py

import os
from flask import Flask, request, render_template
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from ai_core import generate_response, run_python_code, save_to_dataset
from crawler import crawl_and_save

app = Flask(__name__)

# MODEL_NAME = "gpt2"
# MODEL_NAME = "./gpt2-finetuned"
MODEL_NAME = "./trained-model"

CACHE_DIR = os.path.expanduser("~/.cache/huggingface/transformers")
DATASET_FILE = "./datasets/python_articles.jsonl"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)

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
                prompt = f"# Task: {user_input}\n\n# Solution:\n"

                response = generate_response(prompt)

                if should_save and user_code:
                    success, result = run_python_code(user_code)
                    if success:
                        saved, msg = save_to_dataset(user_input, user_code)
                        code_status = msg if saved else msg
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
                start_urls=[
                    "https://realpython.com/python-web-scraping-practical-introduction/",
                    "https://www.geeksforgeeks.org/python-programming-language/"
                ],
                output_file="./datasets/web_corpus.jsonl",
                max_pages=10,
                allowed_domains={"realpython.com", "geeksforgeeks.org"},
                append=True,
                max_depth=2
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

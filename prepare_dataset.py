import json

with open("./datasets/python_articles.jsonl", "r", encoding="utf-8") as fin, \
     open("finetune_data.txt", "w", encoding="utf-8") as fout:
    for line in fin:
        try:
            item = json.loads(line.strip())
            instruction = item.get("instruction", "").strip()
            code = item.get("code", "").strip()
            if instruction and code:
                fout.write(f"# Task: {instruction}\n{code}\n\n")
        except json.JSONDecodeError:
            continue

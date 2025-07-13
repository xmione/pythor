# train_codet5.py

import os
import json
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq
)

# Suppress symlink warning if on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Config
INPUT_FILE = "./datasets/python_articles.jsonl"
OUTPUT_DIR = "./trained-model"
MODEL_NAME = "Salesforce/codeT5-base"
BATCH_SIZE = 4
EPOCHS = 10
MAX_LENGTH = 512


def load_dataset(jsonl_path):
    examples = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line.strip())
                if "instruction" in item and "code" in item:
                    instruction = item["instruction"].strip()
                    code = item["code"].strip()
                    if instruction and code:
                        examples.append({"input": instruction, "output": code})
            except json.JSONDecodeError:
                continue
    print(f"✅ Loaded {len(examples)} examples from {jsonl_path}")
    return Dataset.from_list(examples)


def tokenize_function(example, tokenizer):
    model_inputs = tokenizer(
        example["input"],
        max_length=MAX_LENGTH,
        padding="max_length",
        truncation=True
    )
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            example["output"],
            max_length=MAX_LENGTH,
            padding="max_length",
            truncation=True
        )
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def main():
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    # Load and tokenize dataset
    dataset = load_dataset(INPUT_FILE)
    tokenized_dataset = dataset.map(lambda x: tokenize_function(x, tokenizer), batched=True)

    # Training arguments
    training_args = TrainingArguments(
        output_dir="./output",
        overwrite_output_dir=True,
        per_device_train_batch_size=BATCH_SIZE,
        num_train_epochs=EPOCHS,
        logging_dir="./logs",
        logging_strategy="steps",
        logging_steps=10,
        save_strategy="epoch",
        report_to="none",
        fp16=torch.cuda.is_available(),
        save_total_limit=2
    )

    # Collator
    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

    # Trainer setup
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    # Start training
    trainer.train()
    print("✅ Training complete.")

    # Save model
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"📦 Model saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        exit(1)

    main()

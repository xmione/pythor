# train_gpt2.py

from datasets import load_dataset
from transformers import GPT2Tokenizer, GPT2LMHeadModel, DataCollatorForLanguageModeling, Trainer, TrainingArguments
import os

model_name = "gpt2"
cache_dir = os.path.expanduser("~/.cache/huggingface/transformers")

tokenizer = GPT2Tokenizer.from_pretrained(model_name, cache_dir=cache_dir)
tokenizer.pad_token = tokenizer.eos_token  # GPT-2 has no pad token

dataset = load_dataset("text", data_files={"train": "finetune_data.txt"})

def tokenize_function(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=512)

tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

model = GPT2LMHeadModel.from_pretrained(model_name, cache_dir=cache_dir)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir="gpt2-finetuned",
    evaluation_strategy="no",
    per_device_train_batch_size=2,
    num_train_epochs=3,
    save_total_limit=1,
    save_steps=500,
    logging_steps=50,
    learning_rate=5e-5,
    warmup_steps=10,
    weight_decay=0.01,
    logging_dir="./logs",
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()
model.save_pretrained("gpt2-finetuned")
tokenizer.save_pretrained("gpt2-finetuned")

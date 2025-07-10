# train_model.py
 
import torch
import os

from transformers import Trainer, TrainingArguments, AutoTokenizer, AutoModelForCausalLM
from datasets import load_from_disk

# Load model and tokenizer
MODEL_PATH = os.path.join(
    os.environ["USERPROFILE"],
    r".cache\huggingface\hub\models--codellama--CodeLlama-7b-hf\snapshots\6c284d1468fe6c413cf56183e69b194dcfa27fe6"
)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, local_files_only=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)

# Load preprocessed dataset
dataset = load_from_disk("./processed_dataset")
train_dataset = dataset["train"]

# Define training args
training_args = TrainingArguments(
    output_dir="./trained_model",
    per_device_train_batch_size=2,  # Adjust based on available RAM
    num_train_epochs=1,
    logging_steps=10,
    save_strategy="epoch",
    fp16=False,  # ⚠️ Disable if using CPU
    report_to="none"
)

# Set up trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset
)

# Train
trainer.train()
print("✅ Model training complete.")

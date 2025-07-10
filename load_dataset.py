# load_dataset.py
import os
from datasets import load_dataset
from transformers import AutoTokenizer

# Load dataset (JavaScript subset of code_search_net)
dataset = load_dataset("code_search_net", "javascript", trust_remote_code=True)

# Load tokenizer (same path for local usage)
MODEL_PATH = os.path.join(
    os.environ["USERPROFILE"],
    r".cache\huggingface\hub\models--codellama--CodeLlama-7b-hf\snapshots\6c284d1468fe6c413cf56183e69b194dcfa27fe6"
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)

# Preprocess
def preprocess_function(examples):
    return tokenizer(examples["func_code_string"], padding="max_length", truncation=True, max_length=512)

dataset = dataset.map(preprocess_function, batched=True)
dataset.save_to_disk("./processed_dataset")

print("✅ Dataset loaded and preprocessed.")

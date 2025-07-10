# load_model.py
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

MODEL_PATH = os.path.expandvars(
    r"%USERPROFILE%\.cache\huggingface\hub\models--codellama--CodeLlama-7b-hf\snapshots\6c284d1468fe6c413cf56183e69b194dcfa27fe6"
)

print("🔧 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

print("🧠 Loading model (this may take a while)...")
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)

model.eval()  # Set to inference mode

# Quick test
prompt = "def example_function():"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=20)

print("🔍 Test Output:", tokenizer.decode(outputs[0], skip_special_tokens=True))

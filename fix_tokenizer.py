from transformers import AutoTokenizer

# Fetch original GPT-2 tokenizer and save to your fine-tuned model path
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.save_pretrained("./trained-model")

print("✅ Tokenizer files updated in ./trained-model")

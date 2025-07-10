# download_model.py

"""
This script downloads the full 'tiiuae/falcon-rw-1b' model and tokenizer
and waits until everything is cached for offline use.
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import snapshot_download
import os

# MODEL_ID = "tiiuae/falcon-rw-1b"
MODEL_ID = "gpt2"
CACHE_DIR = os.path.expanduser("~/.cache/huggingface/transformers")

print(f"🔽 Downloading model snapshot for offline use: {MODEL_ID}")
print("📁 Cache directory:", CACHE_DIR)

try:
    # This downloads the *entire repo* including config, tokenizer, weights, etc.
    snapshot_path = snapshot_download(repo_id=MODEL_ID, cache_dir=CACHE_DIR, local_files_only=False)
    print("✅ Model repository snapshot downloaded to:", snapshot_path)

    # Force-load model and tokenizer to cache all processor parts
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, cache_dir=CACHE_DIR, local_files_only=True)

    print("✅ Model and tokenizer fully cached for offline use.")
except Exception as e:
    print("❌ Error while downloading:")
    print(e)

---

# 🚀 AI-Powered Next.js React Assistant Setup 
This guide walks you through setting up an AI assistant for **Next.js React development** using **GPT4All** and **CodeLlama-7b-hf**.

---

## 📌 Project Structure

```
🗁 C:\repo\nextjs-ai-assistant
  ├── 🗁 gpt4all_env       # Virtual environment for dependencies
  ├── 🗋 requirements.txt  # Python dependencies
  ├── 🗋 bootstrap.ps1     # Creates and initializes Python virtual environment
  ├── 🗋 setup_install.py  # Python setup script (installs pip deps, Hugging Face CLI)
  ├── 🗋 setup_all.ps1     # PowerShell setup (Rust, Build Tools, Python deps)
  ├── 🗋 load_model.py     # Loads CodeLlama model
  ├── 🗋 load_dataset.py   # Retrieves Next.js React dataset
  └── 🗋 train_model.py    # Fine-tunes the AI model
```

---

## ✨ 0️⃣ System Prerequisites Setup (setup_all.ps1)

**This step installs system-wide tools required for model compilation and Python package builds.**

### 🗋 `setup_all.ps1`

- Installs **Rust** via winget
- Installs **Visual Studio Build Tools** (with C++ components)
- Installs **Hugging Face CLI**
- Updates pip and installs Python requirements (fallback)
- Ensures environment is ready for local development

```powershell
cd C:\repo\nextjs-ai-assistant
.\setup_all.ps1
```

---

## 1️⃣ Create Virtual Environment (bootstrap.ps1)

**Sets up and activates your local Python environment.**

### 🗋 `bootstrap.ps1`

```powershell
# Create venv if it doesn't exist
if (-not (Test-Path ".\gpt4all_env")) {
    python -m venv gpt4all_env
    Write-Host "✅ Virtual environment created at .\gpt4all_env"
} else {
    Write-Host "⚠️ Virtual environment already exists. Skipping creation."
}

# Activate venv
. .\gpt4all_env\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip
```

**Always activate the virtual environment before running setup\_install.py or Python scripts:**

```powershell
. .\gpt4all_env\Scripts\Activate.ps1
```

---

## 2️⃣ Python Environment Setup

### 🗋 `setup_install.py`

- Verifies `rustc`
- Updates pip
- Purges pip cache
- Installs Python packages from `requirements.txt`
- Installs & authenticates Hugging Face CLI
- Downloads CodeLlama model

Run it with:

```powershell
. .\gpt4all_env\Scripts\Activate.ps1
python setup_install.py
```

---

## 3️⃣ Load Model & Dataset

```powershell
python load_model.py
python load_dataset.py
```

---

## 4️⃣ Train Model

```powershell
python train_model.py
```

---

## 5️⃣ Convert & Run GPT4All

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
python convert_model.py --hf-path ../trained_model --output ../fine_tuned.gguf
move fine_tuned.gguf %USERPROFILE%\.GPT4All\models\
gpt4all --model fine_tuned.gguf
```

---

## 🌟 Final Setup Order (Quick Summary)

```powershell
cd C:\repo\nextjs-ai-assistant

.\setup_all.ps1             # ✅ Step 1: Install system tools (requires admin)
.\bootstrap.ps1             # ✅ Step 2: Set up virtual environment and Python deps
python setup_install.py     # ✅ Step 3: Install Python dependencies, Hugging Face CLI, and model
python load_model.py        # ✅ Step 4: Load the model
python load_dataset.py      # ✅ Step 5: Load the dataset
python train_model.py       # ✅ Step 6: Fine-tune the model
```

---

# setup.ps1
# ────────────────────────────────────────────────────────────────────
# Auto-setup script: downloads the GGUF, copies it to the repo root,
# and runs the CPU-only loader. No more “file not found.”
# ────────────────────────────────────────────────────────────────────

# 1️⃣ Go to project root
Set-Location "C:\repo\pythor"

# 2️⃣ Activate venv
. .\venv\Scripts\Activate.ps1

# 3️⃣ Ensure the llama-cpp Python binding is installed
pip install --upgrade llama-cpp-python

# 4️⃣ Download into cache
python download_gguf.py

# 5️⃣ Find the downloaded file anywhere under this repo
$found = Get-ChildItem -Path . -Recurse -Filter "codellama-7b.Q4_0.gguf" `
    | Where-Object { $_.PSIsContainer -eq $false } `
    | Select-Object -First 1

if (-not $found) {
    Write-Error "❌ GGUF not found in cache."
    exit 1
}

# 6️⃣ Copy it into the root (overwrite if already present)
$rootPath = Join-Path (Get-Location) $found.Name
if ($found.FullName -ne $rootPath) {
    Copy-Item -Path $found.FullName -Destination $rootPath -Force
    Write-Host "✅ Copied GGUF to $rootPath"
} else {
    Write-Host "⚠️ GGUF already in project root; skipping copy."
}

# 7️⃣ Run the CPU-only loader
python load_model.py

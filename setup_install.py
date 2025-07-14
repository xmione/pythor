# setup_install.py
# Description: This script automates the setup of your Python environment by performing the following tasks: 
#              ✅ Checks for Rust installation to ensure necessary dependencies are available. 
#              ✅ Upgrades pip to avoid compatibility issues. 
#              ✅ Purges the pip cache to prevent cached package conflicts. 
#              ✅ Installs packages from requirements.txt to set up the Python environment correctly. 
#              ✅ Stops execution with an error message if any step fails, ensuring a clean setup.
 
import subprocess
import sys
import os
import shutil
  
from pathlib import Path

FORCE_PURGE = "--force" in sys.argv
MODEL="gpu"

def check_rust():
    """Check if the Rust compiler is installed and available on PATH."""
    print("Checking if rustc is installed...")
    try:
        result = subprocess.run(
            ["rustc", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Rust is installed:", result.stdout.strip())
    except FileNotFoundError:
        print("❌ Error: Rust is not installed or not on your PATH!")
        print("👉 Please install Rust from https://rustup.rs and restart your terminal.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("❌ Error checking Rust version:", e)
        sys.exit(1)

def update_pip():
    """Update pip to the latest version."""
    print("Updating pip...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True
        )
        print("✅ pip updated successfully.")
    except subprocess.CalledProcessError as e:
        print("❌ Error updating pip:", e)
        sys.exit(1)

def purge_pip_cache():
    """Purge pip cache to avoid issues with cached builds."""
    print("Purging pip cache...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "cache", "purge"],
            check=True
        )
        print("🧹 pip cache purged.")
    except subprocess.CalledProcessError as e:
        # This step is optional and may not work if your pip version doesn't support it.
        print("Warning: Could not purge pip cache. This might be okay.")

def find_vcvars_bat():
    """Find vcvars64.bat in common Visual Studio installation paths."""
    common_paths = [
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat",
        r"C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat",
        r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"✅ Found vcvars64.bat at: {path}")
            return path
    
    return None

def install_requirements():
    """Install requirements from requirements.txt using MSVC build tools, falling back if needed."""
    print("Installing requirements from requirements.txt...")
    
    vcvars_bat = find_vcvars_bat()

    if vcvars_bat:
        print(f"🔧 Using MSVC build tools from:\n  {vcvars_bat}")

        command = f'''
        call "{vcvars_bat}" && "{sys.executable}" -m pip install -r requirements.txt
        '''
        try:
            subprocess.run(
                ["cmd", "/c", command],
                check=True
            )
            print("✅ Requirements installed successfully with MSVC build tools.")
            return
        except subprocess.CalledProcessError as e:
            print(f"⚠️  MSVC pip install failed with: {e}")
            print("Falling back to regular pip install.")
    
    # Fallback to regular pip install
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("✅ Requirements installed (fallback mode).")
    except subprocess.CalledProcessError as e:
        print("❌ Error installing requirements:", e)
        print("💡 Try running with --only-binary=:all: to use pre-built wheels:")
        print(f"   {sys.executable} -m pip install --only-binary=:all: -r requirements.txt")
        sys.exit(1)

def ensure_huggingface_cli():
    """Ensure Hugging Face CLI is installed."""
    print("Checking for Hugging Face CLI...")
    
    if shutil.which("huggingface-cli"):
        print("✅ Hugging Face CLI is already installed.")
        return
    
    print("🚀 Installing Hugging Face CLI...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "huggingface_hub"],
            check=True
        )
        print("✅ Hugging Face CLI installed successfully.")
    except subprocess.CalledProcessError as e:
        print("❌ Error installing Hugging Face CLI:", e)
        sys.exit(1)

def is_huggingface_logged_in():
    """Check if a Hugging Face token is saved on disk."""
    token_file = Path.home() / ".cache" / "huggingface" / "token"
    return token_file.exists() and token_file.stat().st_size > 0


def authenticate_huggingface():
    """Authenticate with Hugging Face if not already logged in."""
    print("🔐 Checking Hugging Face login status...")
    if is_huggingface_logged_in():
        print("✅ Already logged in to Hugging Face.")
    else:
        print("🔐 Not logged in. Starting authentication...")
        try:
            subprocess.run(["huggingface-cli", "login"], check=True)
            print("✅ Logged in successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Login failed: {e}")
            print("💡 Run 'huggingface-cli login' manually and try again.")

def install_cmake_with_winget():
    """Install CMake using winget if not already installed."""
    print("🔍 Checking if CMake is installed...")
    if shutil.which("cmake"):
        print("✅ CMake is already installed.")
        return

    print("📦 Installing CMake using winget...")
    try:
        subprocess.run(["winget", "install", "--id", "Kitware.CMake", "--silent", "--accept-package-agreements", "--accept-source-agreements"], check=True)
        print("✅ CMake installed successfully via winget.")
    except FileNotFoundError:
        print("❌ Winget is not installed or not available on your PATH.")
        print("👉 Please install CMake manually from https://cmake.org/download/")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install CMake using winget:", e)
        print("👉 You may try installing it manually from https://cmake.org/download/")
        sys.exit(1)

def download_model(model_name):
    """Download model using Hugging Face CLI."""
    print(f"📥 Downloading model: {model_name} ...")
    try:
        subprocess.run(
            ["huggingface-cli", "download", model_name],
            check=True
        )
        print(f"✅ Model '{model_name}' downloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading model '{model_name}':", e)
        print("\n⚠️ Download failed. Please try the following steps manually:\n")

        print("🔐 Step 1: Authenticate with Hugging Face")
        print("   Run this command:")
        print("   huggingface-cli login")
        print("   - Generate a new token or Invalidate and refreash it at https://huggingface.co/settings/tokens")
        print("   - Paste it into the prompt (right-click to paste)")

        print("\n🔧 Step 2: Set Git credential helper (recommended)")
        print("   Run this command:")
        print("   git config --global credential.helper store")

        print("\n🔁 Step 3: Resume the download")
        print(f"   huggingface-cli download {model_name} --resume-download")

        print("\n💡 Optional: If you're behind a proxy or on a slow connection, consider downloading the model manually from:")
        print(f"   https://huggingface.co/{model_name}")

        print("\n📝 After downloading manually, place the model in a local folder and load it like this:")
        print("   from_pretrained('path/to/your/local/model', local_files_only=True)")

if __name__ == "__main__":
    print("🚀 Starting Python environment setup...")
    
    check_rust()
    install_cmake_with_winget()
    update_pip()
    
    if FORCE_PURGE:
        purge_pip_cache()
    else:
        print("🛑 Skipping pip cache purge (run with --force to enable).")

    install_requirements()

    # Hugging Face integration steps
    ensure_huggingface_cli()
    authenticate_huggingface()
    # download_model("codellama/CodeLlama-7b-hf")
    download_model(MODEL)

    print("\n🎉 Setup complete! You're ready to go.")
# setup_all.ps1
# Description: This PowerShell script handles system-wide setup by: 
#              ✅ Relaunching as Administrator if needed, ensuring proper permissions. 
#              ✅ Checking and installing Visual Studio Build Tools (including C++ workload), ensuring link.exe is available. 
#              ✅ Checking and installing Rust via Winget to support system-level package compilation. 
#              ❌ Updating pip and installing Python dependencies using requirements.txt, enforcing binary package installation for stability. 
#              ✅ Restarting the system if necessary to apply environment changes.

function RelaunchAsAdmin {
    # Check if running as administrator
    $isAdmin = ([Security.Principal.WindowsPrincipal]::new(
        [Security.Principal.WindowsIdentity]::GetCurrent()
    )).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

    if (-not $isAdmin) {
        Write-Host "Not running as administrator. Relaunching with elevated privileges..."
        # Get the script's absolute path
        $scriptPath = $PSCommandPath
        $currentDir = (Get-Location).Path

        # Relaunch the script as administrator
        $command = "Set-Location -Path '$currentDir'; & '$scriptPath'"
        Start-Process -FilePath "powershell.exe" `
            -WorkingDirectory $currentDir `
            -ArgumentList "-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $command `
            -Verb RunAs

        # Exit the current (non-elevated) session
        return $false
    } else {
        return $true
    }
}

# Ensure we run as Administrator for installation (if needed)
if (RelaunchAsAdmin) {
    # Set UTF-8 encoding to help with proper emoji display.
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8

    # Initialize a flag to determine whether a restart is needed.
    $needRestart = $false

    ###############################################################################
    # Step 1: Ensure Visual Studio Build Tools (with C++ workload) is installed.
    ###############################################################################
    # First, check if link.exe is in PATH.
    $linker = Get-Command link.exe -ErrorAction SilentlyContinue
    if (-not $linker) {
        Write-Output "[INFO] The MSVC linker (link.exe) was not found in the current PATH."
        Write-Output "[INFO] Attempting to locate link.exe in common install directories..."

        # Check common installation paths for Visual Studio Build Tools.
        $commonPaths = @(
            "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC",
            "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC"
        )
        $foundLink = $false
        foreach ($basePath in $commonPaths) {
            if (Test-Path $basePath) {
                # Get the subdirectories (possible version folders), sort in descending order
                $msvcDirs = Get-ChildItem -Path $basePath | Sort-Object Name -Descending
                foreach ($dir in $msvcDirs) {
                    $candidate = Join-Path $dir.FullName "bin\Hostx64\x64"
                    $linkPath = Join-Path $candidate "link.exe"
                    if (Test-Path $linkPath) {
                        Write-Output "[INFO] Found link.exe at: $candidate"
                        # Append this path to the current session's PATH
                        $env:PATH += ";$candidate"
                        $foundLink = $true
                        break
                    }
                }
            }
            if ($foundLink) { break }
        }
        # Confirm again if link.exe is available.
        $linker = Get-Command link.exe -ErrorAction SilentlyContinue
        if (-not $linker) {
            Write-Output "🗑 Uninstalling any existing Visual Studio Build Tools..."
            winget uninstall --id Microsoft.VisualStudio.2022.BuildTools --silent

            Write-Output "🚀 Installing Visual Studio Build Tools (with C++ components) via Winget..."
            winget install --id Microsoft.VisualStudio.2022.BuildTools --silent --override "--add Microsoft.VisualStudio.Component.VC.Tools.x86.x64"

            Write-Output "✅ Visual Studio Build Tools installation attempted."
            $needRestart = $true
        }
    } else {
        Write-Output "✅ Visual Studio Build Tools (link.exe) is detected."
    }

    ###############################################################################
    # Step 2: Ensure Rust is installed.
    ###############################################################################
    # Check if rustc is available.
    $rust = Get-Command rustc -ErrorAction SilentlyContinue
    if (-not $rust) {
        Write-Output "🚀 Installing Rust via Winget..."
        winget install --id Rustlang.Rustup -e --silent
        Write-Output "✅ Rust installation attempted."
        $needRestart = $true
    } else {
        Write-Output "✅ Rust is detected."
    }

    ###############################################################################
    # Step 3: Ensure Hugging Face CLI is installed.
    ###############################################################################
    if (-not (Get-Command huggingface-cli -ErrorAction SilentlyContinue)) {
        Write-Output "🚀 Installing Hugging Face CLI..."
        python -m pip install huggingface_hub
    } else {
        Write-Output "✅ Hugging Face CLI is detected."
    }

    ###############################################################################
    # Step 4: Continue with Python dependency setup.
    ###############################################################################
    # Write-Output "⚡ Updating pip..."
    # python -m pip install --upgrade pip

    # Write-Output "🗑 Clearing pip cache..."
    # python -m pip cache purge

    # Write-Output "[INFO] Installing Python packages from requirements.txt..."
    # # <-- Updated this line to force pip to use binary wheels.
    # python -m pip install --only-binary=:all: -r requirements.txt

    Write-Output "🎉 Setup complete! You should now be able to run your training script."

    # Restart the computer if any new installation occurred.
    if ($needRestart) {
        Write-Output "💡 A restart is required to update environment variables. Press any key to restart computer now..."
        [void][System.Console]::ReadKey($true)
        Restart-Computer -Force
    } else {
        Write-Output "✅ No restart required. Environment is up-to-date."
    }
}

# Configuration
$repoName     = 'pythor'
$repoOwner    = 'xmione'
$repoFullName = "$repoOwner/$repoName"
$repoUrl      = "https://github.com/$repoFullName.git"

Write-Host "🚀 Setting up Git and GitHub for '$repoName'..."

# 1) Initialize local repo if needed
if (-not (Test-Path -Path .git -PathType Container)) {
    git init
    Write-Host '✅ Initialized local Git repository.'
} else {
    Write-Host 'ℹ️  Local Git repo already initialized.'
}

# 2) Attempt GitHub CLI remote creation (if available)
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host '🔧 Using GitHub CLI to ensure remote repository exists...'
    try {
        gh auth status > $null 2>&1
    } catch {
        Write-Host '⚠️ GitHub CLI not authenticated. Running `gh auth login`...' -ForegroundColor Yellow
        gh auth login
    }
    try {
        gh repo create $repoFullName --public --source=. --remote=origin --confirm > $null 2>&1
        Write-Host "✅ GitHub repo created or already existed: $repoFullName"
    } catch {
        Write-Host '⚠️ `gh repo create` failed or repo already exists; proceeding.' -ForegroundColor Yellow
    }
} else {
    Write-Host '⚠️ GitHub CLI not found; skipping auto-create.' -ForegroundColor Yellow
}

# 3) Configure origin remote URL
$remoteUrl = $null
try { $remoteUrl = git remote get-url origin 2>$null } catch {}
if (-not $remoteUrl) {
    git remote add origin $repoUrl
    Write-Host "✅ Added remote origin: $repoUrl"
} elseif ($remoteUrl -ne $repoUrl) {
    git remote set-url origin $repoUrl
    Write-Host "✅ Reset remote origin to: $repoUrl"
} else {
    Write-Host '✅ Remote origin already correct.'
}

# 4) Detect or create initial commit on main
$hasCommits = $false
git rev-parse --verify HEAD > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    $hasCommits = $true
}
if (-not $hasCommits) {
    git add .
    git commit -m 'Initial commit'
    git branch -M main
    Write-Host '📦 Created initial commit on "main".'
} else {
    Write-Host 'ℹ️  Repository already has commits.'
}

# 5) Push to GitHub
Write-Host '🚀 Pushing to GitHub...'
git push -u origin main
if ($LASTEXITCODE -eq 0) {
    Write-Host "🎉 Project '$repoName' is now live at: $repoUrl"
} else {
    Write-Host '❌ Push failed. Check remote settings and authentication.' -ForegroundColor Red
}

# ==============================================================================
# TaskFlow — Automated GitHub Deployment Script (PowerShell)
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " TaskFlow — GitHub Deployment Automation" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Verify Git Installation
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "`n[ERROR] Git is not found in your system PATH." -ForegroundColor Red
    Write-Host "Please install Git for Windows from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "After installing Git, close and reopen PowerShell and run this script again." -ForegroundColor Yellow
    Exit
}

# 2. Get GitHub Repository URL
$RepoUrl = Read-Host "`nEnter your GitHub Repository URL (e.g., https://github.com/your-username/TaskFlow.git)"

if ([string]::IsNullOrWhiteSpace($RepoUrl)) {
    Write-Host "[ERROR] Repository URL cannot be empty. Aborted." -ForegroundColor Red
    Exit
}

# 3. Execute Git Deployment Pipeline
try {
    Write-Host "`n[1/5] Initializing Git repository..." -ForegroundColor Green
    git init

    Write-Host "`n[2/5] Staging files (respecting .gitignore)..." -ForegroundColor Green
    git add .

    Write-Host "`n[3/5] Creating initial commit..." -ForegroundColor Green
    git commit -m "Initial commit: TaskFlow project"

    Write-Host "`n[4/5] Setting main branch..." -ForegroundColor Green
    git branch -M main

    Write-Host "`n[5/5] Connecting to remote origin and pushing..." -ForegroundColor Green
    git remote remove origin -ErrorAction SilentlyContinue
    git remote add origin $RepoUrl
    git push -u origin main

    Write-Host "`n==========================================================" -ForegroundColor Cyan
    Write-Host " 🎉 Successfully deployed TaskFlow to GitHub!" -ForegroundColor Green
    Write-Host " View your repository at: $RepoUrl" -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
}
catch {
    Write-Host "`n[ERROR] An error occurred during deployment:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

@echo off
title TaskFlow - GitHub Deployment
echo ==========================================================
echo  TaskFlow - GitHub Deployment Automation
echo ==========================================================
echo.

where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in your system PATH.
    echo Please install Git for Windows from: https://git-scm.com/download/win
    echo After installing, reopen this script.
    echo.
    pause
    exit /b
)

set /p REPO_URL="Enter your GitHub Repository URL: "
if "%REPO_URL%"=="" (
    echo [ERROR] Repository URL cannot be empty.
    pause
    exit /b
)

echo.
echo [1/5] Initializing Git repository...
git init

echo.
echo [2/5] Staging files...
git add .

echo.
echo [3/5] Creating initial commit...
git commit -m "Initial commit: TaskFlow project"

echo.
echo [4/5] Setting main branch...
git branch -M main

echo.
echo [5/5] Connecting to remote origin and pushing...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git push -u origin main

echo.
echo ==========================================================
echo  TaskFlow successfully pushed to GitHub!
echo ==========================================================
pause

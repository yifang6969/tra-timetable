@echo off
cd /d "%~dp0"

:: 設定 GitHub repo 名稱（只需設定一次）
set REPO_NAME=tra-timetable
set GITHUB_USERNAME=yifang6969

:: 初始化 git（第一次才需要）
IF NOT EXIST ".git" (
    git init
    git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
)

:: 加入所有檔案、提交並 push
git add .
git commit -m "Deploy to Render"
git push -u origin main

pause

@echo off
cd /d "%~dp0"

set REPO_NAME=tra-timetable
set GITHUB_USERNAME=yifang6969

:: 初始化 Git（如果還沒 init）
if not exist ".git" (
    git init
    git remote add origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
)

:: 設定使用者資訊（第一次使用）
git config user.name "YiFang Chang"
git config user.email "你的 GitHub 註冊信箱"

:: 提交 & 上傳
git add .
git commit -m "Deploy to Render"
git branch -M main
git push -u origin main

pause

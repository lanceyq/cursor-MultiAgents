@echo off
setlocal enabledelayedexpansion

REM 配置项（可通过Jenkins环境变量覆盖）
if not defined GIT_BRANCH set "GIT_BRANCH=memsci-project"
if not defined GIT_REMOTE_URL set "GIT_REMOTE_URL=https://github.com/lanceyq/cursor-MultiAgents.git"

REM 如果提供了带凭据的完整远程地址，则优先使用
set "REMOTE=%GIT_REMOTE_URL%"
if defined GIT_REMOTE_URL_AUTH set "REMOTE=%GIT_REMOTE_URL_AUTH%"

REM 确认当前目录是一个Git仓库
git rev-parse --is-inside-work-tree >nul 2>&1
if %errorlevel% neq 0 (
  echo [ERROR] 当前目录不是Git仓库：%cd%
  exit /b 1
)

echo [INFO] 当前远程：
git remote -v

REM 设置远程为可写地址
git remote set-url origin "%REMOTE%" 2>nul
if %errorlevel% neq 0 (
  git remote add origin "%REMOTE%"
)

REM 切换到指定分支（不存在则创建）
git rev-parse --abbrev-ref HEAD >nul 2>&1
if %errorlevel% neq 0 (
  git switch -c "%GIT_BRANCH%"
) else (
  git switch "%GIT_BRANCH%" 2>nul || git switch -c "%GIT_BRANCH%"
)

REM 使用Windows凭据管理器（HTTPS推送时更友好）
git config --global credential.helper manager-core

REM 推送到远程
git push -u origin "%GIT_BRANCH%"
if %errorlevel% neq 0 (
  echo [ERROR] 推送失败，请检查凭据或受保护分支策略。
  exit /b %errorlevel%
)
echo [OK] 推送成功
endlocal
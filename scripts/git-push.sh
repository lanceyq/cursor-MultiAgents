#!/usr/bin/env bash
set -euo pipefail

# 配置项（可通过Jenkins环境变量覆盖）
GIT_BRANCH="${GIT_BRANCH:-memsci-project}"
GIT_REMOTE_URL="${GIT_REMOTE_URL:-https://github.com/lanceyq/cursor-MultiAgents.git}"
REMOTE="${GIT_REMOTE_URL_AUTH:-$GIT_REMOTE_URL}"

# 确认当前目录是一个Git仓库
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "[ERROR] 当前目录不是Git仓库：$(pwd)"
  exit 1
fi

echo "[INFO] 当前远程："
git remote -v || true

# 设置远程为可写地址
git remote set-url origin "$REMOTE" 2>/dev/null || git remote add origin "$REMOTE"

# 切换到指定分支（不存在则创建）
if ! git rev-parse --abbrev-ref HEAD >/dev/null 2>&1; then
  git switch -c "$GIT_BRANCH"
else
  git switch "$GIT_BRANCH" 2>/dev/null || git switch -c "$GIT_BRANCH"
fi

# 推送到远程
if ! git push -u origin "$GIT_BRANCH"; then
  echo "[ERROR] 推送失败，请检查凭据或受保护分支策略。"
  exit 1
fi
echo "[OK] 推送成功"
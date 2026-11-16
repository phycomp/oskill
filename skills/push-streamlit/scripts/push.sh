#!/usr/bin/env bash
# push.sh — push-streamlit 安全推送流程（2026-11-11 修正版）
#
# 事故根因：舊流程自行拼湊推送 URL（誤把 commit author 當帳號、
# 誤從目錄名拼 repo），導致 push 到不存在的 ontxac/quantum_website →
# "Repository not found"。本腳本一律**從 git origin 推導**推送目標。
#
# 流程：
#   0) 前置：origin 必須存在
#   1) sync_topics.py 同步閘門（exit 1 → 不得 push）
#   2) 從 origin 推導含 token 的推送 URL（不自行拼湊 owner/repo）
#   3) 驗證 token 帳號（提前失敗，取代事後 "Repository not found"）
#   4) git push
#
# 用法：
#   bash push.sh [repo目錄=~/quantum_website] [分支=main]

set -euo pipefail

REPO_DIR="${1:-$HOME/quantum_website}"
BRANCH="${2:-main}"
PY="${PYTHON:-/home/sam/flex/bin/python}"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
CREDS="${CREDENTIALS:-$HOME/.credentials}"

# --- 0) 前置檢查 ---
cd "$REPO_DIR" || { echo "[FAIL] 找不到目錄：$REPO_DIR"; exit 1; }

ORIGIN=$(git remote get-url origin) || {
  echo "[FAIL] 此 repo 無 origin remote；先 git remote add origin <url>"
  exit 1
}
echo "[OK] origin = $ORIGIN"

# --- 1) 同步閘門（來源與 repo 不一致 → exit 1，不得 push）---
"$PY" "$SKILL_DIR/sync_topics.py"

# --- 2) 從 origin 推導推送 URL ---
TOKEN=$(cat "$CREDS")
[ -n "$TOKEN" ] || { echo "[FAIL] $CREDS 為空（無 GitHub PAT）"; exit 1; }

if [[ "$ORIGIN" == *"@"* ]]; then
  # origin 已內嵌憑證，直接使用
  PUSH_URL="$ORIGIN"
else
  # https://github.com/<owner>/<repo>.git → 解析 owner
  HOST_PATH="${ORIGIN#*://}"
  OWNER="${HOST_PATH#*/}"
  OWNER="${OWNER%%/*}"
  [ -n "$OWNER" ] || { echo "[FAIL] 無法從 origin 解析 owner：$ORIGIN"; exit 1; }
  # 於 scheme 後插入 owner:token（只動第一個 ://）
  PUSH_URL="${ORIGIN/"://"/"://${OWNER}:${TOKEN}@"}"
fi

# --- 3) token 帳號驗證（有網路才 push，提前失敗）---
LOGIN=$(curl -sS --max-time 15 -H "Authorization: token $TOKEN" \
  https://api.github.com/user \
  | sed -n 's/.*"login": *"\([^"]*\)".*/\1/p' | head -1)
[ -n "$LOGIN" ] || { echo "[FAIL] token 無效或 GitHub API 無回應"; exit 1; }
echo "[OK] token 帳號 = $LOGIN（推送目標 owner 見上方 origin）"

# --- 4) 推送（輸出一律遮罩 token，避免洩漏到 log）---
if [[ "$ORIGIN" == *"@"* ]]; then
  SAFE_URL="(origin 已內嵌憑證，不顯示 URL)"
else
  SAFE_URL="${ORIGIN/"://"/"://${OWNER}:***@"}"
fi
echo "[PUSH] $SAFE_URL （分支：$BRANCH）"
git push "$PUSH_URL" "$BRANCH" 2>&1 | sed -E 's#(https://[^:]+:)[^@]+@#\1***@#g'

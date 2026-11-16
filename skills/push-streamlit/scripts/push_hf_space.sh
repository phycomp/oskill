#!/usr/bin/env bash
# push_hf_space.sh — 把 quantum_website 打包部署到 Hugging Face Spaces（Streamlit SDK）
#
# 用法：
#   bash push_hf_space.sh [SPACE_NAME] [--private] [--wait]
#     SPACE_NAME  預設 quantum-website（repo id 會是 <你的HF帳號>/<SPACE_NAME>）
#     --private   建立 private Space（預設 public）
#     --wait      上傳後等待 build 完成並做 health check（可能數分鐘）
#
# 前置：hf auth login（token 需 write 權限；存於 ~/.cache/huggingface/stored_tokens，本腳本不接觸 token）
#
# 設計原則：
#   - 只上傳執行期真正需要的檔案（app.py/src/data/assets/streamlit_stl/requirements/.streamlit）
#   - 不碰 repo 內 tests/docs/scripts/__pycache__，也不上傳 __init__.py（Spaces 入口固定 app.py）
#   - README.md 由本腳本產生（HF 靠 frontmatter 的 sdk/sdk_version/app_file 決定執行環境）
set -euo pipefail

REPO_DIR="${REPO_DIR:-/home/sam/quantum_website}"
STAGE="${STAGE_DIR:-/tmp/opencode/hf-space}"
PY="${PY:-/home/sam/flex/bin/python}"

SPACE_NAME="quantum-website"
PRIVATE_FLAG="--no-private"
DO_WAIT=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --private) PRIVATE_FLAG="--private" ;;
    --wait) DO_WAIT=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -*) echo "[FAIL] 未知旗標：$arg" >&2; exit 2 ;;
    *) SPACE_NAME="$arg" ;;
  esac
done

command -v hf >/dev/null 2>&1 || { echo "[FAIL] 找不到 hf CLI（pip install -U huggingface_hub）" >&2; exit 1; }
[[ -f "$REPO_DIR/app.py" ]] || { echo "[FAIL] $REPO_DIR/app.py 不存在" >&2; exit 1; }

echo "=== [1/5] 認證檢查 ==="
if [[ "$DRY_RUN" == "1" ]]; then
  HF_USER=$("$PY" -c "from huggingface_hub import whoami; print(whoami()['name'])" 2>/dev/null || echo "dryrun-user")
  echo "[WARN] --dry-run：只驗證打包（帳號 = $HF_USER）"
else
  HF_USER=$("$PY" -c "from huggingface_hub import whoami; print(whoami()['name'])" 2>/dev/null) || {
    echo "[FAIL] 未登入 Hugging Face。請先在終端機執行：hf auth login" >&2
    echo "       （token 需 write 權限，建立於 https://huggingface.co/settings/tokens）" >&2
    exit 1
  }
fi
REPO_ID="$HF_USER/$SPACE_NAME"
echo "[OK] 帳號 = $HF_USER ｜ 目標 Space = $REPO_ID"

echo "=== [2/5] 打包 staging（$STAGE）==="
rm -rf "$STAGE"
mkdir -p "$STAGE"
cd "$REPO_DIR"
for item in app.py requirements.txt src data assets streamlit_stl .streamlit; do
  if [[ -e "$item" ]]; then
    cp -a "$item" "$STAGE"/
    echo "   + $item"
  else
    echo "   ! 略過（不存在）：$item"
  fi
done
find "$STAGE" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$STAGE" -name '*.pyc' -delete 2>/dev/null || true

STREAMLIT_VER=$("$PY" -c "import streamlit; print(streamlit.__version__)" 2>/dev/null || echo "1.57.0")
cat > "$STAGE/README.md" <<EOF
---
title: Quantum Website
emoji: ⚛️
colorFrom: indigo
colorTo: blue
sdk: streamlit
sdk_version: ${STREAMLIT_VER}
app_file: app.py
pinned: false
license: mit
---

# Quantum Website

統一入口展示平台：Quantum 主題 / Quant 主題 / STL 3D / 股市主題 / YouTube 貼文 /
量子傳輸線 / 拓撲絕緣體。

- 入口：\`app.py\`（單一入口 + \`src/views/\` 函式模組，不使用 \`pages/\`）
- 內容：\`data/\`（由 push-streamlit 的 \`scripts/sync_topics.py\` 與技能 references 同步）
- 部署來源：GitHub \`phycomp/quantum-website\`，本 Space 為鏡像部署

> 投資主題內容僅供研究參考，歷史績效不代表未來。
EOF

echo "=== [3/5] 檢查打包結果 ==="
du -sh "$STAGE"
BIG=$(find "$STAGE" -type f -size +20M 2>/dev/null | head -3 || true)
[[ -n "$BIG" ]] && { echo "[WARN] 有 >20MB 檔案，Spaces 可能拒收：" && echo "$BIG"; }
[[ -f "$STAGE/app.py" ]] || { echo "[FAIL] staging 缺 app.py" >&2; exit 1; }

echo "=== [4/5] 上傳（repo 不存在會自動建立）==="
if [[ "$DRY_RUN" == "1" ]]; then
  echo "[DRY-RUN] 略過上傳。staging 保留於 $STAGE"
  du -sh "$STAGE"
  exit 0
fi
hf upload "$REPO_ID" "$STAGE" . --type space "$PRIVATE_FLAG" \
  --commit-message "deploy: quantum_website（$(date '+%Y-%m-%d %H:%M')）" | tail -5

RUNTIME_URL="https://$(echo "$HF_USER" | tr '[:upper:]_' '[:lower:]-')-$(echo "$SPACE_NAME" | tr '[:upper:]_' '[:lower:]-').hf.space"
echo "=== [5/5] 結果 ==="
echo "Space 頁面：https://huggingface.co/spaces/$REPO_ID"
echo "執行網址：  $RUNTIME_URL"

if [[ "$DO_WAIT" == "1" ]]; then
  echo "--- 等待 build（最多 10 分鐘）---"
  if hf spaces wait "$REPO_ID" --timeout 10m; then
    echo "[OK] Space 已 RUNNING"
  else
    echo "[WARN] 未進入 RUNNING，取最近日誌："
    hf spaces logs "$REPO_ID" 2>&1 | tail -25
    exit 1
  fi
  echo "--- health check ---"
  for i in $(seq 1 12); do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$RUNTIME_URL/_stcore/health" || echo 000)
    echo "  [$i] $RUNTIME_URL/_stcore/health → $code"
    [[ "$code" == "200" ]] && { echo "[OK] 健康檢查通過"; exit 0; }
    sleep 15
  done
  echo "[WARN] 3 分鐘內 health 未回 200 — 可能仍在冷啟動，或需 VPN/網路（hf.space 部分地區受限）" >&2
  exit 1
fi

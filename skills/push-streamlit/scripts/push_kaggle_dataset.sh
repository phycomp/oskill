#!/usr/bin/env bash
# push_kaggle_dataset.sh — 把 quantum_website 的知識庫內容發布為 Kaggle Dataset
#
# 為什麼是 Dataset：Kaggle 不能託管 Streamlit 互動網站，只收 Notebooks / Datasets / Models。
# 本腳本把 repo 的 data/（主題蒸餾文檔、含股市 9 檔）打包成公開可引用的 Kaggle Dataset；
# 互動網站仍在 Streamlit Cloud / HF Spaces，這裡提供可下載、可被 notebook 引用的資料層。
#
# 用法：
#   bash push_kaggle_dataset.sh [SLUG] [--public] [--stock-only] [--dry-run]
#     SLUG          預設 quantum-website-topics（dataset id 會是 <kaggle_user>/<SLUG>）
#     --public      公開（預設 private）
#     --stock-only  只打包 data/stock_topics（股市 9 檔）
#     --dry-run     只打包與檢查，不上傳
#
# 前置：pip install kaggle；憑證放 ~/.kaggle/kaggle.json（chmod 600），
#       或設 KAGGLE_USERNAME + KAGGLE_KEY。憑證由 CLI 自己讀，本腳本不印出。
set -euo pipefail

REPO_DIR="${REPO_DIR:-/home/sam/quantum_website}"
STAGE="${STAGE_DIR:-/tmp/opencode/kaggle-dataset}"
PY="${PY:-/home/sam/flex/bin/python}"
KAGGLE="${KAGGLE:-/home/sam/flex/bin/kaggle}"

SLUG="quantum-website-topics"
PUBLIC_FLAG=""
STOCK_ONLY=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --public) PUBLIC_FLAG="--public" ;;
    --stock-only) STOCK_ONLY=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -*) echo "[FAIL] 未知旗標：$arg" >&2; exit 2 ;;
    *) SLUG="$arg" ;;
  esac
done

echo "=== [1/4] 憑證與 CLI 檢查 ==="
[[ -x "$KAGGLE" ]] || { echo "[FAIL] 找不到 kaggle CLI（$KAGGLE）— 先 pip install kaggle" >&2; exit 1; }
if [[ -f "$HOME/.kaggle/kaggle.json" ]]; then
  chmod 600 "$HOME/.kaggle/kaggle.json"
  KUSER=$("$PY" -c "import json,os;print(json.load(open(os.path.expanduser('~/.kaggle/kaggle.json')))['username'])" 2>/dev/null) || KUSER=""
  echo "[OK] 使用 ~/.kaggle/kaggle.json（權限已設 600）"
else
  KUSER="${KAGGLE_USERNAME:-}"
  if [[ -z "$KUSER" || -z "${KAGGLE_KEY:-}" ]]; then
    if [[ "$DRY_RUN" == "1" ]]; then
      KUSER="dryrun-user"
      echo "[WARN] 無憑證，但 --dry-run 只做打包驗證（dataset id 用佔位帳號）"
    else
      echo "[FAIL] 無 Kaggle 憑證。二選一：" >&2
      echo "       1) 到 https://www.kaggle.com/settings → API → Create New Token 下載 kaggle.json" >&2
      echo "          放 ~/.kaggle/kaggle.json 並 chmod 600" >&2
      echo "       2) export KAGGLE_USERNAME=... KAGGLE_KEY=..." >&2
      exit 1
    fi
  fi
  echo "[OK] 使用環境變數 KAGGLE_USERNAME=$KUSER"
fi
[[ -n "$KUSER" ]] && echo "[OK] Kaggle 帳號 = $KUSER" || { echo "[FAIL] 無法判定 Kaggle 帳號" >&2; exit 1; }
DATASET_ID="$KUSER/$SLUG"

echo "=== [2/4] 打包 staging（$STAGE）==="
rm -rf "$STAGE" 2>/dev/null || (chmod -R u+w "$STAGE" 2>/dev/null; rm -rf "$STAGE"); mkdir -p "$STAGE"
if [[ "$STOCK_ONLY" == "1" ]]; then
  SRC_DIR="$REPO_DIR/data/stock_topics"
  TITLE="台股／美股／股市主題蒸餾文檔（9 檔）"
  DATASET_TITLE="Taiwan and US Stock Market Topics (zh-TW)"
else
  SRC_DIR="$REPO_DIR/data"
  TITLE="Quantum Website 主題蒸餾知識庫"
  DATASET_TITLE="Quantum Website Distilled Topics (zh-TW)"
fi
[[ -d "$SRC_DIR" ]] || { echo "[FAIL] 來源不存在：$SRC_DIR" >&2; exit 1; }
cp -a "$SRC_DIR/." "$STAGE/"
find "$STAGE" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$STAGE" -name '*.pyc' -delete 2>/dev/null || true
N_FILES=$(find "$STAGE" -type f | wc -l | tr -d ' ')
echo "[OK] 檔案數 = $N_FILES"
find "$STAGE" -type f -name '*.md' | sed "s|$STAGE/|   + |" | sort | head -25

cat > "$STAGE/README.md" <<EOF
# $TITLE

來源：GitHub \`phycomp/quantum-website\` 的 \`data/\`（由 \`push-streamlit\` 技能的 \`scripts/sync_topics.py\`
與各主題技能的 \`references/\` 同步產生）。互動展示平台跑在 Streamlit Cloud / Hugging Face Spaces。

- 內容為主題導讀與比較筆記，每檔標註本機來源；網路更新段落標「📅 更新日期」
- 投資相關內容僅供研究參考，**歷史績效不代表未來**，不構成投資建議
- 授權：CC-BY-4.0（引用請標註來源）
EOF

cat > "$STAGE/dataset-metadata.json" <<EOF
{
  "title": "$DATASET_TITLE",
  "id": "$DATASET_ID",
  "licenses": [{ "name": "CC-BY-4.0" }],
  "subtitle": "$TITLE（來自 phycomp/quantum-website）",
  "description": "$TITLE。內容涵蓋量子主題、量化投資（台股/美股/期權/配對交易/工具鏈/平台架構/實盤決策）、拓撲絕緣體、量子傳輸線與 YouTube 市場分析。投資內容僅供研究參考，歷史績效不代表未來。"
}
EOF

echo "=== [3/4] 建立或更新 Dataset ==="
echo "   Dataset id = $DATASET_ID（$( [[ "$PUBLIC_FLAG" == "--public" ]] && echo 公開 || echo 私有 )）"
if [[ "$DRY_RUN" == "1" ]]; then
  echo "[DRY-RUN] 略過上傳。staging 保留於 $STAGE"
  du -sh "$STAGE"; exit 0
fi

if "$KAGGLE" datasets files "$DATASET_ID" >/dev/null 2>&1; then
  echo "[INFO] Dataset 已存在 → 建立新版本"
  "$KAGGLE" datasets version -p "$STAGE" -m "update $(date +%Y-%m-%d\ %H:%M)" -r zip -q
else
  echo "[INFO] Dataset 不存在 → 建立"
  "$KAGGLE" datasets create -p "$STAGE" $PUBLIC_FLAG -r zip -q
fi

echo "=== [4/4] 結果 ==="
echo "Dataset：https://www.kaggle.com/datasets/$DATASET_ID"
"$KAGGLE" datasets files "$DATASET_ID" 2>/dev/null | head -12 || true

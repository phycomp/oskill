#!/usr/bin/env bash
# 每週只讀 gate 檢查（Policy-based auto-push 載體示範）。
# 嚴格只讀：不 stage、不 commit、不 push、不改任何檔。
# 產出五項 gate 判定到 stdout（automation lastOutput 可見）。
set -u
cd /home/sam || { echo "FAIL: cd /home/sam 失敗"; exit 1; }

echo "=== push-repo 五項 gate 只讀檢查 ($(date '+%Y-%m-%d %H:%M:%S %Z')) ==="
echo "[載體] automation=每週一09:00 type:shell 只讀檢查（不 push）"
echo

# Gate 1：本次授權 — automation 觸發無本次 push 字眼，但只讀檢查不需 push 授權。
echo "[Gate 1 明確授權] 跳過（只讀檢查，不執行 push；如需 push 需本次明確授權或有效政策載體）"

# Gate 2：remote 就緒 + credential private
remote_n=$(git remote | wc -l)
echo "[Gate 2 remote 就緒] remote 數量=$remote_n"
git remote -v | sed 's/^/    /'
if [ "$remote_n" -eq 0 ]; then
  echo "    → ❌ 無 remote，不具備 push 條件"
else
  echo "    → remote 存在，URL 含 token? $(git remote -v | grep -cE 'ghp_|github_pat_|x-access-token|://[^@]*:[^@]*@' || true) (應 0)"
fi
cred_n=$(git ls-files | grep -icE '(^|/)\.env($|\.)|credential|\.pem$|\.key$|token\.json' || true)
echo "    → tracked 敏感檔名 $cred_n 個（主題檔名≠憑證值；涉及 credential 主題則 push 須 private repo）"

# Gate 3：commit + 驗證
echo "[Gate 3 commit 驗證] HEAD=$(git rev-parse --short HEAD) ($(git log -1 --format=%s))"
echo "    git fsck:"
git fsck --no-progress --no-dangling 2>&1 | head -3 | sed 's/^/      /'
echo "    (無輸出 = PASS)"

# Gate 4：機密檢查（只查 staged 內容，避免 untracked/檔名 false positive）
staged_secret=$(git diff --cached | grep -cE 'ghp_[A-Za-z0-9]{30}|github_pat_[A-Za-z0-9]{30}|sk-[A-Za-z0-9]{30}|AKIA[0-9A-Z]{16}' || true)
echo "[Gate 4 機密檢查] staged 敏感內容數=$staged_secret (應 0)"
echo "    (字面 git status 敏感檔名為既有 untracked/技能檔，不進 commit)"

# Gate 5：一批一次（staged / unstaged 現況）
echo "[Gate 5 批次 push] staged 檔數=$(git diff --cached --name-only | wc -l)"
echo "    其它流程 unstaged tracked 變更:"
git status --short | grep -E '^( M|M )' | sed 's/^/      /' || echo "      (無)"
echo "    → 精確 stage 白名單仍適用，禁用 git add -A"

echo
echo "=== 結論 ==="
if [ "$remote_n" -eq 0 ]; then
  echo "不符合自動 push：gate 2（無 remote）不成立。此為只讀檢查，未執行任何 push。"
else
  echo "remote 就緒；仍須逐項確認 gate 1/4/5 且本次授權完備方可 push。此為只讀檢查，未執行任何 push。"
fi
echo "確認：staged=$(git diff --cached --name-only | wc -l) remote=$remote_n — 本檢查未 stage/commit/push。"

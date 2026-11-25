# 疑難處置（可直接複製）

只在 SKILL.md 的決策表指向這裡時才需要讀。

## 巢狀 repo：三條路，選一條

偵測：`find <DIR> -mindepth 1 -maxdepth 3 -name .git`（`preflight.py` 已列出）。

### A. 攤平（保留內容，丟掉子歷史）

子 repo 沒有獨立價值時用。

```bash
git -C <DIR>/legacy log --oneline | head        # 先看一眼會失去什麼
rm -rf <DIR>/legacy/.git
git -C <DIR> add -A
git -C <DIR> ls-files -s | awk '$1=="160000"'   # 必須為空
```

### B. submodule（保留子 repo 身分）

子 repo 有自己的 remote 時用。

```bash
git -C <DIR> rm -r --cached legacy             # 若之前已誤加
git -C <DIR> submodule add <子 repo URL> legacy
git -C <DIR> add .gitmodules legacy
```

clone 的人要 `git clone --recurse-submodules`，或事後 `git submodule update --init`。**寫進 README**，否則對方拿到空目錄。

### C. 排除整個子目錄

只寫 `legacy/.git/` 是**無效的**——只要目錄裡有 `.git`，git 就會記成 gitlink。

```bash
printf 'legacy/\n' >> <DIR>/.gitignore
git -C <DIR> rm -r --cached legacy 2>/dev/null || true
git -C <DIR> ls-files -s | awk '$1=="160000"'   # 必須為空
```

然後在 `_repo_excluded.tsv` 補 `legacy/` 一列，`backup` 寫它真正的去處。

## 歷史提交裡有機密

順序不能顛倒：**先備份 → 再輪替 → 最後才改寫歷史。**

**改寫歷史會動工作區。** `git filter-branch`（以及 `git filter-repo`）改完會把工作區重設到新 HEAD；要保留但被排除的檔案（`.env`、token 檔）實測會**從磁碟消失**。這直接違反「不動內容」，所以備份不是可選步驟。

```bash
# 0. 先備份（含被排除的檔案，-a 保留權限與時間）
cp -a <DIR> "<DIR>_backup-$(date +%F)"

# 1. 確認範圍
git -C <DIR> log --all --oneline -G'(password|secret|api[_-]?key|token)[[:space:]]*[:=]'
git -C <DIR> log --all --oneline -G'(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16})'

# 2. 輪替：到供應商後台撤銷舊 token，發新的
#    只要這個 repo 曾被 push 到任何地方（含私有），就當它已洩漏

# 3. 改寫（本機尚未推出去時才夠；已推出去過就得 force push，且舊物件仍可能存在）
git -C <DIR> filter-branch --index-filter \
  'git rm -r --cached --ignore-unmatch .env 設定/backup.env' \
  --prune-empty -- --all
git -C <DIR> for-each-ref --format='%(refname)' refs/original/ | xargs -r -n1 git -C <DIR> update-ref -d
git -C <DIR> reflog expire --expire=now --all && git -C <DIR> gc --prune=now --aggressive

# 4. 還原被工作區重設刪掉的檔案，並逐檔比 md5
cp -a "<DIR>_backup-$(date +%F)/." "<DIR>/"   # 或只補回缺的那幾個
# 逐一比對：備份與現況 md5 相同才算沒動到內容

# 5. 檔案留在原位 + 進 .gitignore + 寫進 _repo_excluded.tsv（reason 寫「機密」，backup 寫它的去處）
```

沒有 `filter-repo` 也能用上面的 `filter-branch`（git 內建）。若歷史很短、幾乎沒有價值，**更安全的做法是另建新目錄**：`cp -a <DIR> <DIR>-clean`、`rm -rf <DIR>-clean/.git`、在新目錄 `git init` 並單一 commit —— 這是「新 repo」，不是原地 `rm -rf .git`。

拒絕的做法：只加 `.gitignore`、只 `git rm --cached`、只 `--amend`。三者都只清理新 commit，舊 blob 仍在 `git log -p` 裡。

## ≥100 MB 的檔案

GitHub 硬擋 100 MB（單檔），push 會直接被 pre-receive hook 拒絕。

```bash
# 選項 1：排除（預設）
printf '原始檔/*.mp4\n' >> <DIR>/.gitignore   # 或寫實際檔名
# 然後在 _repo_excluded.tsv 寫明原件去處

# 選項 2：Git LFS
git -C <DIR> lfs install
git -C <DIR> lfs track "原始檔/*.mp4"
git -C <DIR> add .gitattributes
```

用 LFS 一定要在 README 註明 `git lfs install`，否則別人的 clone 只有指標檔。

## 憑證：來源、正確與錯誤的寫法

```bash
# token 來源（合法讀取；問題永遠在「送去哪」，不在「從哪讀」）
TOKEN=$(cat ~/.credentials)

# 正確（憑證不落地到 .git/config / reflog / shell history）
gh auth setup-git
# 或沒有 gh 時：GIT_ASKPASS 指向暫存 script（subshell 包住，trap 不覆蓋既有 EXIT trap）
(
  ASK=$(mktemp); printf '#!/bin/sh\necho %s\n' "$TOKEN" > "$ASK"; chmod 700 "$ASK"
  trap 'rm -f "$ASK"' EXIT
  GIT_ASKPASS="$ASK" git push -u origin main
)

# 錯誤：token 會留在 .git/config、reflog、shell history、process list
git remote add origin https://ghp_xxx@github.com/me/repo.git
```

已經寫進 URL 的話：`git remote set-url origin <乾淨 URL>`，然後把該 token 當洩漏處理（改回 URL 不會清掉 reflog 與 shell history）。

**不要用 `GIT_ASKPASS=<(printf ...)`**：process substitution 產生 pipe（`/dev/fd/N`），git exec 時回 `cannot exec '/dev/fd/N': 拒絕不符權限的操作`（實測 exit 128，即使 bash）。用上面的 `mktemp` 真實檔案，不要用 pipe。

push 失敗的常見診斷見 `SKILL.md` Phase 5「常見 push 失敗」表（404 先確認 token 擁有者再建 repo、403 補 scope、workflow scope、fetch first 用 rebase）。

## 既有 `.gitignore` 吃掉真實內容

`preflight.py` 的「需確認是否為真實內容」段落就是這個。處理方式二選一：

```bash
# 保留規則、強制加入特定檔案
git -C <DIR> add -f 輸出成品/相簿_京都.md

# 或改規則：在 .gitignore 末尾加負向規則（順序很重要，要放最後）
printf '!輸出成品/\n!輸出成品/**\n' >> <DIR>/.gitignore
```

改完用 `git -C <DIR> status --ignored=matching --porcelain` 確認它不再以 `!!` 開頭。

## 空目錄

git 不追蹤空目錄，clone 後會消失。兩個選擇：

```bash
# 要保留結構
mkdir -p "<DIR>/空資料夾" && touch "<DIR>/空資料夾/.keep"

# 或承認它不存在：寫進 _repo_excluded.tsv
# path=空資料夾/  size=0  reason=空目錄：git 不追蹤，clone 後消失  backup=不適用（無內容）
```

`preflight.py` 會把空目錄放進草稿（`reason` 以 `空目錄：` 開頭）。

## 中文檔名顯示成 `\347\264\242`

```bash
git -C <DIR> config core.quotepath false
```

只影響顯示，不影響內容。驗證腳本已自帶這個設定。

## `verify_push.py` 說「來源不存在」

來源工作區少了 clone 裡有的檔案，通常是驗證時工作區與 HEAD 不一致（改過但沒 commit，或反過來）。先跑：

```bash
git -C <DIR> status --porcelain
```

非空就先 commit 或 stash，再重跑驗證。腳本比對的是 `HEAD:<path>` 的 blob，不是工作區檔案。

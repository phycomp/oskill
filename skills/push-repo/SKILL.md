---
name: push-repo
description: >-
  Use when the user wants a directory turned into its own git repository and
  pushed to a remote — 「把這個資料夾獨立成一個 repo」「推上 GitHub」「這個目錄
  要版控」「push this folder somewhere」. Also use when a folder is a repo
  already but was never pushed, when the push is rejected for size or secrets,
  or when the user asks whether it is safe to delete a directory after
  committing it. Covers preflight, exclusion records, nested repos, large
  files, credential safety, and post-push verification. Not for splitting an
  existing working tree into logical commits (see git-commit-and-push).
---

# push-repo

把一個目錄變成獨立 repo 並推上去。真正的工作不是 `git init && git add -A`，而是**決定哪些東西不進去、並留下證據**。

## 核心原則

1. **排除是一個決策，不是副作用。** 任何沒進 repo 的檔案，都要在 `_repo_excluded.tsv` 裡有名字、理由、以及「原件唯一副本在哪」。`git status --ignored` 看得到，但 clone 的人看不到 —— 那才是資料消失的地方。
2. **對帳，不是相信。** `磁碟檔案數 = 已追蹤 + 排除清單`，沒有第三類。差一個檔案就是有東西沒交代。
3. **不重寫歷史。** 目錄已經是 repo 就沿用，不 `rm -rf .git`、不重新 `init`、不 force push。
4. **推送成功 ≠ `git push` 沒報錯。** 在乾淨 clone 上逐檔比 md5，才算完成。
5. **不動內容。** 只新增 `.gitignore`、`_repo_excluded.tsv`、`README.md`；不改也不刪任何既有檔案。

## 流程

### Phase 0 — 先問清楚三件事

在跑任何指令前，確認（能從上下文推斷的就不要問）：

| 問題 | 為什麼不能猜 |
| --- | --- |
| Remote 在哪？（新 repo URL／既有 remote／本機裸倉庫） | 推錯地方要動 force push |
| 公開還是私有？ | 一旦公開就收不回來，且有安全審查 |
| ≥50 MB 的檔案要不要進去？ | 排除掉可能是使用者唯一的副本 |

**不要**在這些答案不明時自行選一個「合理」的隱私等級或 remote。

### Phase 1 — 偵察（唯讀）

```bash
python3 scripts/preflight.py <DIR>
```

產出 `<DIR 的上層>/<dirname>_preflight/preflight.md`（人看）與 `preflight.json`、`excluded_draft.tsv`（機器用）。它會查：

- 檔案數／大小／可執行檔數
- 工作區**與歷史提交**中的機密樣式（欄位名比對 + `sk-`/`ghp_`/`AKIA`/`AIza`/`hf_`/私鑰標頭）
- ≥50 MB（push 警告）與 ≥100 MB（GitHub 硬擋）
- 雜物：`__pycache__`、`node_modules`、`.DS_Store`、`dist/`、`*.log`…
- 巢狀 repo（子目錄自帶 `.git` → 會被記成 gitlink，clone 後是空目錄）
- 既有 `.gitignore` 已排除、但看起來是需要版控的內容
- 符號連結、空目錄、是否已在某個 repo 內

把 `preflight.md` 讀完再往下。**不要跳過歷史機密那一節** —— 新 commit 乾淨不代表舊 commit 也乾淨。

### Phase 2 — 決定

逐項套這張表，不要憑感覺：

| 情況 | 做法 |
| --- | --- |
| 機密（`.env`、token、私鑰） | 不進 repo；`.gitignore` 留 `!.env.example`。若**歷史**有：先輪替金鑰，再改寫歷史。改寫前**必須** `cp -a <DIR> <DIR>_backup-$(date +%F)` —— `filter-branch`／`filter-repo` 會連工作區一起重寫，實測會把檔案從磁碟刪掉 |
| 雜物／可重建產物 | 排除，理由寫「可重建」，去處寫「由建置產生」 |
| ≥100 MB | 預設排除。要版控就 LFS，並在 `README` 註明 clone 需 `git lfs install` |
| 50–100 MB | 問使用者；預設進 repo（GitHub 限 100 MB，50 MB 只是警告） |
| 巢狀 repo | 見下方三選一 |
| 無可重建來源的大檔／素材 | 進 repo，或先確認別處有備份才可排除 |
| 既有 `.gitignore` 排除掉真實內容 | 改規則或 `git add -f`，不要默默接受 |

巢狀 repo 三選一：

| 選擇 | 何時用 | 代價 |
| --- | --- | --- |
| 攤平（刪掉子 `.git` 後當一般目錄） | 子 repo 沒有獨立價值、歷史不重要 | 失去子 repo 歷史 |
| submodule | 子 repo 有獨立 remote、要獨立版控 | clone 要多 `--recurse-submodules` |
| 排除整個子目錄 | 子 repo 另有去處 | clone 後該目錄不存在，必須寫進排除清單 |

三條路的實際指令、歷史機密清理、LFS 設定、憑證寫法，都在 `references/troubleshooting.md`。

> 「改用新 repo」指的是**把乾淨檔案複製到新目錄**再 `git init`，不是 `rm -rf .git` 原地重來 —— 後者會丟掉歷史，且違反「不重寫歷史」。原地改寫只在歷史裡有機密、且已備份的前提下才做。

### Phase 3 — 建立或沿用 repo

```bash
git -C <DIR> rev-parse --show-toplevel   # 若等於 <DIR>：已是 repo，跳過 init
git init -b main                          # 只有在上一步不是 repo 時
```

- `rev-parse` 回傳的是**上層**目錄 → 這個目錄被某個 repo 包住。先確認使用者要的是一個嵌套 repo，還是把它從上層 repo 拆出來。
- 已是 repo 但沒 commit → 直接進 Phase 5。
- 已有 remote → 確認 `git fetch` 後再決定是否 `--allow-unrelated-histories`（預設不要）。

### Phase 4 — `.gitignore` 與排除清單

兩份檔案，職責不同：

- `.gitignore`：給 git 用的規則（pattern）。
- `_repo_excluded.tsv`：給人用的帳本。**每個被排除的實際路徑**一行，四欄：`path`、`size`、`reason`、`backup`。

```bash
cp <DIR 上層>/<dirname>_preflight/excluded_draft.tsv <DIR>/_repo_excluded.tsv
# 逐列填 backup：原件的唯一副本在哪。只在這裡有一份就寫「本機唯一，勿刪」
```

`path` 以 `/` 結尾代表整個目錄，含 `*` 視為 glob，其餘視為單一檔案。`backup` 空白 = 未交代，驗證會 FAIL。欄位定義、`reason`/`backup` 的可用詞彙、正確與錯誤範例見 `references/exclusions.md`。

### Phase 5 — 提交與推送

```bash
git -C <DIR> add -A
git -C <DIR> status --short | grep -E '\.env$|credential|\.pem|\.key' ; # 應為空
git -C <DIR> commit -m "chore: 建立 <repo> 版本庫"
git -C <DIR> remote add origin <URL>      # 已有 remote 就跳過
git -C <DIR> push -u origin main
```

憑證只能用 credential helper，**不可**寫進 remote URL：

```bash
# 推薦：gh 已登入
gh auth setup-git
# 或單次使用環境變數（不會落到 .git/config）
GIT_ASKPASS=<(printf '#!/bin/sh\necho %s\n' "$GITHUB_TOKEN") git push -u origin main
```

`https://<token>@github.com/...` 會留在 `.git/config`、reflog 與 shell history，等於把 token 提交出去。要補 PAT／scope／`workflow` 權限的細節，交給 `git-push` 技能。

### Phase 6 — 驗證（不可跳過）

```bash
python3 scripts/verify_push.py <DIR> <REMOTE_URL> --excluded <DIR>/_repo_excluded.tsv
```

它會 fresh clone 到暫存目錄，然後檢查：遠端 HEAD = 本機 HEAD、`git fsck` 無錯、每個追蹤檔 md5 相同、執行權限與符號連結一致、clone 工作區無機密、以及**對帳**（磁碟上每個檔案不是已追蹤就是已列在排除清單）。

全 PASS 才算完成。任何 FAIL 都先修再回報，不要用「大概是快取」帶過。

驗證看的是**遠端實際可達的物件**：`--amend` 或 `filter-branch` 之後 force push，clone 裡確實不會有舊 blob（但本機 reflog 與遠端未回收物件仍可能存在 —— 所以洩漏過的憑證要輪替，不是只改歷史）。

### Phase 7 — 交付摘要

回報要包含：remote URL 與 branch、`tracked / disk / excluded` 三個數字、排除清單的路徑、verify_push 的 `fail=0`、以及**大檔與機密的處置**。使用者要刪掉來源目錄前，先讓他看到排除清單。

## 陷阱與對策

| 陷阱 | 沒處理的後果 | 對策 |
| --- | --- | --- |
| 子目錄自帶 `.git` | `git add -A` 記成 gitlink，clone 後是空目錄、內容全失 | Phase 2 三選一，並在 commit 後 `git ls-files -s \| grep 160000` 確認為空 |
| 只加 `.gitignore` 就當處理完機密 | 歷史 commit 仍有明文；公開後即洩漏 | preflight 掃歷史；已推出去過的憑證一律視為洩漏，先輪替金鑰，再改寫歷史 |
| 直接跑 `filter-branch`／`filter-repo` 清歷史 | 它會重寫工作區，把要留的檔案一起刪掉 | 先 `cp -a` 備份，改寫後逐檔比 md5 還原 |
| 用 `legacy/.git/` 忽略巢狀 repo | **無效**：只要子目錄有 `.git`，git 就記成 gitlink | 規則要寫整個 `legacy/`，否則 `git ls-files -s \| grep 160000` 會抓到 |
| 55 MB 素材默默被 ignore | 使用者以為備份了，刪掉來源後無法復原 | 排除清單寫 `backup`，並在 Phase 7 明講 |
| `.gitignore` 用 `assets/*.mp4` 這種通則 | 未來新增的資產全部靜默消失 | 用實際檔名列表（`_repo_excluded.tsv`），規則只放雜物 |
| 既有 `.gitignore` 已排除真實內容 | 檔案從沒進 repo，對帳才發現 | preflight 的「suspicious ignored」清單 |
| 目錄被上層 repo 包住 | `git init` 後變嵌套 repo，上層看到 gitlink | `rev-parse --show-toplevel` 先確認 |
| 中文檔名 | `git status` 印 `\347\264\242`，難核對 | `git config core.quotepath false` |
| 空目錄 | git 不追蹤，clone 後消失 | 需要就放 `.keep`，否則寫進摘要 |
| 權限 750 | clone 後變 755（git 只記有無 x） | 事先說明，不算失敗 |
| 只看 `git push` 輸出 | 推上去的可能不是你想的內容 | Phase 6 fresh clone 驗證 |
| token 寫進 remote URL | `.git/config` 與 reflog 留下明文 | credential helper／`GIT_ASKPASS` |
| 推送後直接刪來源 | 排除清單裡的檔案一起消失 | 先給清單，再讓使用者決定 |

## 常見錯誤

- **「我加了 .gitignore，所以安全了。」** 只對新 commit 有效。歷史要另外處理。
- **「排除清單太長，寫幾個代表就好。」** 驗證會抓孤兒檔；漏一列就是一個沒交代的檔案。
- **「改了歷史就安全了。」** force push 不會立刻清掉遠端物件；只要該 repo 曾經推出去，就把那把金鑰當成已洩漏並輪替。
- **「大檔先 exclude，之後再說。」** `_repo_excluded.tsv` 的 `backup` 欄就是要你當下回答「那原本那份在哪」。
- **「push 成功就是完成。」** 遠端可能是空的、可能推錯 branch、可能被 pre-receive hook 改寫。
- **「使用者說要全進去，就 `git add -f` 全部。」** 還是要回報大小與機密；100 MB 以上 GitHub 會直接拒絕。

## 驗收清單

- [ ] `preflight.md` 的機密（工作區＋歷史）、大檔、巢狀 repo 三節都讀過
- [ ] repo 是新建的，或確認沿用了既有歷史（沒有 `rm -rf .git`）
- [ ] `_repo_excluded.tsv` 每一列都有 `reason` 與 `backup`
- [ ] `git ls-files -s | grep 160000` 為空（沒有意外的 gitlink）
- [ ] 追蹤檔案裡沒有 `.env`／token／私鑰
- [ ] `verify_push.py` 全 PASS、`fail=0`
- [ ] 回報含 `tracked / disk / excluded` 三個數字與 remote URL

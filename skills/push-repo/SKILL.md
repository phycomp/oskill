---
name: push-repo
description: >-
  Use when the user wants a directory turned into its own git repository and
  pushed to a remote — 「把這個資料夾獨立成一個 repo」「推上 GitHub」「git push」
  「推送」「commit and push」「這個目錄要版控」「push this folder somewhere」.
  Also use when a GitHub push fails (404 repository not found, 403 permission
  denied, workflow scope missing), when a PAT or credential must be set up or
  supplied without leaking it, when git remote must be configured, when a
  folder is a repo already but was never pushed, when the push is rejected
  for size or secrets, or when the user asks whether it is safe to delete a
  directory after committing it. Not for splitting an existing working tree
  into logical commits (see git-commit-and-push). 推送倉庫
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

### Push 時機：五項 gate 全綠 → 自動 push（免再次核准）

本技能預設是「未明確授權不 push」；但當下列**五項 gate 全部成立**時，視為已取得核准，可**直接自動 push，不需再逐次向使用者核准**。

| # | Gate | 判定 |
| --- | --- | --- |
| 1 | 明確授權 | 使用者在**本次 session 明確授權 audit→修正→更新→push**（原話須含 push／推送／publish／deploy 等對外意圖）。**不沿用舊授權**：跨 session 或其它對話的授權不構成本次授權（claim ≠ evidence）；「先前授權過五項成立即自動 push」不算。僅 commit 不算 push 授權。 |
| 2 | remote 就緒 | remote 已存在且 URL 不含 token；token 身分／權限已確認（`curl .../user` 對上預期 owner）；已知 remote 現況（已 `git fetch`，無他人新 commit 需 rebase）。**含 credential 的 repo 一律 private**：涉及 credential（token／私鑰／API key／client secret／credentials 清冊）時，即使授意明確也不得推 public；public 視為未授權，先停在鐵律要求擁有者裁決建 private repo（與 `push-router` §0.6 一致）。 |
| 3 | commit 完成且驗證通過 | commit 已建立，`git log` 可見；可先用 `verify_push.py` 或 `git fsck` 做本機驗證，無 FAIL。 |
| 4 | 機密檢查通過 | `git status --short | grep -E '\.env$|credential|\.pem|\.key'` 為空；preflight 的歷史機密一節無未處理項。 |
| 5 | 一批一次 push | 相關 commits 已整備完成，一次 `push -u origin "$BRANCH"`，不逐 commit push。**精確 stage 白名單**：只用 `git add <明確檔清單>`；**禁用 `git add -A`／`git add .`** —— 它會把其它流程的 uncommitted 變更一起 stage→commit→push（實測工作區有其它 tracked 變更時造成 merge 混亂）。stage 後用 `git diff --cached --name-only` 核對白名單，混入非預期檔就 `git restore --staged <檔>` 退出。 |

**五項全數成立 → 自動 push，不需再次核准。** 任一項不成立就停在那一步，依 Phase 5／troubleshooting 處理，回到 gate 再判定。

> 注意：此自動化**僅適用 push-repo 技能的 repo 建立／推送流程**，不覆蓋使用者的全域硬規則（未明確授權不 push／不設 remote）；gate 1 是 union 的一部分，不是可跳過項。push 後仍須跑 Phase 6 驗證，`fail=0` 才算完成。

### Policy-based auto-push：預先授權載體取代每次 push 字眼

「沒有本次 push 字眼」不代表不能自動 push —— 但**安全機制要求的是授權有載體／證據（claim ≠ evidence），不是每次都重新問**。當存在下列**預先核准且目前仍生效**的授權載體時，該載體**等同 gate 1 的明確授權**，可觸發自動 push，不需逐次向使用者核准。

| 載體 | 判定為有效的條件 |
| --- | --- |
| `automation`／`type:"code"`（`tools.automation.create`） | 有活動中的 automation，其 action 為 `type:"code"`、內容明確執行本技能的 preflight／commit／push／verify，且建立時已取得本次 session 明確授權。**限制**：`type:"code"` 只能呼叫 `tools.box.shell`（遠端 box、cwd 在 `/workspace`、無 `.git`、看不到本機 `/home/sam`），**碰不到本機 repo**。 |
| `automation`／`type:shell`（`tools.automation.create`） | 有活動中的 automation，其 action 為 `type:shell`，command 呼叫本技能 `scripts/` 下可達**本機** repo 的受控腳本，且建立時已取得本次 session 明確授權。此載體是本機 git 動作的**唯一可達路徑**（`type:"code"` 做不到）。示範採**只讀**檢查（五項 gate + git 狀態），**不 stage／commit／push**，回報落 automation `lastOutput`。 |
| allow-list／policy 檔 | 有預先核准的 repo／path 清單檔（含 private 裁決），executor 只對照清單動作，不在對話中逐次問 |
| systemd user service | 有 enabled／active 的 unit，其 `ExecStart` 呼叫本技能的 `scripts/verify_push.py` 或受控 push script，且 unit 建立時已明確授權 |

**載體不存在或已失效 → 退回 gate 1**，要求本次 session 明確的 push／推送／publish／deploy 意圖；跨 session 的舊口頭話不算（claim ≠ evidence）。此設計與 `push-router` §0 鐵律一致：授權必須有載體，不是「上次講過」。

> **fail-closed**：政策載體只豁免「逐次核准」這一步（gate 1 的表達形式），**不豁免 gate 2–5 的任何一項**。任一項不成立就停，不因為「有政策」而勉強 push。

> **仍受 gate 2 credential private 約束**：政策自動 push **仍受** gate 2 限制 —— 涉及 credential（token／私鑰／API key／client secret／credentials 清冊）的 repo，即使政策载體有效，也**必須 private repo**；public 視為未授權，停在鐵律要求擁有者裁決。政策不能繞過這條。

> **gate 5 精簡 stage 仍適用**：政策自動 push 仍用精確 stage 白名單，禁用 `git add -A`／`git add .`；actor 干擾（其它流程 unstaged 變更）依白名單排除，不因「有政策」而誤收。

> push 後仍須跑 Phase 6 驗證，`fail=0` 才算完成（與手動 push 相同）。

> **Logic check: 2026-11-26 (fix4)**：fix3 政策表僅列 `type:"code"`，但其實作只能呼叫 `tools.box.shell`（遠端 `/workspace`、無 `.git`、看不到本機 `/home/sam`），無法觸及本機 repo；真正碰得到本機 git 的只有 `type:shell`。故補承認 `type:shell` 為本機唯一可達載體，維持 fail-closed 與 gate 2–5 不變，示範限值為只讀檢查（不 push）。

### Phase 5 — 提交與推送

```bash
# 新環境先確認 commit 身分，否則 commit 直接失敗 Author identity unknown
# 用 repo 層級設定，不寫 --global 污染其他 repo
git -C <DIR> config user.name >/dev/null 2>&1 || git -C <DIR> config user.name "<name>"
git -C <DIR> config user.email >/dev/null 2>&1 || git -C <DIR> config user.email "<email>"
BRANCH=$(git -C <DIR> branch --show-current)
# 精確 stage：只用白名單，禁用 git add -A（會誤收其它流程 uncommitted 變更）
git -C <DIR> add <明確檔清單>
git -C <DIR> diff --cached --name-only   # 核對白名單，混入非預期檔就 git restore --staged 退出
git -C <DIR> status --short | grep -E '\.env$|credential|\.pem|\.key' ; # 應為空
git -C <DIR> commit -m "chore: 建立 <repo> 版本庫"
git -C <DIR> remote add origin <URL>      # 已有 remote 就跳過；URL 不可含 token
git -C <DIR> push -u origin "$BRANCH"
```

#### 憑證：來源、送出方式、常見失敗（唯一真相來源）

本節是推送憑證的**唯一參考**。不要再把「token 從哪裡來」和「token 怎麼送出去」拆給不同技能 —— 那會產生兩份互相矛盾的指令。

**1. token 從哪裡來（申請／存放）**

- 申請（擇一）：
  - **fine-grained**（`github_pat_...`，建議）：Settings → Developer settings → Personal access tokens → Generate new token (fine-grained)，選目標 repo（或帳號），給 `Contents: Read and write`；推 `.github/workflows/` 再給 `Workflows: Read and write`。
  - **classic**（`ghp_...`）：Generate new token (classic)，勾 `repo`；推 `.github/workflows/` 再勾 `workflow`。
- scope 不足的後果：一般寫入缺權限 → 403；推 workflows 缺 `workflow`／`Workflows` → `workflow scope missing`（見下方失敗表）。
- 存放：單行 token 放 `~/.credentials`（本機、檔權限 600）。`TOKEN=$(cat ~/.credentials)` 是合法的「讀取」，問題永遠在「送去哪」。

**2. token 怎麼送出去 —— 只有兩條路**

```bash
# 首選：gh 已登入
gh auth setup-git

# 沒有 gh：GIT_ASKPASS 指向暫存 script，不落 .git/config / reflog / shell history
# 用 subshell 包住：trap 只在本區塊生效，不覆蓋既有 EXIT trap，push 結束即清理
(
  ASK=$(mktemp)
  printf '#!/bin/sh\necho %s\n' "$TOKEN" > "$ASK"
  chmod 700 "$ASK"
  trap 'rm -f "$ASK"' EXIT
  GIT_ASKPASS="$ASK" git push -u origin "$BRANCH"
)
```

`https://<token>@github.com/...` **不可**：token 會留在 `.git/config`、reflog 與 shell history，等於把 token 提交出去。就算不改 remote 只寫在指令裡，argv 與 process list 仍會暴露。

> **不要用 `GIT_ASKPASS=<(printf ...)`（process substitution）。** 它產生的是 pipe（`/dev/fd/N`），git 用 `exec` 執行 askpass 路徑時會 `cannot exec '/dev/fd/N': 拒絕不符權限的操作`（實測 exit 128，即使 shell 是 bash）。這不是單純的 bash/dash 相容問題，而是 pipe 根本不可 exec —— 所以用上面 `mktemp` + `chmod 700` 的**真實檔案**。`trap ... EXIT` 確保 push 失敗也清掉暫存 script。

**3. 常見 push 失敗 → 原因 → 動作**

| 訊息 | 原因 | 動作 |
| --- | --- | --- |
| `Repository not found (404)` | repo 不存在／token 屬別的帳號／私有 repo 無權限（GitHub 回 404 而非 403） | 見下方「404 的處理」 |
| `Permission denied (403)` | token 缺 `repo`／`Contents: Write` | 重新產生含正確 scope 的 token |
| `workflow scope missing` | 推 workflows 但缺 `workflow`／`Workflows` scope | 補 `workflow` scope |
| `Large file warning` | >50 MB 檔案 | 見 Phase 2 LFS／排除 |
| `fetch first` | 遠端有新 commit | `git pull --rebase`，預設不要 force push |

**404 的處理（含建 repo 權限）**

```bash
# 1. 先確認 token 屬哪個帳號；login 不是預期 owner 就停，換對的 token
curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/user
# 2a. 個人 repo
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/user/repos \
  # 含 credential → private=true（push-router §0.6：public 視為未授權）
  -d '{"name":"<repo>","private":<BOOL>}'
# 2b. org repo
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/orgs/<org>/repos \
  # 含 credential → private=true（push-router §0.6：public 視為未授權）
  -d '{"name":"<repo>","private":<BOOL>}'
```

**API 建 repo 需要比推送更高的權限**：classic 勾 `repo`；fine-grained 要 `Administration: Read and write` 且 token 範圍選「All repositories」—— 只授權單一 repo 的 fine-grained token 建不了新 repo。沒這些權限就改用網頁 `https://github.com/new` 手動建，不要拿既有 token 一直重試。

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
| token 寫進 remote URL | `.git/config`、reflog、shell history、process list 留下明文；公開 repo 一推就收不回來 | `gh auth setup-git`／`GIT_ASKPASS`；已寫入就 `set-url` 改回**不含 token 的 URL**並輪替金鑰 |
| `GIT_ASKPASS=<(printf ...)`（process substitution） | 產生 pipe（`/dev/fd/N`）不可 exec，git 回 `cannot exec ... 拒絕不符權限的操作`（實測 exit 128，**即使 bash**） | 一律用 `mktemp` 暫存 script + `chmod 700` + `trap rm`；不要用 process substitution |
| 推 `.github/workflows/` 卻用一般 scope 的 PAT | 403 `workflow scope missing` | 重新產生含 `workflow` scope 的 token |
| 推送後直接刪來源 | 排除清單裡的檔案一起消失 | 先給清單，再讓使用者決定 |
| 自我指涉：掃描器的註解被自己的 regex 抓到 | 修正判定後 verify 反而在「工作區／歷史無機密」兩項 FAIL（實測 `fail=2`），看起來像修正失敗 | 講解只寫描述，不貼可執行的字面指派式；若註解含 URL query 分隔符 `&`，豁免條件要與 separator 消耗一致（第一個指派符號已被消耗，值裡不會再有它，故只判斷 `&`，不要再要求值內也有指派符號）。改完先對腳本自身跑一次掃描，命中數須為 0 再 commit |
| 用 `git update-index --assume-unchanged` 讓 verify 顯示乾淨 | 工作區其實有未提交變更，推上去的與看到的不同；「工作區乾淨」檢查被遮蔽 | 先 commit 讓工作區真正乾淨再驗證；verify 前用 `git ls-files -v` 確認沒有 `h` 前綴（正常是 `H`）；不要用 index 技巧掩蓋 FAIL |

## 常見錯誤

- **「我加了 .gitignore，所以安全了。」** 只對新 commit 有效。歷史要另外處理。
- **「排除清單太長，寫幾個代表就好。」** 驗證會抓孤兒檔；漏一列就是一個沒交代的檔案。
- **「改了歷史就安全了。」** force push 不會立刻清掉遠端物件；只要該 repo 曾經推出去，就把那把金鑰當成已洩漏並輪替。
- **「大檔先 exclude，之後再說。」** `_repo_excluded.tsv` 的 `backup` 欄就是要你當下回答「那原本那份在哪」。
- **「push 成功就是完成。」** 遠端可能是空的、可能推錯 branch、可能被 pre-receive hook 改寫。
- **「使用者說要全進去，就 `git add -f` 全部。」** 還是要回報大小與機密；100 MB 以上 GitHub 會直接拒絕。
- **「先把 token 寫進 URL 推完再改回明文就好。」** 改回 URL 不會清掉 reflog、shell history 與 process list；推公開 repo 的當下就等於把 token 公佈，事後只能輪替金鑰。
- **「URL 寫法最不容易因 bearer 支援差異出包，所以先用它。」** 這是拿「可能的相容性問題」換「確定的憑證洩漏」。gh 或 GIT_ASKPASS 才是同時滿足安全與可用的路徑。
- **「排除帳本跟 `.gitignore` 重複，又會 drifting，不必做。」** `.gitignore` 給 git、`_repo_excluded.tsv` 給 clone 的人；後者回答的是「clone 後消失的檔案原本在哪」，`git status --ignored` 看不到。
- **「對帳等式太脆弱、假陽性多，不必做。」** 對帳就是要逼出那些「以為排除、其實漏掉」的孤兒檔；`git status` 只告訴你 git 的觀點，不告訴你磁碟的真實檔案數。
- **「verify 報 FAIL，先把它藏起來讓它 PASS。」** `assume-unchanged` 或臨時改檔案只掩蓋症狀；FAIL 要查到根因並修正，工作區要真的乾淨再驗證。
- **「修正機密判定不會有副作用。」** 掃描器本身的註解與範例也會被掃到；改完先對它自我掃描（命中數須為 0），再跑完整 verify，且真實憑證格式仍須硬 FAIL。

## 驗收清單

- [ ] `preflight.md` 的機密（工作區＋歷史）、大檔、巢狀 repo 三節都讀過
- [ ] repo 是新建的，或確認沿用了既有歷史（沒有 `rm -rf .git`）
- [ ] `_repo_excluded.tsv` 每一列都有 `reason` 與 `backup`
- [ ] `git ls-files -s | grep 160000` 為空（沒有意外的 gitlink）
- [ ] 追蹤檔案裡沒有 `.env`／token／私鑰
- [ ] `verify_push.py` 全 PASS、`fail=0`
- [ ] 若改過 `verify_push.py`：先自我掃描該檔（命中數 0），且未用 `assume-unchanged` 遮蔽工作區
- [ ] 回報含 `tracked / disk / excluded` 三個數字與 remote URL

Logic check: 2026-11-26 — 新增「Push 時機：五項 gate 全綠 → 自動 push（免再次核准）」章節（rev-skill：RED 4 fail → GREEN）。

Logic check: 2026-11-26 (fix2) — 依核實結果修正 4 點：gate 1 限本次 session 不沿用舊授權；gate 2 credential repo 一律 private（對齊 push-router §0.6）；gate 5 精確 stage 禁用 git add -A；Phase 5 分支改用 $BRANCH 不硬編碼 main。rev-skill RED 5 fail → GREEN。

Logic check: 2026-11-26 (fix3) — 新增「Policy-based auto-push」規則節：預先核准且生效的授權載體（automation／allow-list／systemd）等同 gate 1 明確授權，可免逐次核准；載體不存在退回 gate 1；fail-closed 不豁免 gate 2–5；仍受 credential private 與精確 stage 約束。rev-skill RED 7 fail → GREEN。

Logic check: 2026-11-27 — 依 oskill @ a3e0c20 實測新增兩條陷阱：掃描器自我指涉（註解的 URL query 範例被自身判定式抓到，`fail=2`）與 `assume-unchanged` 遮蔽工作區；配套要求「改完先自我掃描命中數 0」與「先 commit 再 verify」。真憑證格式仍硬 FAIL，未削弱其它檢查。

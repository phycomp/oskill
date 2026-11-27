---
name: push-router
description: >
  推送／Git 家族 parent / 單一入口：依目標把 request route 到既有 push-*/\*-push/git-* child skill（通用目錄推 repo、Streamlit 部署、環境剖面上傳、logical commits 拆分、PAT/remote 除錯、ljg skills 同步、publish new repo、clone/pull、Paperclip 部署），本身不重複 child 的領域規則；chain-skill 六階段閉環 + darwin-skill 進化規則（E0-E3 / 9 維 rubric / keep-revert 棘輪）。Use when the user asks to push, commit and push, publish to GitHub, deploy Streamlit, push env-profile, sync skills to repo, clone/pull a repo, or which push/git skill to use, or the 鐵律「本機 commit 不 push、不設 remote」（除非明確要 push repo）, or credential repo must be pushed to a private repo (never public). 所有回覆／文件使用繁體中文（正體中文）。
version: "1.2.0"
user-invocable: true
---

# Push Router — 推送／Git 家族父節點 / 單一入口

> 2026-11-24 重構整合：以 chain-skill 六階段閉環 + darwin-skill 進化規則建立。push-router **只做「目標 → hook child」決策**，不重複 child 的領域規則；實際推送／部署由 hooked child skill 承接。涵蓋 `push-xxx`、`xxx-push`、`git-xxx` 三種型式。

## 0. 鐵律（優先於一切）：本機 commit 不 push、不設 remote

> **除非使用者明確要求 push repo，否則鐵律是「本機 commit、不 push、不設 remote」。** 本節優先於 §1 所有 goal→hook 決策與 §3 功能集合；任何 child skill 的推送／部署動作都受此閘門約束。

判定與執行要點：

1. **明確 push 意圖才解鎖**：使用者原話須出現「push／推送／push 到遠端／推上 GitHub／publish／deploy／上傳遠端」等明確對外動作意圖，才允許 hook push child（`push-repo`／`publish-to-github`／`quantum-website`等）執行。
2. **僅 commit 不算授權**：「commit」「本機 commit」「先在本機存一版」「記錄一版」等僅要求版控的命令，**只做本機 commit**，不得 push、不得設 remote。
3. **不設remote**：未獲明確 push 授權時不得新增 remote（`git remote add`／`git remote set-url`）；remote 已存在也不代表可 push。
4. **不沿用舊授權**：前一個 session 或其它對話曾授權 push，**不構成**本次 push 授權（claim ≠ evidence）；每次 push 都要本次明確意圖。
5. **現況宣告**：完成本機 commit 後須明確告知「未 push、無 remote」或「未 push（remote 已存在）」，讓使用者可核對。
6. **credential repo 一律 private**：若 repo 涉及 credential（token／私鑰／API key／client secret／session cookie／credentials 清冊等），即使已明確授權 push，也**不得 push 至 public repo**；必須 push 至 private repo。 public repo 視為未授權，先停在鐵律並要求使用者裁決建立 private repo。private 不構成把秘密值寫入 repo 的授權——token／私鑰／session 仍不得進 remote URL、git config 或檔案（遵循環境剖面憑證政策）。

> 例外次序：若同時命中 §1 某 goal 但使用者未明示 push → 先停在鐵律，改 hook 本機 commit；待明確 push 意圖出現才續走原 goal 的 child。

> credential 次序：若命中第 6 點（涉及 credential），即使 push 意圖明確，仍先確認目標為 private repo；未確認前不得 push。

## 1. Parent Node — 目標 → hook 決策（need-based predicate）

push-router 是推送／Git 家族的 **parent / 單一入口**：使用者提出推送／版控需求時先載本 skill，再依目標 hook 既有 child。判定依 **goal，不是 skill 名稱**；parent 不 inline child 步驟。

| Goal | Hook（既有 child） | Skip when |
|---|---|---|
| 通用任意目錄變成自己的 repo 並推遠端／「推上 GitHub」／「這個目錄要版控」／404/403/workflow scope/PAT/remote/大小或秘密被拒／commit 後能否刪目錄（`push-xxx`） | `push-repo`（canonical 安全引擎） | 要拆分 working tree → `git-commit-and-push`；剖面 kit → `push-env-profile`；新 repo 產品化 → `publish-to-github` |
| Streamlit 網站推 GitHub → Streamlit Cloud / Hugging Face Spaces 部署／Kaggle Dataset 上傳（`push-xxx`） | `quantum-website`（合併自 push-streamlit v1.3.1 → toolkit-viz D） | 一般目錄 → `push-repo` |
| 環境剖面 kit／auto-load profile／可攜剖面／剖面含版本號或絕對路徑或憑證值／clone 後檔案消失（`push-xxx`） | `push-env-profile` | 通用目錄 → `push-repo`（本 skill 是剖面領域流程） |
| 拆分 uncommitted changes 成 logical single-concern commits 再 push／conventional commits 系列（`xxx-push`） | `git-commit-and-push` | 目錄本身要變 repo → `push-repo`（其明確 NOT for splitting） |
| commit → push GitHub／PAT 設定／remote 設定／大檔案／workflow scope 除錯（`git-xxx`） | `push-repo`（原 `git-push` 已封存） | 要拆分 commits → `git-commit-and-push`；新 repo 產品化 → `publish-to-github` |
| 同步 `~/.agents/skills/ljg-*` 到 ljg-skills repo（master→md 分支）（`xxx-push`） | `ljg-push` | 非 ljg skills／任意 repo → `push-repo`（其明確 NOT FOR） |
| Publish 新 folder/skill 成 repo／create repo／fork upstream／加 README/topics/release／第三方 patched skill 歸屬（`git-xxx` 邊界） | `publish-to-github` | 已存在 repo 只 push → `push-repo`；**安全 preflight/commit/push/verify 一律委派 `push-repo`** |
| clone / update repo／`git pull`／`update env-profile`／pull latest（反向邊界） | `repo-pull` | push 需求 → 上方 push skills |
| 部署 Paperclip agents 到 self-hosted instance／裝 server／hire agents／PostgreSQL 失敗（`xxx-push` 名稱但為部署域） | `paperclip-deploy-push` | 單純 repo push → `push-repo` |

### Need-based predicate 細則
- 一個 request 命中單一 goal → 只 hook 該 child，不廣播。
- 跨 goal（例：commit 拆分 → push → deploy Streamlit）→ 依序 hook `git-commit-and-push` → `push-repo`/`quantum-website`，parent 只處理順序與銜接，不重複解釋。
- 邊界語意（children 已宣告）：
  - `push-repo` 明確「Not for splitting an existing working tree into logical commits」→ 拆分導向 `git-commit-and-push`。`push-repo` 為安全推送 canonical 引擎；`publish-to-github` 的產品化流程完成後必須 hook `push-repo` 執行 preflight/commit/push/verify，不得自行繞過。
  - `push-env-profile` 明確「與 push-repo 不同：通用任意目錄 vs 剖面 kit 領域流程」→ 剖面導向 `push-env-profile`。
  - `ljg-push` 明確「NOT FOR pushing non-ljg skills or arbitrary git repos」→ 非 ljg 導向 `push-repo`。
  - `repo-pull` 是 pull 反向操作，僅在 clone/update 目標 hook，不與 push skills 並列。
- parent 不自行產出領域內容；children own their rules。

## 2. 既有本機 child 盤點（不另開發）

| Child | 型式 | 位置 | 版本／狀態 | 角色 |
|---|---|---|---|---|
| `push-repo` | `push-*` | `.agents/skills` | 活動（allow-list） | **canonical 安全引擎**：preflight/exclude/verify/push；被 `publish-to-github` hook |
| `quantum-website` | `push-*` | `.opencode/skills` | D1–D7（原 push-streamlit v1.3.1 → toolkit-viz D，deprecated） | Streamlit → Cloud/HF／Kaggle |
| `push-env-profile` | `push-*` | `.agents/skills` | 活動（allow-list） | 環境剖面 kit 上傳 repo |
| `git-commit-and-push` | `*-push` / `git-*` | `.agents/skills` | 活動 | logical commits 拆分後 push |
| `ljg-push` | `*-push` | `.agents/skills` | 活動 | ljg-* skills 同步 |
| `publish-to-github` | `git-*` 邊界 | `.agents/skills` | 活動 | 新 repo 產品化（gh create/fork/topics/release/attribution）；安全 push 委派 `push-repo` |
| `repo-pull` | git 反向邊界 | `.agents/skills` | 活動 | clone/update repo |
| `paperclip-deploy-push` | `*-push` | `.agents/skills` | 活動 | Paperclip 部署（部署域） |

- **不另開發**：以上 8 個 child 全部既有本機技能；push-router 不新建重複推送技能。
- 已封存：`git-push`（1.0.0）搬到 `.agents/skills-archive`；原因為 token 寫入 remote URL 違反憑證政策且與 canonical `push-repo` 重疊，其路由改由 `push-repo` 承接。
- 跨家族：Paperclip 部署屬 paperclip 家族，明確父節點見 §5。

## 3. 功能集合（Function Set）

推送家族功能模組映射到 child：

1. **通用推送／故障排除（canonical）** — `push-repo`（preflight/排除/歷史機密/大檔/巢狀 repo/fresh-clone md5 驗證；404/403/PAT/remote/size/secrets）。
2. **平台部署** — `quantum-website`（Cloud/HF/Kaggle）、`paperclip-deploy-push`（self-hosted）。
3. **剖面 kit** — `push-env-profile`（可攜剖面／auto-load／上傳）。
4. **commit 工藝** — `git-commit-and-push`（logical commits 拆分）→ `push-repo`（安全 commit→push；原 `git-push` 已封存）。
5. **領域同步** — `ljg-push`（ljg skills，master/md 分支）。
6. **發布新 repo（產品化）** — `publish-to-github`（gh create remote/fork/topics/release/attribution）；實際安全 push/verify 委派 `push-repo`。
7. **反向拉取** — `repo-pull`（clone/update）。

## 4. 閉環六階段（chain-skill 風格）

1. **Plan** — 本 skill 與 push 家族盤點對齊（push-* 3 + *-push 4 + git-* 2）。
2. **Code** — 本 SKILL.md + child skills 既有，不另開發。
3. **Test** — darwin-skill E0 體檢 + chain-skill Logic Consistency Check（goal→hook 無衝突）。
4. **Verify** — allow-list SSOT 同步（push-router 納入）+ hook 目標存在性驗證（9/9）。
5. **Review** — whole-branch review（native，no worker mechanism）。
6. **Close** — distill：Version Log + chain-skill Inventory + skill-family 索引同步。

## 5. Cross-family references（明確父節點）

| Target Family | Explicit Parent | 說明 |
|---|---|---|
| `paperclip-xxx` | `paperclip-board`（parent）/ `paperclip-deploy-push`（部署 child） | Paperclip 部署與代理治理 |
| `env-profile` | `push-env-profile`（parent）/ `inspect-env-profile`（診斷） | 剖面 kit 上傳 vs 診斷 |
| `skill-family` | `skill-family`（parent router，unified entry） | 跨家族路由總入口 |
| `audit-skill` | `audit-skill`（security gate） | publish 前安全審查（publish-to-github hook） |

- 跨家族流程以 parent → hook chain 為序；每個 family 入口標註 parent，避免歧義。

## 6. Evolution — darwin-skill 進化規則

E0–E3／9 維 rubric／keep-revert 棘輪的規則單一來源為 `darwin-skill`。本 router 不重複其實作；需要進化時 hook `darwin-skill`，依它的流程執行。

## Version Log
- 1.2.0 — 2026-11-25：新增 §0 第 6 點「credential repo 一律 private」：涉及 credential 的 repo 即使獲明確 push 授權，也必須 push 至 private repo，不得 push 至 public；private 不構成了秘密值入 repo 的授權。補 description 觸發詞與 version；rev-skill RED 6→GREEN 6/6。
- 1.1.0 — 2026-11-25：新增 §0 鐵律（優先於一切）：除非明確要求 push repo，否則本機 commit 不 push、不設 remote；補 description 觸發詞與 version。
- 1.0.0 — 2026-11-24：初始建立。以 chain-skill 六階段 + darwin-skill 進化規則重構 push 家族（push-* 3 + *-push 4 + git-* 2，共 9 child）；明確 parent/child、need-based predicate、children 邊界語意、跨家族父節點表、E0-E3 進化棘輪。

## Notes
- 使用者語言：繁體中文（文件 prose 以繁體中文為主）。
- no worker mechanism（native 執行）。
- allow-list 為 SSOT：push-router 納入改 allow-list 後同步 chain-skill / skill-family 索引。
- 不另開發：9 child 全部既有本機技能。
- 憑證政策：token 不進 remote URL／git config／history；使用 `GIT_ASKPASS`（詳見 `quantum-website` D3 引用的 push.sh 腳本，非本 skill 檔案）。
Logic check: 2026-11-26 (rev-skill / quantum-website 規則搬移) — 現行引用同步指向 `quantum-website`；僅引用同步，規則語意不變。Gate 0 explicit consent；Gate 1 `push-router-qw-move-pre.sha256`；Gate 2 RED `tests/test_quantum_website_rule_move.py`；Gate 3 GREEN；Gate 5 drift 僅預期檔。

---
name: quantum-website
description: "Use when the user asks to 推送／部署 quantum_website、同步蒸餾主題到 Streamlit 網站、push 到 phycomp/quantum-website、Streamlit Cloud／Hugging Face Spaces／Kaggle Dataset 部署、GIT_ASKPASS／Repository not found 除錯，或提到 quantum website 規則。當使用者說『推送網站』『上傳新主題』『部署 Streamlit』時使用。本技能是 ~/quantum_website 同步／推送／部署的唯一規則來源（SSOT）；展示平台的架構／元件／版面／寫入 Gate 在 toolkit-viz。"
version: 1.0.0
---

# Quantum Website — 網站同步與部署技能

## 目標

`~/quantum_website`（GitHub `phycomp/quantum-website`）的來源同步、提交推送、部署驗證與除錯**唯一規則來源（SSOT）**。2026-11-26 由 `toolkit-viz` SSOT.D1–D7 完整搬移沉澱；`toolkit-viz` 只保留一行指向本技能，不再維護第二份規則。

## 與其他技能的分工

| 技能 | 負責 |
|---|---|
| 本技能（quantum-website） | repo 事實卡、同源同步閘門、Git／credentials、提交推送、三部署目標、驗證、除錯（D1–D7） |
| `toolkit-viz` | 蒸餾成果展示平台：SSOT A–C（架構／元件／版面）與 E（寫入前 Gate）；D 節只留指向本技能的指標。展示位置規則見其 SSOT.A.4：成果僅展示在 `~/進化技能`，**非明確要求不進入本技能**（本技能只管推送部署 D1–D7，不管展示在哪）|
| `push-streamlit` | deprecated_keep thin alias，僅供既有引用追溯；5 支 scripts 保留原路徑，由本技能 D2/D4/D5 引用 |
| `push-repo` | repo 初始化、推送目標、PAT setup、token 安全送出、push 全流程決策（D3 hook） |

> 規則不重複：其他地方只 hook 本技能，不複製 D1–D7 條文。

## D1. Repo 事實卡（一律用指令查證，勿憑記憶拼湊）

| 項目 | 值 |
|---|---|
| 本地目錄 | `~/quantum_website`（底線） |
| GitHub repo | `phycomp/quantum-website`（連字號） |
| origin | `https://github.com/phycomp/quantum-website.git` |
| 推送帳號 | `phycomp`（token 持有者）；commit author ≠ 推送帳號 |
| 預設分支 | `main` |
| HF CLI | `hf`（huggingface_hub 1.x；無 `spaces create`，靠 `hf upload --type space`） |
| Kaggle CLI | `/home/sam/flex/bin/kaggle`（憑證 `~/.kaggle/kaggle.json` chmod 600） |

推送目標一律從 `git remote get-url origin` 推導，**禁止**從 commit author 或目錄名拼 owner/repo（歷史事故：`ontxac/quantum_website` → Repository not found）。

## D2. 同源同步閘門（git add 之前必跑）

```bash
python /home/sam/.opencode/skills/push-streamlit/scripts/sync_topics.py
```
- 同步 `~/量子/PQC/topics/*.md` → `data/topics/`、`~/量化/topics/0*.md` → `data/quant_topics/`、`~/.opencode/skills/topological-insulator/references/*.md` → `data/ti_topics/`。
- 只取來源頂層檔案；同名覆蓋；repo 缺檔補齊；同步後逐一 md5 驗證。
- **exit 1（來源缺失／無檔／複製失敗／驗證不符）→ 不得 push**。
- 支援 `--dry-run`。新增主題時把 references 目錄加進 `SYNC_PAIRS`，驗證所有 `[OK]` 無 `[FAIL]`。
- 主題內容改來源檔（sync 以來源覆蓋 repo）；**`data/topics_index.json` 預設不註冊新主題**——僅在使用者明確指出要註冊時才新增/更新該索引；獨立演示工具直接讀蒸餾來源目錄，不經此索引。
- ⚠️ `content_loader` 是「家目錄優先、repo data/ fallback」，本機測試正常 ≠ 雲端正常；push 前一律以 repo `data/` 為準。

## D3. Git／Credentials → hook `push-repo`
- repo 初始化、推送目標、PAT setup、token 安全送出、push 全流程決策由 `push-repo` 承接，本節不重複。
- token 一律走 `GIT_ASKPASS` + mktemp（chmod 700，trap 清除），**不進 remote URL／git config／history**。

## D4. 提交與推送腳本
```bash
git add -A
git -c user.name=phycomp -c user.email=phycomp@gmail.com commit -m "feat: <desc>"
bash /home/sam/.opencode/skills/push-streamlit/scripts/push.sh [repo目錄] [分支]
```
`push.sh` 依序：origin 前置檢查 → sync_topics 閘門 → GitHub API 驗證 token 帳號 → push。

## D5. 三個部署目標

| 目標 | 做法 | 限制 |
|---|---|---|
| Streamlit Cloud | https://share.streamlit.io → 選 repo／main／`app.py` → Deploy | 免費；需 GitHub 登入；Sharing 必為 Public |
| HF Spaces | `hf auth login` → `bash scripts/push_hf_space.sh [space] [--private] [--wait] [--dry-run]` | **2026-11-12 實測：免費層無法跑 Streamlit**（sdk=streamlit → 400；docker → 402；static 只能放文檔鏡像）；要嘛升 PRO，要嘛用 Cloud |
| Kaggle | `bash scripts/push_kaggle_dataset.sh [slug] [--public] [--stock-only] [--dry-run]` | **只能** Dataset／Notebook，不能託管 Streamlit；Notebook 無持久服務 |

HF 網址：`https://<owner>-<space>.hf.space`（小寫、底線轉連字號）；Kaggle：`https://www.kaggle.com/datasets/<user>/<slug>`。投資文檔保留「歷史績效不代表未來」。

## D6. 驗證
- Streamlit Cloud／HF：`curl -s -o /dev/null -w "%{http_code}" <base_url>/_stcore/health` 應為 200；303 → Sharing 改 Public。
- health 只證明 app 活著，**不證明內容完整**；內容完整性由 D2 sync（數量＋md5）保證，部署後抽查主題數等於 repo `data/` 檔數。
- Kaggle：`kaggle datasets files <id>` 核對檔案清單。
- HF `--wait` 會輪 polling health（首次 build 需數分鐘）。

## D7. 除錯與預防（合併去重）

| 現象 | 診斷 | 處置 |
|---|---|---|
| sync 未執行／新主題未同步 | 輸出缺 `[OK]` | 跑 sync；把新 references 加進 `SYNC_PAIRS` |
| "Everything up-to-date" 但遠端落後 | `git branch -vv` 無 `[origin/main]` | `git push --set-upstream origin main`（token 走 GIT_ASKPASS） |
| "Repository not found" | `git remote -v` 拼錯 owner/repo | 從 `git remote get-url origin` 推導 |
| push 無認證（could not read Username） | 無 PAT／SSH／helper | `gh auth setup-git` 或 GIT_ASKPASS（見 D3） |
| Streamlit Cloud 未更新 | push 成功但 webhook 未觸發／app 私有 | dashboard 手動 Reboot；Sharing → Public |
| HF build 失敗／打不開 | `hf spaces logs`／`hf spaces info` | 查 `requirements.txt`、`sdk_version`、`app_file`；`hf.space` 可能被本地網路封鎖 |
| Kaggle 401/403 | `kaggle.json` 權限非 600 或 key 失效 | `chmod 600`；`kaggle datasets list -m` 驗證 |

預防：每次 push 前 `git branch -vv` → sync_topics → commit → push.sh → `git fetch origin` 比對 → health 驗證。

## 觸發條件

- 「推送／部署 quantum_website」「推送網站」「推送 Streamlit」「上傳新主題」「部署 Streamlit」
- 「同步蒸餾主題」「sync_topics」「push.sh」「Streamlit Cloud／HF Spaces／Kaggle Dataset」
- 「GIT_ASKPASS」「Repository not found」「token 帳號驗證」「health 驗證」
- 「quantum website 規則」「quantum-website 技能」
- 「不要動 quantum_website／不要 push」→ 停手，不進入 D2–D4

## 歷史追溯

- 本技能只沉澱**現行有效規則**（D1–D7）；既有稽核軌跡留在 `~/.opencode/skills/toolkit-viz/SKILL.md` 的 4 行 `Logic check:`（2026-11-25：B2 完全移除／skill_inventory 整合／A4 移除／索引註冊改預設不註冊），以及 `push-streamlit/SKILL.md` 的 deprecated alias 紀錄，**原文不改寫**。
- 本技能的規則前身為 `push-streamlit` v1.3.1 → `toolkit-viz` SSOT.D（2026-11-25 合併）→ 本技能（2026-11-26 搬移）。`push-router`／`viz-router`／`skill-family`／`skill-seek`／`chain-skill`／`skill-dependency-hook`／`social-media-suite`／`sci-router`／`audit-credential`／`topic-distill`／`stock-market`／`topic-post`／`ai-ml-app-engineering`／`da-xue` 的現行引用已同步指向本技能；歷史字串保留。

Logic check: 2026-11-26 (rev-skill / quantum-website 規則搬移) — 依使用者四項裁決（搬移＋引用／4 行歷史原樣保留／跨技能引用同步／技能置 `~/.opencode/skills/`），把 `toolkit-viz` SSOT.D1–D7 完整搬移至本技能；`toolkit-viz` D 節改為指標，A–C/E 與 `app.py` 規則不改。Gate 0 explicit consent；Gate 1 pre manifests：toolkit-viz `toolkit-viz-qw-move-pre.sha256` 及 15 份跨技能 `{skill}-qw-move-pre.sha256`（新技能無改前基線，建立即交付）；既有 HIGH/CRITICAL 皆為 pre 既有（`data/skill_inventory_viz_data.json` 快照、`push_kaggle_dataset.sh`、`audit-credential` 憑證盤點），白名單排除，不屬本輪寫入範圍。Gate 2 RED `tests/test_quantum_website_rule_move.py` 48 項失敗 exit=1；Gate 3 GREEN 最小修正；Gate 4 清快取；Gate 5 re-audit + drift，變更清單僅預期檔。

Logic check: 2026-11-26 (rev-skill / __init__.py 物理移除) — 依使用者裁決，`quantum_website` 根目錄 `__init__.py` 以 `git rm` 移除，`app.py` 為物理上唯一入口；`tests/test_structure.py` 移除 `test_entrypoints_in_sync()` 與根 `__init__.py` compile，同步更新 `app.py` docstring；D5（Streamlit Cloud 選 `app.py`）與 `push_hf_space.sh`（排除 `__init__.py`）規則不變。`streamlit_stl/__init__.py`／`src/views/__init__.py` 為套件檔保留，`toolkit-viz` 加對應 Logic check 追溯。Gate 0 explicit consent；Gate 1 pre manifest `quantum-website-initcleanup-pre.sha256`（2 MEDIUM，白名單排除）；Gate 2 RED 9/14 失敗 exit=1；Gate 3 GREEN；Gate 5 re-audit + drift。

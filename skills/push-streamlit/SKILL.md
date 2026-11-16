---
name: push-streamlit
description: "Streamlit 網站推送技能：從本地開發 → GitHub 推送 → Streamlit Cloud / Hugging Face Spaces 部署，並可把主題文檔發布成 Kaggle Dataset；含 credentials 設定與常見問題。Use when the user wants to push a Streamlit website to GitHub, deploy to Streamlit Cloud or Hugging Face Spaces, or publish/upload datasets to Kaggle."
version: "1.3.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---
# Push Streamlit — 網站推送與部署

## Repo 事實卡（勿憑記憶拼湊，一律用指令查證）

| 項目 | 值 |
|------|-----|
| 本地目錄 | `~/quantum_website`（**底線**） |
| GitHub repo | `phycomp/quantum-website`（**連字號**） |
| origin | `https://github.com/phycomp/quantum-website.git` |
| 推送帳號（token 持有者） | `phycomp` |
| commit author | `ontxac <ontxac@gmail.com>`（僅 commit 署名，**與推送帳號無關**） |
| 預設分支 | `main` |
| HF Spaces CLI | `hf`（`/usr/sbin/hf`，huggingface_hub 1.x；**無** `spaces create`，靠 `hf upload --type space` 自動建 repo） |
| Kaggle CLI | `/home/sam/flex/bin/kaggle`（Kaggle CLI 2.2.5；憑證 `~/.kaggle/kaggle.json` chmod 600，或 `KAGGLE_USERNAME`/`KAGGLE_KEY`） |
| 三個部署目標 | Streamlit Cloud（互動網站，需 GitHub 登入）／HF Spaces（互動網站，`hf` CLI）／Kaggle（**只能** Dataset・Notebook，不能託管 Streamlit） |

> ⚠️ 事故備忘（2026-11-11「Repository not found」根因）：
> 舊版流程要人工填 `<username>/<owner>/<repo>`，結果把 commit author（ontxac）
> 當成推送帳號、又從目錄名拼出 `quantum_website`（實為連字號 `quantum-website`），
> push 到不存在的 `ontxac/quantum_website` → "Repository not found"。
> **推送目標一律從 `git remote get-url origin` 推導，不得自行拼湊；
> commit author ≠ 推送帳號；目錄名 ≠ repo 名。**

## 流程

### 1. 本地開發
- 單一入口架構：`app.py`（含 `st.set_page_config`，只呼叫一次）+ `src/views/` 函式模組 + `requirements.txt`；**不用** `pages/` 目錄或 `st.navigation`（先前 pages/ 在 Streamlit Cloud 造成 StreamlitAPIException，已移除）。
- **主題清單一律 sidebar（`*_sidebar` 模式，全站統一展示）**：主題型區塊（Quantum 主題／Quant 主題／拓撲絕緣體／YouTube 貼文）各提供 `<name>_sidebar()`（sidebar radio，`horizontal=True`，回傳選定項），`app.py` 側邊欄依分區條件呼叫；主畫面 `render_*(sel)` 只渲染選定內容。區塊內的非主題大檔（如 TI 部署包、YT 市場分析）**併入同一 sidebar 清單當一項**。工具型區塊（STL／傳輸線／台股）的參數控制不在此限。回歸測試：`tests/test_app_smoke.py`（AppTest 驗證各區塊選項數與切換渲染）。
- `__init__.py` 與 `app.py` 內容同步（支援 `streamlit run __init__.py`）。
- 使用相對路徑引用資產（避免雲端路徑錯誤）。
- 本地測試：`streamlit run app.py`（Python 用 `/home/sam/flex/bin/python`）。

### 2. Git 設定（首次設定才需要）
```bash
cd ~/quantum_website
git config user.name ontxac && git config user.email ontxac@gmail.com   # commit 署名
git remote add origin https://github.com/phycomp/quantum-website.git
git remote -v   # 確認推送目標
```

### 3. Credentials
- GitHub PAT 儲存於 `~/.credentials`（一行，僅 token 值），屬於 **phycomp** 帳號。
- 手動推送時：`TOKEN=$(cat ~/.credentials)`。

### 4. 同步主題資料（git add 之前必跑）
```bash
python /home/sam/.opencode/skills/push-streamlit/scripts/sync_topics.py
```
- 同步 `~/量子/PQC/topics/*.md` → `data/topics/`（15 檔）、`~/量化/topics/0*.md` → `data/quant_topics/`（9 檔）、`~/.opencode/skills/topological-insulator/references/*.md` → `data/ti_topics/`（7 檔；TI 蒸餾主題以技能 references 為唯一真源）。
- 只取來源頂層檔案（`fb_posts/` 等子目錄自動排除）；同名一律覆蓋；repo 缺檔自動補齊；同步後逐一 md5 驗證。
- **exit 1（來源缺失/無檔/複製失敗/驗證不符）→ 不得 push**。
- 支援 `--dry-run`（只顯示將複製什麼）。
- 修改 Quant 主題內容必須改**來源檔** `~/量化/topics/`；TI 主題內容改**技能 references**（`~/.opencode/skills/topological-insulator/references/`）（sync 會以來源覆蓋 repo）。

> ⚠️ 事故備忘（2026-11-11「quant 主題無法上線」根因）：
> `content_loader` 與頁面載入器是「家目錄優先、repo data/ 為 fallback」—
> 本機永遠讀到家目錄的檔案，會**掩蓋 repo 缺檔**。本機測試正常 ≠ 雲端正常。
> 歷史上 commit 4c44911 只放了一個合併檔進 `data/quant_topics/`，9 個獨立主題檔
> 從未進 repo，靠本機 fallback 掩蓋、health check 也測不出來（只驗活不驗內容）。
> **push 前一律跑 sync_topics.py，以 repo data/ 為準，不依賴家目錄 fallback。**

### 5. 提交與推送（建議用腳本）
```bash
git add -A
git -c user.name=ontxac -c user.email=ontxac@gmail.com commit -m "feat: <description>"
bash /home/sam/.opencode/skills/push-streamlit/scripts/push.sh          # [repo目錄] [分支]
```
`push.sh` 依序執行：origin 前置檢查 → sync_topics.py 閘門 → **從 origin 推導**含 token 的推送 URL → GitHub API 驗證 token 帳號 → push。

手動推送（應急時，務必先 `git remote -v` 查證）：
```bash
TOKEN=$(cat ~/.credentials)
ORIGIN=$(git remote get-url origin)          # https://github.com/phycomp/quantum-website.git
git push "${ORIGIN/"://"/"://phycomp:${TOKEN}@"}" main
```
**禁止**：從 commit author 或目錄名拼湊 owner/repo。

### 6. Streamlit Cloud 部署
1. 前往 https://share.streamlit.io → Sign in with GitHub。
2. New app → 選擇 repo（phycomp/quantum-website）→ Branch: main → Main file: `app.py`。
3. Deploy! → 取得 URL（如 `https://<app>.streamlit.app`）。

### 6B. Hugging Face Spaces 部署（免互動、git/CLI 直推）
Spaces 用 Python SDK 跑真正的 Streamlit 伺服器，是 Streamlit Cloud 之外最省事的公開站。

```bash
pip install -U huggingface_hub      # 提供 hf CLI
hf auth login                       # token 需 write 權限（https://huggingface.co/settings/tokens）
bash /home/sam/.opencode/skills/push-streamlit/scripts/push_hf_space.sh [space名稱] [--private] [--wait] [--dry-run]
```
- 腳本行為：`whoami` → 打包 staging（`app.py` `src/` `data/` `assets/` `streamlit_stl/` `requirements.txt` `.streamlit/`；**不含** `tests/ docs/ scripts/ __pycache__/ __init__.py`）→ 產生帶 frontmatter（`sdk: streamlit`、`sdk_version`、`app_file: app.py`）的 `README.md` → `hf upload --type space`（repo 不存在會自動建立）→ 印出 Space 頁面與執行網址。
- 執行網址格式：`https://<owner>-<space>.hf.space`（owner/space 一律小寫、底線轉連字號）。
- 驗證：`curl -s -o /dev/null -w "%{http_code}" https://<owner>-<space>.hf.space/_stcore/health`（首次 build 需數分鐘；`--wait` 會 `hf spaces wait` + 輪詢 health）。
- 失敗排查：`hf spaces logs <owner>/<space>`（BUILD_ERROR／RUNTIME_ERROR 都在這裡）；`hf spaces info` 看 stage；`hf spaces restart` 重啟。
- 純驗證打包：`--dry-run`（無需登入），會停在 staging 並印出大小；可 `cd /tmp/opencode/hf-space && streamlit run app.py` 先本機確認。
- 限制：免費 CPU basic 會睡眠（訪問喚醒）；`hf.space` 在部分網路環境不可達。
- ⚠️ **2026-11-12 實測硬限制（帳號 `phycomp`，免費層）**：
  - `/api/repos/create` 的 `sdk` 只接受 `gradio|docker|static`；傳 `streamlit` → **HTTP 400 Invalid option**。
  - 傳 `docker`（或任何非 static）→ **HTTP 402**：Static Spaces are free, Gradio/Docker on cpu-basic require PRO。
  - 繞法（先 `sdk=static` 建 repo、再上傳含 `sdk: streamlit` 的 README）**能寫入 card_data**，但 runtime 停在 `PAUSED`，`errorMessage: Quota exceeded for flavor cpu-basic (requested=1): current=0, limit=0`。
  - 結論：**免費帳號無法運行 Streamlit Space**。要嘛升 PRO（升級後 `hf spaces restart <owner>/<space>` 即可上線），要嘛改用 Streamlit Cloud（免費、互動網站）＋ Kaggle Dataset（資料層）。
  - 免費 Static Space 仍可用 → 適合放「文檔鏡像」（純 HTML），但**跑不了 Streamlit**。

### 6C. Kaggle 發布（只能發 Dataset／Notebook，不能託管互動網站）
**Kaggle 不提供 Streamlit 託管** — 它只收 Notebooks / Datasets / Models。因此 Kaggle 的角色是「資料與分析層」：把 `data/` 主題蒸餾文檔發布成可引用、可被 notebook 掛載的 Dataset。

```bash
pip install -U kaggle                # CLI 2.x
# 憑證：https://www.kaggle.com/settings → API → Create New Token → 放 ~/.kaggle/kaggle.json（chmod 600）
bash /home/sam/.opencode/skills/push-streamlit/scripts/push_kaggle_dataset.sh [slug] [--public] [--stock-only] [--dry-run]
```
- 腳本行為：憑證檢查（`kaggle.json` 或 `KAGGLE_USERNAME`/`KAGGLE_KEY`，不印出 secret）→ 打包 `data/`（`--stock-only` 只打包 `data/stock_topics` 9 檔）→ 產生 `dataset-metadata.json`（CC-BY-4.0）與 `README.md` → 存在則 `datasets version -m`，否則 `datasets create`（預設 private，`--public` 公開）→ 印出 `https://www.kaggle.com/datasets/<user>/<slug>`。
- 內容免責：投資文檔一律保留「歷史績效不代表未來」。
- 若還要 Notebook（例如把台股本益比表格做成可重跑的 report），用 `kaggle kernels push -p <dir>`，`kernel-metadata.json` 需含 `id`/`title`/`code_file`/`language: python`/`kernel_type: script`/`dataset_sources: ["<user>/<slug>"]`；Notebook 執行環境**沒有持久服務**，不要期待跑起 Streamlit。
- 純驗證打包：`--dry-run`（無需憑證）。

### 7. 驗證
```bash
curl -s -o /dev/null -w "%{http_code}" <base_url>/_stcore/health   # 應為 200
```
- 若 303 redirect → 設定 Sharing 為 Public。
- ⚠️ health check 只證明 app 活著，**不證明內容完整** — 內容完整性由步驟 4 的 `sync_topics.py`（數量 + md5 驗證）保證；部署後抽查頁面主題數應等於 repo `data/` 檔數。
- 三個目標的驗證差異：Streamlit Cloud / HF Spaces 有 `/_stcore/health`；Kaggle Dataset 改用 `kaggle datasets files <id>` 核對檔案清單。

### 常見問題
- **Repository not found（push 失敗）**：owner/repo 拼錯（帳號 ≠ commit author；目錄名 ≠ repo 名）→ 用 `git remote -v` 查證實際 remote，或 token 無該 repo 權限 → 用 `curl -H "Authorization: token $(cat ~/.credentials)" https://api.github.com/user` 驗證帳號。
- **ModuleNotFoundError**：requirements.txt 缺少依賴。
- **FileNotFoundError**：使用絕對路徑 → 改為相對路徑。
- **303 redirect**：應用設為私有 → Settings → Sharing → Public。
- **Large file**：>100MB 檔案需 Git LFS。
- **HF Spaces build 失敗**：`hf spaces logs <owner>/<space>` 看日誌；常見為 `requirements.txt` 缺依賴、`README.md` frontmatter 的 `sdk_version` 過舊、或上傳到 repo 根目錄的路徑不對（`app_file` 必須是相對路徑 `app.py`）。
- **HF `hf.space` 打不開**：部分網路環境封鎖 `hf.space`（不影響 `huggingface.co`）；先用 `curl .../_stcore/health` 確認服務端，再判斷是否本地網路問題。
- **Kaggle 401/403**：`kaggle.json` 權限非 600 或 key 失效；先 `kaggle datasets list -m`（唯讀）驗證憑證。
- **Kaggle 想要互動網站**：做不到 — Kaggle 沒有持久服務；互動版留在 Streamlit Cloud / HF Spaces，Kaggle 只發 Dataset/Notebook。

### 觸發條件
- 「push streamlit」「推送網站」「streamlit deploy」「GitHub 推送」
- 「上傳到 Hugging Face」「HF Spaces」「huggingface 部署」「hf.space」
- 「上傳到 Kaggle」「kaggle dataset」「kaggle 發布」

## 除錯與解決流程 (Debugging & Resolution) — 2026-11-13

### 問題 1：push 說 "Everything up-to-date" 但遠端落後
- **現象**：`git push` 回傳 "Everything up-to-date"，但 `git log origin/main` 顯示遠端版本較舊
- **原因**：本地 `main` 分支未設定 upstream tracking branch，git 不知道要推送到哪個 remote branch
- **診斷**：`git branch -vv` 顯示 main 後面沒有 `[origin/main ...]` 追蹤資訊
- **解決**：
  ```bash
  TOKEN=$(cat ~/.credentials)
  git push --set-upstream "https://phycomp:${TOKEN}@github.com/phycomp/quantum-website.git" main
  ```
- **驗證**：`git fetch origin` 後 `git log --oneline origin/main -1` 應與本地 HEAD 一致

### 問題 2：push 說 "Repository not found"
- **現象**：`git push` 回傳 "Repository not found"
- **原因**：owner/repo 拼錯（commit author ≠ 推送帳號；目錄名 ≠ repo 名）
  - 錯誤：`ontxac/quantum_website`（author + 目錄名）
  - 正確：`phycomp/quantum-website`（token 持有者 + repo 名）
- **診斷**：`git remote -v` 查證實際 remote URL
- **解決**：從 `git remote get-url origin` 推導推送目標，不得自行拼湊
- **驗證**：`curl -H "Authorization: token $(cat ~/.credentials)" https://api.github.com/user` 確認帳號

### 問題 3：sync_topics.py 未包含新技能
- **現象**：新增的蒸餾主題 (如 2d-superconductor) 未同步到 repo
- **原因**：SYNC_PAIRS 清單未包含新技能的 references 目錄
- **診斷**：`sync_topics.py` 輸出中缺少新技能的 [OK] 行
- **解決**：在 SYNC_PAIRS 中新增條目：
  ```python
  (
      HOME / ".opencode" / "skills" / "<new-skill>" / "references",
      REPO / "data" / "<new_skill>_topics",
      "*.md",
  ),
  ```
- **驗證**：重新執行 `sync_topics.py`，確認所有 [OK] 無 [FAIL]

### 問題 4：Streamlit Cloud 未自動部署
- **現象**：git push 成功但 Streamlit Cloud 未更新
- **原因**：Streamlit Cloud webhook 未觸發，或 app 設為私有
- **診斷**：檢查 Streamlit Cloud dashboard 的 app 狀態
- **解決**：
  1. 確認 push 成功 (`git log origin/main`)
  2. 至 Streamlit Cloud dashboard 手動觸發 Reboot
  3. 檢查 Settings → Sharing → Public
  4. 驗證：`curl -s -o /dev/null -w "%{http_code}" <base_url>/_stcore/health` 應為 200

### 完整除錯流程
```
1. git remote -v                          # 確認 remote URL
2. git log --oneline -1 && git log --oneline origin/main -1  # 比較本地/遠端
3. git branch -vv                         # 檢查 tracking branch
4. sync_topics.py                         # 同步主題資料
5. git add -A && git commit -m "..."      # 提交
6. git push --set-upstream <token-url> main  # 推送 (首次需 set-upstream)
7. git fetch origin && git log origin/main -1  # 驗證推送成功
8. curl <base_url>/_stcore/health         # 驗證 Streamlit 部署
```

### 預防措施
- 每次 push 前先 `git branch -vv` 確認 tracking branch
- 使用 `push.sh` 腳本（自動處理 origin 推導 + token 驗證）
- 推送後執行 `git fetch origin` 確認遠端已更新
- 新增蒸餾主題後，先更新 sync_topics.py 再執行同步

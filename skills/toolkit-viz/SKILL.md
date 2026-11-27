---
name: 蒸餾成果展示平台
description: 統一展示所有蒸餾成果（Streamlit 網站／靜態 HTML／Markdown 索引），含技能盤點與主題儀表板，是本地/Cloud/Pages 部署的展示平台。Use when the user asks about 蒸餾成果展示、skill inventory viz、技能盤點圖表、Streamlit 展示、quantum website 展示平台、更新演示工具、開發演示工具、演示工具、開發 demo、展示工具。（註：「演示graphify」先 hook graphify 產圖，成果展示再依目標決定是否用本平台；見 Related）
---

# Skill: toolkit-viz

# Toolkit Viz Platform — 蒸餾成果展示平台

## 目標
將所有蒸餾成果（PQC、TI、塑膠分解等）統一展示，支援 Streamlit 網站、靜態 HTML、Markdown 索引三種形式，部署至本地/Cloud/Pages。

## 核心功能

### 1. 多主題儀表板
- 主題切換 (sidebar 選擇)
- 每個主題顯示：子主題清單、來源映射、arXiv 論文表、中國/台灣研究生態
- 時間軸視圖（按日期顯示蒸餾進度）

### 2. 搜尋
- 關鍵字全文搜尋所有蒸餾內容
- 跨主題搜尋

### 3. 下載
- 下載個別 md 檔案
- 下載完整主題包 (zip)

### 4. 上傳新主題
- 表單輸入：主題名 + 來源目錄 + arXiv 關鍵字
- 原 `topic-workflow-auto` pipeline 已封存；改由手動/既有流程承接

### 5. 三種輸出形式
- **Streamlit** (app.py + src/views/) — 互動式網站
- **靜態 HTML** — GitHub Pages 部署
- **Markdown 索引** — README.md

### 6. 三種部署目標
- 本地 Streamlit (localhost:8501)
- Streamlit Cloud
- GitHub Pages

## 架構

```
toolkit-viz/
├── SKILL.md
├── app.py                    # Streamlit 入口 (規則見「Streamlit 規則（SSOT）」A)
├── src/
│   └── views/
│       ├── __init__.py
│       ├── dashboard.py      # 多主題儀表板
│       ├── search.py         # 搜尋功能
│       ├── upload.py         # 上傳新主題
│       ├── timeline.py       # 時間軸
│       └── skill_inventory/  # 技能盤點展示（2026-11-25 由 showcase 移植整合）
│           ├── data.py       # 同源快照讀取（SNAPSHOT_PATH 指向 data/）
│           ├── __init__.py   # sidebar + render 入口（無折疊）
│           └── views/        # overview/types/hierarchy/uncertain/catalog
├── data/
│   ├── topics_index.json
│   └── skill_inventory_viz_data.json  # 技能盤點同源快照（只讀）
├── scripts/
│   ├── gen_static_html.py    # 靜態 HTML 生成器
│   ├── gen_markdown_index.py # Markdown 索引生成器
│   └── collect_topics.py     # 收集所有蒸餾主題
├── data/
│   └── topics/               # 主題資料 (symlink 或 copy)
└── push.sh                   # 部署腳本
```

## 資料來源 (D3.D)
1. 本地 distill 目錄 (`/tmp/opencode/distill_*`)
2. 技能 references 目錄 (`~/.opencode/skills/*/references/` 和 `~/.agents/skills/*/references/`)
3. Streamlit 網站已部署的內容 (`~/quantum_website/data/`)
4. 手動添加的主題目錄 (qalgo, quixer-quantum-transformer, em-simulation-llm, 道, etc.)

## 使用方式

### 基本啟動
```bash
cd ~/.opencode/skills/toolkit-viz
streamlit run app.py --server.port 8502
```

### 指定主題展示
當使用者說「@toolkit-viz <topic-name>」時：
1. 查詢 topics_index.json 中的對應主題
2. 若主題存在，啟動 Streamlit 並自動選取該主題
3. 若主題不存在，提示使用者並列出可用主題

```bash
# 範例：展示 em-simulation-llm 主題
streamlit run app.py --server.port 8502 -- --topic em-simulation-llm

# 或直接修改 URL 參數
http://localhost:8502/?topic=em-simulation-llm
```

### 新增主題
```bash
python3 -c "
import json
d = json.load(open('data/topics_index.json'))
d['new-topic'] = {'source': 'local', 'path': '/path/to/dir', 'md_files': [...], 'count': N}
json.dump(d, open('data/topics_index.json', 'w'), ensure_ascii=False, indent=2)
"
```

### 同步與推送
同源同步閘門與推送流程**見 SSOT.D2–D4**（唯一來源，此處不重複）。簡言之：先跑 `sync_topics.py` 閘門 → commit → `push.sh`（ token 走 GIT_ASKPASS，禁止裸 `git push` ）。

## 已整合的蒸餾主題 (43 個)
- dao-classics (6 files) — 大學、中庸、道、理、天命
- quantum-algo-qkd (8 files) — 量子算法與 QKD
- quixer-quantum-transformer (7 files) — Quixer 量子 Transformer
- em-simulation-llm (7 files) — 電磁模擬 + LLM
- qalgo (46 files) — PQC/QKD/ECC/Quantum
- ai-code-not-slop (1 file) — AI 程式碼品質
- topological-insulator (8 files) — 拓撲絕緣體
- stock-market (10 files) — 股市主題
- 🧭 技能盤點展示（skill_inventory）— 本機 173 技能盤點同源視覺化（2026-11-25 整合自 skill_inventory_showcase）
- 以及其他 35 個技能 references

## 觸發條件
- 「蒸餾成果展示」「toolkit viz」「展示平台」
- 「主題儀表板」「蒸餾索引」「toolkit index」
- 「上傳新主題」「蒸餾成果」「展示蒸餾」
- 「@toolkit-viz <topic-name>」— 指定主題展示
- 「展示 <topic-name> 主題」— 指定主題展示
- 「開發演示工具」「演示工具」「開發 demo」「展示工具」— hook toolkit-viz；依 SSOT 決定是更新既有展示 app 或建立獨立演示工具；若同時含「更新演示工具」仍走 §E 直接實作例外
- 「演示graphify」「演示 graphify 圖譜」— **先 hook `graphify`** 做 codebase/knowledge graph 的 query/path/explain 或產圖；僅當使用者明確要把成果做成 Streamlit 展示時才接本平台（見 Related 雙向鏈）
- 「更新演示工具」— 直接依 SSOT 更新 Streamlit 展示 app，免 §E 提案等待

## Streamlit 規則（SSOT）

> 本節為本機 Streamlit 展示/平台的**單一規則來源**。其他技能（topic-viz、qbit-viz 等）應引用此處，不重複抄寫規則。

### A. 架構與狀態
1. **單一入口**：`app.py` + `src/data.py` + `src/views/*` 函式模組；禁 `pages/` 與 `st.navigation`。
2. **`st.set_page_config` 只呼叫一次**，且在入口最早且唯一位置。
3. **同源快照驅動**：視圖讀同一份資料快照/來源；缺來源或相依時顯示 `errors`/降級，**不編造**。
4. **展示位置限制（使用者規則）**：量子／蒸餾成果僅展示在 `~/進化技能`（及該主题自有目錄）；**除非使用者明確要求 hook 進入 `quantum_website`，否則一律不進入、不修改 quantum_website**。理由：展示位置與部署平台分離，避免未授權觸及展示平台。此規則與 `quantum-website` 的部署 SSOT 不衝突——本檔管「展示在哪」，qw 管「如何推送部署」（見 D 節雙向指標）。
5. **相對路徑**：資產/資料用相對路徑，避免雲端路徑錯誤。

### B. 互動元件強制規則
1. **`selectbox → radio`（強制）**：所有單選/選擇控制一律用 `st.radio` / `st.sidebar.radio`，**禁止 `st.selectbox`**（不限 sidebar）。subtopics 置 sidebar `st.sidebar.radio(..., horizontal=True)`；需提供可識別標籤與穩定 `key`。
2. **直接呈現（不折疊）**：可折疊/輔助區塊一律直接呈現，或改用 `st.container`／`st.tabs`；不另做折疊包裹。
3. **`use_container_width` → `width`（強制）**：禁止 `use_container_width`。`True -> width='stretch'`，`False -> width='content'`。

### C. 版面慣例
- 左右欄：`left, right = st.columns([3, 7])`（或依情境調整）；左欄 radio 選擇，右欄內容呈現。
- 主題 sidebar + 內容區：`<name>_sidebar()` 回傳選取值，`render_*(sel)` 只渲染選定內容。

### D. 發布與同步（規則已搬移至 `quantum-website` 技能）

> Streamlit 展示平台的推送／部署規則已於 2026-11-26 完整搬移至 `~/.opencode/skills/quantum-website/SKILL.md` D1–D7（repo 事實卡、同源同步閘門、Git／credentials、提交推送、三部署目標、驗證、除錯）。本節不再維護第二份規則；`push-streamlit` 為 deprecated_keep thin alias，5 支 scripts 保留原路徑供新技能引用。

### E. 寫入前 Gate（Streamlit 展示 app）
> 當任務需要寫入/修改 `app.py` 或 `src/views/*`（Streamlit 展示）時，必須先完成此 gate。

> **例外（直接實作觸發）**：使用者原話含「更新演示工具」時，視為已明確裁決同意——直接實作，免提案、免等待；仍須遵守 A–D 強制慣例，並於交付提出驗證證據（`py_compile`／grep／同源一致性）。使用者原話僅含「開發演示工具」「演示工具」「開發 demo」「展示工具」時，hook toolkit-viz 進行路由與規格釐清；「演示graphify」則先 hook graphify 產圖（見 §觸發條件），成果展示需求再回到本平台；若目標是修改既有 Streamlit 展示 app 且未含「更新演示工具」，仍走下列 1–3；若目標是建立獨立演示工具，依該工具目標位置的技能/開發流程執行。

1. **先提案（僅對話，不落檔）**：給出四欄位 prompt 建議：(a) `app.py + src/data.py + src/views/*` 架構；(b) 上述 A/B/C 強制慣例逐條；(c) 同源資料路徑與讀取方式；(d) 驗證方式（`py_compile` / `streamlit run` / 同源一致性 / `errors` 降級）。
2. **停止並等待明確裁決**：提案訊息結尾逐字宣告：「尚未寫入任何檔案、未 hook @toolkit-viz，等待你的明確裁決。」不得同回合寫檔。
3. **明確裁決同意後才實作**：使用者在看過提案後的新訊息中，明確針對本次提案給出肯定（同意/可以/照辦/開始寫/就照這個）才可寫入。沉默、先前授權、「你判斷就好」、「先不 hook」等均不算同意。

## Related（上下級雙向鏈）
- **上級**：`viz-router`（viz 家族 parent，goal→hook；本平台為其「開發演示工具／展示平台」目標的承接者之一）。
- **同級／方法**：`topic-viz`（方法論 A–G 與 Streamlit 慣例；本平台為其格式 F 的平台層實例，雙向互引）。
- **雙向指標**：`graphify`（codebase knowledge graph：query/path/explain/產圖）。「演示graphify」先 hook graphify；其成果若要做成 Streamlit 展示再接本平台。graphify 的 Related 段亦回指本平台。
- **部署 SSOT**：`quantum-website`（推送／部署 D1–D7；本檔 D 節只留指標，qw 回指本檔 SSOT.A.4）。

## 鐵律
1. 本檔「Streamlit 規則（SSOT）」為規則真相來源；其他技能只引用不複製。
2. 其餘強制規則（架構／元件／版面／寫入 Gate）以「Streamlit 規則（SSOT）」A–E 為準；**推送／部署以 `quantum-website` 技能為唯一來源（本檔 D 節只留指標）**，本節不重複。

Logic check: 2026-11-25 — 整合舊副本：刪除 `~/軟體/代理人/.agents/skills/toolkit-viz/`（其 5 條鐵律全部為本檔 SSOT 子集，無獨特規則）；精簡重複：`app.py` 架構註解改指向 SSOT.A、`鐵律 2–4` 併入 SSOT.D。Streamlit 規則真相來源單一化。
Logic check: 2026-11-25 (rev-skill / B2 完全移除) — 依使用者裁決 Scope A，skill 內所有「展開式元件」字串與用法完全清除：B2 改為「直接呈現（不折疊）」、`app.py` 搜尋結果改直接 `st.markdown`、Logic check 與測試改寫（舊測試檔移除、新檔 `tests/test_b2_direct_render.py`）。Gate 0 explicit consent（完整 rev）；Gate 1 pre2 報告 `toolkit-viz-pre2-20261125-105146.md` + manifest `toolkit-viz-pre2.sha256`；Gate 2 RED 3 項失敗 exit=1；Gate 3 GREEN 最小修正。前一版「禁用」規則字串亦一併清除。quantum_website 不在寫入範圍。
Logic check: 2026-11-25 (U / 整合 skill_inventory_showcase) — 依使用者明確裁決，把 `~/skill-inventory-viz/skill_inventory_showcase/` 整合入本 skill：來源取已去折疊、相對 import 已修復的 `quantum_website/src/views/skill_inventory/` 移植版（非含 9 處 expander 的原 showcase），落點 `src/views/skill_inventory/` + `data/skill_inventory_viz_data.json`；`app.py` 頂層加「展示模式」radio（SSOT.B.1）分派蒸餾主題／技能盤點。符合 SSOT A/B/C（無 pages、無 selectbox、無 expander、use_container_width→width）。`skill_inventory_showcase` 標 deprecated（thin pointer），其 spec 與 task-changelog 同步。Gate 0 explicit consent；Gate 1 pre manifest `toolkit-viz-pre.sha256`；Gate 2 RED 4/4；Gate 3 GREEN；Gate 5 re-audit + drift。SSOT A–E 規則文字不改（只引用）。
Logic check: 2026-11-25 (rev-skill / A4) — 依使用者明確裁決移除 A4「`__init__.py` 同步：若支援 `streamlit run __init__.py`，保持與 `app.py` 一致」。理由：本機 repo 已無 `app.py`（`__init__.py` 為唯一入口），且 `push-streamlit` 打包明確排除 `__init__.py`，symlink 或內容同步要求均已過時；A5「相對路徑」遞補為 A4。Gate 1 `toolkit-viz-pre3.sha256`；Gate 2 RED `tests/test_no_init_sync_rule.py` 4 項失敗 exit=1；Gate 3 GREEN。`topic-distill/SKILL.md:35` 仍有同類「`__init__.py` 同步」字串，屬另一技能規則，本輪未改。
Logic check: 2026-11-25 (rev-skill / push-streamlit 合併) — D 節擴為部署唯一來源（repo 事實卡／sync 閘門／push-repo hook／push.sh／三部署目標／驗證／除錯），合併 push-streamlit v1.3.1；既有 Known Issues 與預防措施已併入 D7 並移除；未重新引入 `__init__.py` 同步規則（見前筆 A4 移除）。push-streamlit 降為 deprecated_keep alias，交叉引用同步至 toolkit-viz D。Gate 1 `toolkit-viz-pre4.sha256`；Gate 2 RED `tests/test_deployment_merge.py` 7 項失敗 exit=1；Gate 3 GREEN。
Logic check: 2026-11-25 (U / 去除 4 處冗餘規則) — 核實後移除：(1)「同步至 quantum_website repo」段的 `sync_topics.py` 指令重複（與 SSOT.D2 同指令，改為「見 SSOT.D2–D4」引用）；(2) 裸 `git commit && git push`（繞過 D3 GIT_ASKPASS／D4 push.sh，改 hook 引用）；(3) 整合進來的 `src/views/skill_inventory/__init__.py` docstring 重述 SSOT 規則（改為「見 SKILL.md，此處不重複」）；(4) `data.py` 舊 showcase 路徑註解（改為 toolkit-viz 新路徑）。SSOT A–E 規則本體、定義+引用型重複（GIT_ASKPASS／sync_topics／同源快照）、Logic check 歷史記錄均未動。Gate 1 `toolkit-viz-dedup-pre.sha256`；Gate 2 RED `tests/test_no_redundant_rules.py` 4/4 失敗；Gate 3 GREEN 4/4。
Logic check: 2026-11-25 (rev-skill / 更新演示工具觸發) — 依使用者明確裁決新增「更新演示工具」為直接實作觸發字眼：§觸發條件登錄、§E 加例外（免提案、免等待，仍遵守 A–D 與驗證）；其餘語句仍走原 1–3 gate。Gate 0 explicit consent；Gate 1 pre 報告 `toolkit-viz-trigger-pre-20261125-153813.md` + manifest `toolkit-viz-trigger-pre.sha256`（CAUTION：既有 `scripts/gen_markdown_index.py` 的 `__import__('datetime')` finding，白名單排除 `scripts/`，不屬本輪範圍）；Gate 2 RED `tests/test_update_demo_trigger.py` 5 項失敗 exit=1；Gate 3 GREEN 最小修正，只動 `SKILL.md` 與新測試。
Logic check: 2026-11-25 (rev-skill / 索引註冊改預設不註冊) — 依使用者裁決，SSOT.D2 原「`topics_index.json` 必須包含所有蒸餾主題」改為「`data/topics_index.json` 預設不註冊新主題；僅明確指出才註冊；獨立演示工具直接讀蒸餾來源目錄」。app.py 規則與 `toolkit-viz/app.py` 實體檔均不改（使用者明確「不去除 app.py」）；索引檔案內容未新增《大學》條目；`quantum_website` 未觸碰。Gate 1 pre manifest `toolkit-viz-rule-cleanup-pre.sha256`；Gate 2 RED `tests/test_topic_index_default_no_register.py` 4/5 失敗；Gate 3 GREEN 只動 `SKILL.md`。

Logic check: 2026-11-26 (rev-skill / quantum-website 規則搬移) — 依使用者四項裁決，SSOT.D1–D7 完整搬移至新建 `~/.opencode/skills/quantum-website/`，本檔 D 節只留一行指標；4 行 2026-11-25 `Logic check:` 歷史與 `app.py` 實體檔原樣保留；跨技能現行引用同步指向 `quantum-website`，歷史字串不改。Gate 0 explicit consent；Gate 1 pre manifest `toolkit-viz-qw-move-pre.sha256`；Gate 2 RED `tests/test_quantum_website_rule_move.py` 48 項失敗 exit=1；Gate 3 GREEN；Gate 4 清快取；Gate 5 re-audit + drift 白名單外不變。

Logic check: 2026-11-26 (rev-skill / __init__.py 物理移除) — 依使用者裁決延續方案 1：以 git 移除 quantum_website 根目錄 `__init__.py`，達成只剩 `app.py` 的物理上唯一入口；移除 `app.py` 同步 docstring 與過時 `pages/app.py` 註解、`tests/test_structure.py` 的 `test_entrypoints_in_sync()` 與根 `__init__.py` compile，`topic-distill` 鐵律 4 的「`__init__.py` 同步」字串同步清除。`streamlit_stl/__init__.py` 與 `src/views/__init__.py` 為套件檔，保留。SSOT A1/D5 與本檔 A4 現行規則一致，規則本體不改；`quantum-website` 技能同步新增追溯行。Gate 0 explicit consent（使用者回覆「是的」同意精確 guardrails）；Gate 1 pre manifests：`toolkit-viz-initcleanup-pre.sha256`、`topic-distill-initcleanup-pre.sha256`、`quantum-website-initcleanup-pre.sha256`（toolkit-viz CAUTION：既有 `data/skill_inventory_viz_data.json` 6 HIGH，白名單排除）；Gate 2 RED `/tmp/opencode/test_init_cleanup_red.py` 9/14 失敗 exit=1；Gate 3 GREEN 最小修正；Gate 4 清快取；Gate 5 re-audit + drift。

Logic check: 2026-11-27 (rev-skill / 演示工具觸發 hook) — 依使用者明確指令「更新規則 觸發『開發演示工具、演示工具』就hook toolkit-viz」，擴充 frontmatter description 與 §觸發條件，新增「開發演示工具、演示工具、開發 demo、展示工具」→ hook toolkit-viz；§E 補充僅含演示工具觸發時的路由：改既有展示 app 未含「更新演示工具」仍走提案 gate，獨立演示工具依目標流程執行。未改 SSOT A–D 規則本體。Gate 0 explicit consent（使用者本輪明確要求更新規則）；Gate 1 pre 本輪未重跑完整 audit-skill 報告（既有 CAUTION 歷史：`data/skill_inventory_viz_data.json` finding 已記錄）；Gate 2 RED：觸發字串缺失（本次對話前確認）；Gate 3 GREEN：最小 SKILL.md 修正；Gate 4/5 後續由 re-audit 補齊。

Logic check: 2026-11-27 (rev-skill / 展示位置規則入 SSOT.A.4) — 依使用者「更新規則 入 toolkit-viz」＋「檢查上下鏈」，於 SSOT.A 新增 A.4「展示位置限制（使用者規則）」：量子／蒸餾成果僅展示 `~/進化技能`，非明確要求不進 `quantum_website`；原 A.4 相對路徑順延為 A.5。SSOT B–E 規則本體不改。上下鏈雙向對帳通過：toolkit-viz D 節 → qw 唯一部署 SSOT；qw 上下層級表 → 本檔 SSOT.A.4 指標（展示位置在本檔、部署在 qw）。Gate 0 explicit consent；Gate 1 pre 報告 `toolkit-viz-displayloc-pre-20261127-162948.md`（69/100 HIGH 185 findings：6 HIGH PE3 全在 data/ 快照、176 MEDIUM AS3 在 data/，均白名單排除，本輪只改 SKILL.md）+ `quantum-website-displayloc-pre`（11/100 LOW）；Gate 2 RED（展示規則 0 處）；Gate 3 GREEN 最小修正；Gate 4 清快取；Gate 5 re-audit（findings 數不變）+ drift 兩邊皆只 SKILL.md；verdict toolkit-viz CAUTION（白名單 triage）/ qw APPROVE。

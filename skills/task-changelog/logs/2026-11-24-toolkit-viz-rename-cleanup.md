# 2026-11-24 — distill-showcase --> toolkit-viz 改名殘留清理（含視頻展示線同步）

## distill-showcase --> toolkit-viz 改名殘留清理（含視頻展示線同步）

- **日期**：2026-11-24
- **類型**：refactor + docs
- **涉及技能/檔案**：
  - `/home/sam/.opencode/skills/toolkit-viz/`（原 distill-showcase，已改名）— SKILL.md / app.py / scripts/* / data / src
  - `/home/sam/軟體/代理人/.agents/skills/toolkit-viz/`（原 distill-showcase 副本，已改名）— SKILL.md / app.py / scripts / data / src
  - `/home/sam/.venvs/toolkit-viz/`（原 distill-showcase venv，已改名）
  - `/home/sam/em-simulation-llm/00_索引.md`
  - `/home/sam/heatload_research/`（docs / scripts / md）
  - `/home/sam/quantum-algo-qkd/00_索引.md`
  - `/home/sam/量傳線/`（docs / scripts / md）
  - `/home/sam/skill-inventory-viz/`
  - `/home/sam/物理模擬/topo/floquet/`（docs / scripts / floquet_showcase）
  - `/home/sam/quixer-quantum-transformer/00_索引.md`
  - `/home/sam/道/00_索引.md`
  - `/home/sam/quantum_website/data/qalgo_topics/QALGO_INDEX.md`、`/home/sam/quantum_website/data/quixer_topics/00_索引.md`
  - `/home/sam/quantum_website/src/views/toolkit_viz.py`（原 distill_showcase.py，已改名）

### 變更摘要
1. 主 skill 目錄 `distill-showcase` → `toolkit-viz`；frontmatter name / title / 架構樹 / `@toolkit-viz` / 觸發詞（`toolkit viz`、`toolkit index`）全數同步。
2. 殘留副本（軟體代理人）與 venv 同步改名並同步內部引用。
3. 跨專案殘留引用批量替換（em-simulation-llm、heatload_research、quantum-algo-qkd、量傳線、skill-inventory-viz、floquet、quixer-quantum-transformer、道、quantum_website data topics）。
4. 網站 module 由 `distill_showcase.py` 改名為 `toolkit_viz.py`，內部自引用（顯示文案 / helper / render / search key）改寫；`py_compile` PASS。

### 驗證結果
- Python：14 個修改後檔案 `py_compile` 全數 PASS（toolkit-viz app+scripts、heatload_research / 量傳線 showcase scripts、floquet app、quantum module）。
- 舊名殘留掃描：排除 runtime / git / session / 歷史文件後，最終殘留命中轉清（4 真實檔替換；module 改名；git log 與 runtime 排除）。

### 上下級鏈影響
- 無（展示平台重命名清理；不動 heatload 技能鏈）。

### 待辦／已知限制
- `/home/sam/量傳線/.superpowers/sdd/...` 為歷史任務文件，未改寫。
- 舊 streamlit 背景程序（cwd 已改名）未止。

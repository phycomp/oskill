# 2026-11-18 — 熱負載技能重命名與引用同步

## thermal-* 技能重命名為 heatload-* + 全引用同步

- **日期**：2026-11-18
- **類型**：refactor
- **涉及技能/檔案**：
  - `/home/sam/.opencode/skills/thermal-coff-nist/` → `heatload-coff-nist/` — v1.0.0 → v1.1.0
  - `/home/sam/.opencode/skills/thermal-load-measurement/` → `heatload-measurement/` — v1.0.0 → v1.1.0
  - `/home/sam/.opencode/skills/thermal-load-simulation/` → `heatload-simulation/` — v1.0.0 → v1.1.0
  - `/home/sam/.opencode/skills/thermal-load-sop/` → `heatload-sop/` — v1.0.0 → v1.1.0
  - `/home/sam/.opencode/skills/thermal-load-units/` → `heatload-units/` — v1.0.0 → v1.1.0
  - `/home/sam/軟體/代理人/.agents/skills/thermal-load-{measurement,simulation,sop,units}/` → `heatload-*/` — 4 目錄（副本無 version 欄，略過）
  - `/home/sam/.opencode/skills/qcable-index/SKILL.md` — v1.2.0 → v1.3.0（熱負載鏈節點與表格、description/觸發詞同步）
  - `/home/sam/.opencode/skills/heatload-coff-nist/MANIFEST.sha256` — 重算並驗證
  - `/home/sam/.opencode/skills/task-changelog/logs/2026-11-18-thermal-load-chain.md` — 加更名註記（保留歷史真相）
  - 其餘引用同步檔：qcable-usage、topic-seek、qbit-arch、physim-topics（含 `quantum_website/data/physim_topics/`）、topological-insulator、kpi-delivery-valid、`物理模擬/topics/`、`量子/`、`quantum_website/`、創新商模/MYC-15、`軟體/代理人/REFACTOR_MANIFEST.md`、KPI/pipeline 文件、`docs/`、`examples/`、`quantum_mindmap.svg`、`量傳線/qcable_dep.svg`

### 變更摘要

1. **使用者決策**：前綴用 `heatload-`（語義正確，非 `headload`）；整段 `thermal-load-` → `heatload-`（避免 `heatload-load-` 重複）；主目錄與 `軟體/代理人/.agents/skills/` 副本兩份都改；所有技能名引用全部同步。
2. **新舊名對照**：
   - `thermal-coff-nist` → `heatload-coff-nist`
   - `thermal-load-measurement` → `heatload-measurement`
   - `thermal-load-simulation` → `heatload-simulation`
   - `thermal-load-sop` → `heatload-sop`
   - `thermal-load-units` → `heatload-units`
   - 通用 glob `thermal-load-*` → `heatload-*`
3. **目錄重命名**：主目錄 5 個 + 副本 4 個，共 9 個；未刪除任何技能內容。
4. **引用同步**：對 48 個檔案做精確字串替換，共 180 處（含 frontmatter `name:`、description、內文、觸發條件、qcable-index 的 linked-list 鏈圖與表格、task-changelog 五檔、heatload-coff-nist 內部路徑與 docstring，以及 KPI/docs/examples/mindmap/SVG/physim/創新商模/REFACTOR_MANIFEST 等引用）。
5. **版本號**：被改名的 5 個主 SKILL.md v1.0.0 → v1.1.0；qcable-index v1.2.0 → v1.3.0；副本無 version 欄故略過。
6. **MANIFEST**：在 `heatload-coff-nist/` 以 `sha256sum` 重算 6 個原始檔（沿用原 Manifest 結構，排除 `scripts/__pycache__` 快取），並以 `sha256sum -c` 驗證。
7. **歷史日志**：`logs/2026-11-18-thermal-load-chain.md` 內技能名同步為新名，並於 H2 後加註更名說明，保留「為何那時叫 thermal-」的來龍去脈。

### 驗證結果

- 目錄重命名：PASS（9 個 heatload-* 存在、無 thermal-* 殘留目錄；主目錄 5 + 副本 4）
- frontmatter name：PASS（5 個主技能 name 值等於目錄名）
- 版本號：PASS（heatload-* 皆 1.1.0、qcable-index 1.3.0）
- 技能名殘留：PASS（僅 task-changelog 3 檔命中，皆為更名註記／新舊對照，刻意保留）
- 雙前綴 heatload-load-：PASS（僅「避免重複」說明字串，無實際雙前綴技能名）
- MANIFEST：PASS（sha256sum -c 6/6 成功）
- qcable-index 鏈：PASS（linked-list 7 節點全用新名、表格／觸發詞一致）
- 日誌一致性：PASS（新舊對照完整、驗證欄如實、三處標題逐字一致、與展示整合條目並存排序正確）
- 核實方式：reviewer（ses_e13781672ffeX2FfNgStFo4v8W）實跑 8 項檢查全數 OK

### 上下級鏈影響

- 上級 ← 論文/NIST 出處（不變）
- 本級·計算 ← `heatload-coff-nist`（9 係數，有 upper 出處）、`heatload-simulation`（示意模型）
- 下級 → Excel 產出 → `heatload-measurement` → `heatload-units` → `heatload-sop`
- `qcable-index` 鏈圖與表格的 `← 上級 / 下級 →` 語意不變，僅節點名更新。

### 待辦／已知限制

- 內部模組/檔案名保留未改（非技能名）：skill 內 `scripts/thermal_load.py`、`scripts/coeff_data.py`、函式 `calculate_thermal_load`；平台側函式 `calculate_coupled_thermal_load`（`軟體/代理人/計算.py`）亦未改動；改動會破壞 import，使用者未要求。
- 物理術語與一般文字保留原文：thermal load、熱負載、thermal conductivity、κ(T)、`thermal conductivity fitting coefficients` 等。
- 歷史日志檔名 `logs/2026-11-18-thermal-load-chain.md` 與 `format.md` 中的 slug 範例保留（`thermal-load-chain` 是 slug 不是技能名）。
- `scripts/__pycache__/*.pyc` 為生成快取，不納入 MANIFEST（與原 Manifest 一致）。
- 副本技能檔無 version 欄位，未額外新增。

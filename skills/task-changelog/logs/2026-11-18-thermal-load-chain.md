# 2026-11-18 — 熱負載技能鏈重構與常態日誌機制

## 熱負載技能上下級鏈重構 + 新建 heatload-coff-nist + 建立 task-changelog 常態日誌機制

> **更名註記**：本日志記錄的是 2026-11-18 當日的重構事件，當時技能名為 `thermal-coff-nist` / `thermal-load-*`（熱負載 = thermal load，故原名如此）；（技能已於 2026-11-18 更名：thermal-coff-nist→heatload-coff-nist、thermal-load-*→heatload-*）。以下內文已同步為新名，原名保留於本註記以保存來龍去脈。

- **日期**：2026-11-18
- **類型**：refactor + feature
- **涉及技能/檔案**：
  - `/home/sam/.opencode/skills/qcable-index/SKILL.md` — v1.1.0 → v1.2.0（熱負載區塊重構為 linked-list 上下級鏈，新增 heatload-coff-nist 於「本級·計算」節點，更新 description/觸發詞）
  - `/home/sam/.opencode/skills/heatload-coff-nist/` — 新建（6 主檔 + MANIFEST：`SKILL.md`、`scripts/coeff_data.py`、`scripts/thermal_load.py`、`references/coefficient_table.md`、`references/coefficient_table.csv`、`references/citations.md`、`MANIFEST.sha256`）
  - `/home/sam/.opencode/skills/task-changelog/` — 新建（本 skill：常態日誌機制）

### 變更摘要

1. **溯源**：熱負載技能無單一父論文；確認通用 Fourier / Wiedemann-Franz 定律，以及 Raicu et al. 2025 (EPJQT 12:124, doi:10.1140/epjqt/s40507-025-00427-1) / NIST Cryogenic DB / NIST Monograph 177 / Flynn 教科書為公式與 9 係數來源。
2. **下游**：找到 Excel 產出路徑（`量傳線/熱負載/積分係數.py` → `Quantum_Microwave_Stripline_Thermal_Calculator.xlsx`；`pages/10建立xlsx.py` → `功能.xlsx`）；發現 `thermal_load.py` 的 `sys.path` 失效 bug（指向 `/home/sam/代理人`，實際在 `/home/sam/軟體/代理人`）— 僅記錄，未修改既有檔。
3. **9 係數**：8 階多項式 `c0..c8`（log-log 形式 κ(T)=10^Σ ci·(log10T)^i）；4 組權威出處（Raicu Table 4 三組 + Table 6 電阻率一組）+ NIST 48 材料 + 2 組自推導（Kapton 有值；NbTi 為執行期 polyfit 無固定值 → 表中標 N/A）。
4. **新技能 heatload-coff-nist**：54 材料單一對照表（md + csv）、計算引擎（9 係數 + rational_copper + 多溫區積分 + 衰減器熱 + CLI `--list`）、`citations.md`、`MANIFEST.sha256`（6 檔 `sha256sum -c` 全通過）、安全自檢 APPROVE。
5. **索引重構**：`qcable-index` 熱負載鏈 = 上級出處 → heatload-coff-nist → heatload-simulation → Excel 產出 → measurement → units → sop，雙向交叉引用。
6. **建立 task-changelog 常態日誌機制**（本 skill）：單一真相來源（每日一檔 + 索引 + CHANGELOG），並寫下本筆第一筆日誌。

### 驗證結果

- reviewer 實跑核實 — 鏈一致性：PASS
- 交叉引用：PASS
- 本體完整性：OK
  - 對照表 54 列
  - CLI `--list` 列出 54 項
  - `sha256sum -c` 6 項全成功
  - DOI / NIST URL 齊全
  - NbTi N/A 如實揭露

### 上下級鏈影響

- 上級 ← 出處（Fourier / Wiedemann-Franz、Raicu 2025、NIST Cryo DB、NIST Monograph 177、Flynn）
- 本級·計算 ← 新增 `heatload-coff-nist`（54 材料 9 係數對照表 + 計算引擎）
- 下級 → `heatload-simulation` → Excel 產出 → `heatload-measurement` → `heatload-units` → `heatload-sop`
- 雙向交叉引用：`qcable-index` ↔ 各熱負載節點；`heatload-coff-nist` ↔ 上級出處與下級模擬/量測

### 待辦／已知限制

- NbTi 9 係數在原始檔為執行期 `polyfit` 動態生成，無固定數字；對照表標 N/A，引擎要求以 `coeffs=[...]` 自傳。
- `thermal_load.py` 的 `sys.path` 指向 `/home/sam/代理人`（實際在 `/home/sam/軟體/代理人`）— 本次僅記錄，未修改既有檔，待後續 fix 處理。
- 本次未觸碰 `/home/sam/量傳線/` 任何檔案；僅新建技能與日誌。

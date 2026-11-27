# 2026-11-18 — 熱負載展示整合

## heatload-coff-nist 蒸餾展示整合（論文出處/資料庫/計算 Excel）

- **日期**：2026-11-18
- **類型**：feature
- **涉及技能/檔案**：
  - `/home/sam/.opencode/skills/toolkit-viz/app.py` — 修改（新增附加檔案下載區）
  - `/home/sam/.opencode/skills/toolkit-viz/data/topics_index.json` — 重建（collect_topics.py）
  - `/home/sam/.opencode/skills/heatload-coff-nist/references/00_熱負載總覽.md` — 新建
  - `/home/sam/.opencode/skills/heatload-coff-nist/references/Quantum_Microwave_Stripline_Thermal_Calculator.xlsx` — 新建
  - `/home/sam/量傳線/熱負載/積分係數.py` — 唯讀執行（未修改）

### 變更摘要
1. 產出計算 Excel：於 `heatload-coff-nist/references/` 執行下游 `/home/sam/量傳線/熱負載/積分係數.py`（`/home/sam/flex/bin/python`，openpyxl 3.1.5），生成 `Quantum_Microwave_Stripline_Thermal_Calculator.xlsx`。
2. 新建展示入口 md：`references/00_熱負載總覽.md`，條列三類檔案——論文出處（Raicu et al. 2025, EPJQT 12:124, doi:10.1140/epjqt/s40507-025-00427-1；Zenodo doi:10.5281/zenodo.15238913；NIST Cryogenics DB；Flynn 教科書）、資料庫（54 材料 9 係數 c0..c8、log-log κ(T) 模型與溫度範圍，`coefficient_table.md` / `.csv`）、計算 Excel（下游 積分係數.py 產出，含幾何參數輸入與熱負載/長度回推公式）。
3. 最小增強 `toolkit-viz/app.py`：在 right 區塊 md 下載之後，動態掃描主題 `path` 下的 `*.xlsx` / `*.xls` / `*.csv`，以 `st.download_button` 提供二進位下載（xlsx 用 spreadsheet mime、csv 用 text/csv、其餘 octet-stream，key 為 `xdl_<name>`）；無附加檔案則不顯示。既有 md 呈現/搜尋/側欄 logic 未動，`st.set_page_config` 仍只呼叫一次。
4. 重建索引：執行 `scripts/collect_topics.py`，共收集 41 個主題；`heatload-coff-nist` 為 `source=skill`、`count=3`、`md_files` 含 `00_熱負載總覽.md` / `citations.md` / `coefficient_table.md`，`path` 指向 `.../heatload-coff-nist/references`（xlsx 與 csv 由 app 動態掃描取得）。
5. 確認執行環境：`/home/sam/flex/bin/python` 提供 streamlit 1.57.0；建議以此 python 啟動 `streamlit run app.py --server.port 8502`。

### 驗證結果
- xlsx：PASS — openpyxl 成功開啟，sheet `Thermal Calculator`，21 列 × 8 欄，檔案 6456 bytes（reviewer 實跑複核一致）。
- 總覽 md：PASS — Raicu doi:10.1140/epjqt/s40507-025-00427-1、NIST、Flynn、54 材料 9 係數、`功能.xlsx` 未納入說明五項俱在。
- app.py 加法式改動：PASS — `py_compile` OK；`set_page_config` 僅 1 處；動態掃描 `*.xlsx`/`*.xls`/`*.csv`、key `xdl_<name>` 唯一、既有 md/搜尋/側欄 logic 未動。
- 索引條目：PASS — `source=skill` / `count=3` / md_files 三項 / path 正確（reviewer json 實讀一致；索引實為 41 key，與日誌自洽）。
- 服務與功能複核：PASS — `setsid` 啟動 `localhost:8502`，health HTTP 200 + listener 存在；AppTest 以 `?topic=heatload-coff-nist` 渲染 0 exception、radio 預選正確、**3 個下載按鈕**（md/xlsx/csv）、「附加檔案（Excel / CSV）」子標題出現。
- streamlit：OK — flex 環境 1.57.0；系統 `python3` 無 streamlit（ModuleNotFoundError）。
- 核實方式：reviewer（ses_e137c9fafffeDM6NbMqM4Bh8IG）四面向查證 + router 服務/AppTest 獨立複核（補 reviewer 查證當下服務未啟動之差，重新以 setsid 啟動後通過）。

### 上下級鏈影響
- 無（展示平台整合，不動 heatload 技能鏈）。

### 待辦／已知限制
- `功能.xlsx` 由 Streamlit 多頁應用 `pages/10建立xlsx.py` 產生，依賴 `session_state` 與多個 import 模組，無法獨立產出，故未納入展示。
- 服務【啟動】由 router 負責；本任務僅完成準備並回報 python 路徑。

# 2026-11-18 — POI 展示排除已停業餐廳

## 已停業素食餐廳不列入總覽卡與 contact sheet

- **日期**：2026-11-18
- **類型**：fix + docs
- **涉及技能/檔案**：
  - `/home/sam/渲染邏輯/img2svg/景點資訊卡.py` — 修改（過濾停業餐廳、移除卡片「已停業」標記與行前提醒停業那行）
  - `/home/sam/渲染邏輯/img2svg/圖至SVG.py` — 修改（OverviewRenderer 渲染時過濾 `dining` id）
  - `/home/sam/渲染邏輯/img2svg/contact_sheet.py` — 修改（新增 `--exclude`、保留 `item_id`）
  - `/home/sam/poi-showcase/card/台北植物園.svg` / `.png` / `manifest.json` — 重產
  - `/home/sam/poi-showcase/overview/overview.svg` / `.png` / `manifest.json` / `contact-sheet.png` — 重產
  - `/home/sam/poi-showcase/README.md` — 更新數字與說明

### 變更摘要

1. **需求**：已停業的「三個傻瓜 印度蔬食」（`three-idiots`，特色含「已停業（2026/11/30）」）不列入餐點資訊。使用者選擇「總覽卡 + contact sheet 都移除」。
2. **保留完整紀錄**：`data/pois.json` 的該筆資料與 `svg/restaurants/three-idiots.svg` 皆不刪除（先前刻意保留的決定僅限資料完整性，此次覆蓋展示面）。
3. **渲染時過濾**（不改資料、不碰 `svg/`）：
   - `景點資訊卡.py` 的 `dining` 用 `field(i,"特色")` 過濾含「停業」者；移除卡片上的「已停業」紅標區塊；行前提醒移除手寫的停業那行。
   - `圖至SVG.py` 的 `OverviewRenderer` 對 `ov["dining"]` 的 id 以 `_item_of(food,did)` 的「特色」過濾；`len(diners)` 自動從 4 → 3。
   - `contact_sheet.py` 新增 `--exclude three-idiots`（逗號分隔 id），在 `build_entries` 後過濾；`build_entries` 保留 `item_id`（manifest 與 fallback 兩路徑）；頁首/頁尾的「N 個檔案 / N files」原已用 `len(entries)`，自動 15 → 14。
4. **重產成品**：card 1080×1907 → **1080×1787**（少一間餐廳 72px + 一行提醒 48px），素食 4 → 3 間；overview 尺寸不變、素食 3 間；contact sheet 15 → 14 格（5×3，末格留白，2092×1200）。
5. **文件同步**：README 更新素食數、格數、card 高度、見解說明、所有驗證數字與「已知注意事項」的停業註記。

### 驗證結果（數值，未讀圖）

- 景點資訊卡：XML well-formed；`viewBox 0 0 1080 1787`；6,116 `<path>`；16 個 `<g>` transform 全保留；截圖尺寸 (1080,1787)；平均色差 **3.34/255**、差異 **3.1%**；最長空白帶 61px=3.4%；38 處文字寬度檢查全過；內容外框 x72–1008 / y60–1725 四邊無裁切 — **PASS**
- Overview：PNG 與程式重建卡逐位元相同（max diff 0）；截圖 (1080,1440)；平均色差 **3.19/255**、差異 **2.9%**；最長空白帶 146px=10.1%（門檻 15%，少一列素食後變大仍通過）— **PASS**
- Contact sheet：14/14 格非空白；`--exclude` 排除 1 項 `three-idiots`；尺寸 2092×1200
- 過濾正確性：card 與 overview 的 dining 過濾後皆為 `[liande, fanshuteng, hejia]`；`three-idiots` 仍在 `data/pois.json`
- 回歸：`git diff -- svg/` 與 `git diff -- data/pois.json` 皆為空（原始 15 張 SVG 與資料未動）
- `py_compile` 三個產生器全通過

### 上下級鏈影響

- 上游 ← `data/pois.json`（唯一資料來源，未修改）
- 下游 → 兩張展示卡 + contact sheet（已過濾）；`svg/` 獨立卡不受影響
- 工具鏈：`圖至SVG.py` 的 `vectorize_image()` 仍為 card 與 overview 共用的 K-Means + Potrace 流程，本次僅改文字層清單

### 待辦／已知限制

- 產生器（`渲染邏輯/img2svg/`）在 `/home/sam` 為 untracked，本來就不在 `phycomp/poi-showcase` repo 內（repo 只收資料與成品）；此次過濾邏輯改動不會進 repo，僅成品進 repo。
- worker subagent 連續三次誤報完成且未寫檔，本次改由主代理直接操作並逐項驗證。

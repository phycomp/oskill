# 2026-11-25 — 整合 skill_inventory_showcase 入 toolkit-viz 並標 deprecated

## 技能盤點展示入口收斂至 toolkit-viz，原 showcase 降為 thin pointer

- **日期**：2026-11-25
- **類型**：feature + refactor + docs
- **涉及技能／檔案**：
  - `~/.opencode/skills/toolkit-viz/src/views/skill_inventory/`（新建，5+ 檔：data.py／__init__.py／views×5）
  - `~/.opencode/skills/toolkit-viz/data/skill_inventory_viz_data.json`（新建，同源快照副本）
  - `~/.opencode/skills/toolkit-viz/app.py`（修改，頂層「展示模式」radio 分派）
  - `~/.opencode/skills/toolkit-viz/SKILL.md`（修改，架構樹／已整合主題／Logic check）
  - `~/.opencode/skills/toolkit-viz/tests/test_skill_inventory_integration.py`（新建，RED/GREEN 驗收）
  - `/home/sam/skill-inventory-viz/skill_inventory_spec.md`（修改，第八節加 deprecated 註記）
  - `/home/sam/skill-inventory-viz/skill_inventory_showcase/DEPRECATED.md`（新建，thin pointer）
  - `references/log-index.md`／`CHANGELOG.md`（本 skill，同步）

### 變更摘要
1. 依使用者明確裁決（Gate 0 consent），把 `~/skill-inventory-viz/skill_inventory_showcase/` 整合入 toolkit-viz skill。來源**不用**含 9 處 expander 的原 showcase，而取**已去折疊、相對 import 已修復、已驗證**的 `quantum_website/src/views/skill_inventory/` 移植版（2026-11-25 既有成果），避免重複引入折疊違規。
2. `data.py` 的 `SNAPSHOT_PATH = parents[3] / data / skill_inventory_viz_data.json`：在 toolkit-viz 的 `src/views/skill_inventory/data.py` 位置，`parents[3]` 正好指向 skill 根，路徑無需改；快照從 `skill-inventory-viz/skill_inventory_viz_data.json` 複製。
3. `app.py` 頂層加 `st.sidebar.radio("展示模式", ["蒸餾主題", "🧭 技能盤點"], key="viz_display_mode", horizontal=True)`，選技能盤點則 `skill_inventory_sidebar()` + `render_skill_inventory()`，否則走原有蒸餾主題邏輯；符合 SSOT.B.1（radio、穩定 key、單 goal 只 hook 一條路徑）。
4. `skill_inventory_showcase` 非 skill（無 SKILL.md），故「deprecated」以 thin pointer（`DEPRECATED.md`）+ spec 註記處理，**不是** skill 索引 D 操作；原 showcase 程式保留供追溯，不刪除。
5. 遵守 SSOT A–E：無 pages/、無 selectbox、無 expander、`width="stretch"`、同源快照降級不編造；SSOT 規則文字本身不改（只引用）。

### 驗證結果
- Gate 1 pre audit：`toolkit-viz-pre-20261125-154214.md` + manifest `toolkit-viz-pre.sha256`（14 project + 1 generated；1 finding AST3 `__import__('datetime')` 為 dist/index.html 內嵌 JS 巧合字串，與本次無關）
- Gate 2 RED：`test_skill_inventory_integration.py` 4/4 失敗（view dir／no expander／app route／snapshot）
- Gate 3 GREEN：整合後 4/4 PASS（見 post 驗證）
- Gate 4 cleanup：清除 `__pycache__`／`.pyc`
- Gate 5 post audit + drift：見本 skill 報告，預期檔以外的 drift 視為 FAIL

### 上下級鏈影響
- 規則來源：toolkit-viz「Streamlit 規則（SSOT）」A–E（B1 radio、B2 直接呈現不折疊、A1 單一入口）。
- 上級：`toolkit-viz` skill 本身（U 修改，Gate 0–5）。
- 下級：`src/views/skill_inventory/`（viz 演示工具）、`data/skill_inventory_viz_data.json`（同源快照）。
- 退役：`skill_inventory_showcase` 為 thin pointer（非 skill 索引 D，不碰 self-developed.list）。

### 待辦／已知限制
- `quantum_website` 既有整合保留，本輪不改（已是既成事實）。
- 原 `skill_inventory_showcase/` 程式保留（只加 DEPRECATED.md），不刪除，供追溯。
- 未跑 `streamlit run` 實際 UI 渲染（僅 py_compile／import／靜態 grep 驗證）。
- 無 commit／publish／push。

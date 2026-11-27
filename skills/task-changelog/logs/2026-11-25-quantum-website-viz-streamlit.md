# 2026-11-25 — quantum_website viz 展示工具

## 移植 viz 演示工具、全站去除折疊區塊、修正 src.data 絕對 import

- **日期**：2026-11-25
- **類型**：feature + refactor + fix
- **涉及技能/檔案**：
  - `~/quantum_website/src/views/skill_inventory/` — 新建（`__init__.py`、`data.py`、`views/{overview,types,hierarchy,uncertain,catalog}.py`）
  - `~/quantum_website/data/skill_inventory_viz_data.json` — 新建（180 KB 同源快照副本）
  - `~/quantum_website/__init__.py` — 修改（新分段／sidebar／dispatch／去 2 處 expander）
  - `~/quantum_website/pages/app.py` — 修改（同步新分段／去 2 處 expander）
  - `~/quantum_website/src/views/toolkit_viz.py` — 修改（去 1 處 expander）
  - `~/quantum_website/src/views/quantum_tline.py` — 修改（去 1 處 expander）

### 變更摘要
1. 依 E-gate 提案與明確裁決，把 `~/skill-inventory-viz/skill_inventory_showcase/` 移植為 `quantum_website/src/views/skill_inventory/`，入口改為 `skill_inventory_sidebar()` + `render_skill_inventory()`；**不新增 pages/**。
2. 快照複製到 `data/skill_inventory_viz_data.json`，`data.py` 的 `SNAPSHOT_PATH` 改以 `Path(__file__).parents[3]` 推導 repo root，保留欄位驗證與 `errors` 降級。
3. 全 repo 6 處 `st.expander`（`__init__.py` S4 與搜尋、`pages/app.py` 同兩處、`quantum_tline.py` 備忘錄、`toolkit_viz.py` 搜尋結果）改為直接 `st.markdown`／`st.caption`，遵從 toolkit-viz SSOT B2「直接呈現（不折疊）」。
4. 使用者回報 `ModuleNotFoundError: No module named 'src.data'`；查證發現根因**不是** `__init__.py` 未指向 `app.py`，而是移植後 5 個 view 仍用絕對 `from src.data import ...`（在 quantum_website 解析到不存在的 `src/data.py`）。改為相對 `from ..data import ...` 後修復。

### 驗證結果
- 全 repo `st.expander`／`st.sidebar.expander`：PASS（0 命中）
- `selectbox`／`use_container_width`：PASS（0 命中，排除既有 doc_browser 註解）
- `py_compile` 所有修改檔：PASS
- Import 煙霧測試（`/home/sam/.venvs/toolkit-viz/bin/python`，streamlit 1.67.0）：PASS — routes = overview/types/hierarchy/origin/skills，快照存在
- 兩入口 `SECTIONS` 同步：PASS（皆含「🧭 技能盤點展示」）
- symlink 規則核實：skill-seek 搜尋所有 SKILL.md／docs／changelog，**無**「`__init__.py` symlink 指向 `app.py`」規則；最接近的 `toolkit-viz` A4 與 `push-streamlit:36` 是「內容同步」的 Streamlit 規則，未要求 symlink；`__init__.py` 為一般檔案、`app.py` 不存在。

### 上下級鏈影響
- 規則來源：toolkit-viz Streamlit SSOT A–E（B2 直接呈現、A4 入口同步）。
- 上級：`__init__.py`（單一入口，set_page_config 唯一）；`pages/app.py` 為既有未追蹤重複檔，本輪同步但其存在仍違反 A1（禁 pages/）。
- 下級：`src/views/skill_inventory/`（viz 演示工具）、`data/` 同源快照。

### 待辦／已知限制
- `pages/app.py` 仍是未追蹤檔且違反 SSOT A1；本輪只同步內容，未刪除（需擁有者裁決）。
- toolkit-viz A4「若支援 `streamlit run __init__.py`，保持與 `app.py` 一致」在本 repo 已過時（`app.py` 不存在，`__init__.py` 為唯一入口）；是否移除該規則待裁決。
- 未跑 `streamlit run` 實際 UI 渲染（僅 import 與 compile 驗證）。
- 無 commit／publish／push。

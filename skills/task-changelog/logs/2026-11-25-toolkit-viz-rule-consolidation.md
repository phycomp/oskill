# 2026-11-25 — toolkit-viz 規則單一化

## 整合 toolkit-viz 舊副本為單一 Streamlit 規則 SSOT + 同步 allow-list／chain-skill 盤點

- **日期**：2026-11-25
- **類型**：refactor + docs
- **涉及技能/檔案**：
  - `/home/sam/軟體/代理人/.agents/skills/toolkit-viz/` — 刪除（舊副本，5 條鐵律全為主版 SSOT 子集）
  - `/home/sam/.opencode/skills/toolkit-viz/SKILL.md` — 修改（去內部重複 + Logic check 2026-11-25）
  - `/home/sam/.opencode/skills/toolkit-viz/__pycache__/`、`scripts/__pycache__/` — 刪除（稽核建議的 bytecode 清理）
  - `/home/sam/.config/skill-timer/self-developed.list` — 修改（新增 `toolkit-viz`，self-developed SSOT）
  - `/home/sam/.agents/skills/chain-skill/SKILL.md` — 修改（新增盤點列 + Logic check 2026-11-25）
  - `/home/sam/skill-reports/toolkit-viz-20261125-102001.md` — 新建（稽核報告，填入 APPROVE / Low）
  - `/home/sam/skill-reports/manifests/toolkit-viz.sha256` — 更新（對應乾淨樹）
  - `/home/sam/.opencode/skills/task-changelog/` — 本日誌 + `references/log-index.md` + `CHANGELOG.md` 同步

### 變更摘要
1. 溯源比對：舊副本 5 條鐵律（單一 `app.py`+`src/views/`、subtopics 放 sidebar、`set_page_config` 一次、push 用 `scripts/push.sh`、主題改來源檔）全部為主版「Streamlit 規則（SSOT）」A–E 的子集，**無獨特規則**；使用者裁決直接刪除舊副本。
2. 主版去重複：`app.py` 架構樹註解由「單一 set_page_config」改指向 SSOT.A；原 `鐵律 2–4`（重複 SSOT.D1–D2）併為單一引用條；追加 `Logic check: 2026-11-25` 記錄閉環。
3. 稽核閉環：首掃 100/100 CRITICAL（SC8 `__pycache__` + generated SC9）→ 清除 bytecode 後重跑為 **9/100 LOW**；唯一殘留 AST3 `__import__('datetime')` 經語意審查為字面標準庫呼叫、無使用者輸入，判定良性誤報；報告填入 `APPROVE / Low`；manifest drift verify `OK: 10 files match`。
4. 治理同步：依 chain-skill「增刪 skill 時先改 allow-list，再同步下表」，先在 `self-developed.list`（SSOT）補 `toolkit-viz`，再於 chain-skill 盤點表新增一列（hooks：`push-streamlit` by goal、`chain-skill` + `rev-skill` 規則異動、`viz-router` 僅明確要求 mindmap 時）；chain-skill Logic check 落檔。
5. 不同步項判定：`skill-router` 已於 2026-11-24 標棄用（責任併入 `skill-family`），其表為 hook allow-list、不複製清單；`skill-family` 的表是 family-parent 路由索引，`toolkit-viz` 属展示平台而非 family parent，故兩者均未加入。

### 驗證結果
- 舊副本不存在：`PASS`（`[ -e ~/軟體/代理人/.agents/skills/toolkit-viz ]` 為 false）
- 主版編輯落地：`PASS`（`grep` 命中 `:42`、`:156–158`、`:213`）
- 規則不重複：`PASS`（`set_page_config` / `push.sh` / `topics_index.json` 僅出現於 SSOT 或程序性說明，無第二份規則表述）
- 稽核：`PASS`（helper 實跑，`toolkit-viz-20261125-102001.md`：9/100 LOW，1 finding 已判定誤報，verdict `APPROVE`）
- Manifest drift：`OK`（10 files match manifest）
- allow-list／盤點同步：`PASS`（allow-list `:23`、盤點表 `:65`、Logic check `:245`；新增列欄位數 6，與表頭一致）
- 敏感面：稽核報告 `External hosts: none`、無憑證讀取、無 persistence。

### 上下級鏈影響
- 上級 ← `skill-timer` allow-list（self-developed 唯一來源）；`chain-skill` 盤點表（index-only，非判定依據）。
- 下級 → `push-streamlit`（sync_topics.py／deploy by goal）；`chain-skill` + `rev-skill`（規則異動審查）；`viz-router`（僅明確要求 mindmap 時）。
- 雙向交叉引用：`toolkit-viz/SKILL.md` 的 SSOT 宣告 ↔ `self-developed.list` 的 `toolkit-viz` 條目 ↔ `chain-skill` 盤點列 ↔ 本日誌。

### 待辦／已知限制
- 歷史日誌 `logs/2026-11-24-toolkit-viz-rename-cleanup.md` 仍記載舊副本路徑，属事件記錄，依慣例不修改。
- 本次無 commit／publish／push。

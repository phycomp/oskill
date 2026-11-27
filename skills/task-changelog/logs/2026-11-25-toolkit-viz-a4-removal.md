# 2026-11-25 — toolkit-viz A4 移除

## 移除 toolkit-viz SSOT A4「__init__.py 保持與 app.py 一致」

- **日期**：2026-11-25
- **類型**：refactor + docs
- **涉及技能/檔案**：
  - `/home/sam/.opencode/skills/toolkit-viz/SKILL.md` — 移除 A4、A5 遞補為 A4、追加 Logic check
  - `/home/sam/.opencode/skills/toolkit-viz/tests/test_no_init_sync_rule.py` — 新建（RED/GREEN）
  - `/home/sam/skill-reports/toolkit-viz-pre3-20261125-140840.md` + `manifests/toolkit-viz-pre3.sha256` — 新建
  - `/home/sam/skill-reports/toolkit-viz-post3-20261125-141317.md` + `manifests/toolkit-viz-post3.sha256` — 新建

### 變更摘要
1. 使用者先要求以 skill-seek 核實「`__init__.py` symlink 指向 `app.py`」規則；全 SKILL.md／docs／changelog 搜尋結果：無此規則。最接近的 `toolkit-viz` A4 與 `push-streamlit:36` 都是「內容同步」的 Streamlit 規則、未要求 symlink；`push-streamlit` 打包明確排除 `__init__.py`。
2. 使用者明確裁決移除 `toolkit-viz` A4「若支援 `streamlit run __init__.py`，保持與 `app.py` 一致」：理由為本機 repo 已無 `app.py`（`__init__.py` 為唯一入口），且 symlink／內容同步要求已過時。
3. A5「相對路徑」遞補為 A4；A 節由 5 條變 4 條。B/C/D/E 不受影響。
4. `topic-distill/SKILL.md:35` 仍有同類「`__init__.py` 同步」字串，屬另一技能規則，本輪未改（已於 Logic check 記錄）。

### 驗證結果
- Gate 1：`toolkit-viz-pre3-20261125-140840.md`，9/100 LOW，`APPROVE / Low`，manifest 路徑已確認。
- Gate 2 RED：`tests/test_no_init_sync_rule.py` 4 項失敗 exit=1。
- Gate 3 GREEN：4 項全數 PASS exit=0。
- Gate 4：`__pycache__`／test cache 清除。
- Gate 5：`toolkit-viz-post3-20261125-141317.md`，9/100 LOW、`APPROVE / Low`；drift 僅 `CHANGED SKILL.md` + `NEW tests/test_no_init_sync_rule.py`，皆預期。

### 上下級鏈影響
- 上級 ← `toolkit-viz` Streamlit SSOT A–E（本輪改 A 節）。
- 下級 → 引用 SSOT 的技能（`topic-viz`／`qbit-viz` 等）不受影響；A 節重新編號後沒有懸空引用。
- 交叉引用：`toolkit-viz` A4 ↔ `tests/test_no_init_sync_rule.py` ↔ 本日誌。

### 待辦／已知限制
- `topic-distill/SKILL.md:35` 的「`__init__.py` 同步」仍存在，若要一併移除需另走 Gate 0 裁決。
- 無 commit／publish／push。

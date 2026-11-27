# 2026-11-25 — science family 合併

## 合併 sci-sediment／sci-research-distill 並將 sci-router 收斂為純 router

- **日期**：2026-11-25
- **類型**：refactor + docs
- **涉及技能/檔案**：
  - `/home/sam/.agents/skills/sci-sediment/SKILL.md` — v1.1.1 → v2.0.0（共用核心 C1–C4 + Branch A/B）
  - `/home/sam/.agents/skills/sci-sediment/tests/test_v2_merge.py` — 新建（RED/GREEN）
  - `/home/sam/.agents/skills/sci-research-distill/SKILL.md` — v1.1.2 → v1.2.0 deprecated_keep thin alias（`replaced_by: sci-sediment`）
  - `/home/sam/.agents/skills/sci-research-distill/tests/test_deprecated_alias.py` — 新建
  - `/home/sam/.opencode/skills/sci-router/SKILL.md` — v1.4.2 → v2.0.0（純 goal→hook router）
  - `/home/sam/.opencode/skills/sci-router/tests/test_v2_router.py` — 新建
  - `/home/sam/.agents/skills/chain-skill/SKILL.md` — 修改（三列同步 + Logic check）
  - `/home/sam/.agents/skills/skill-family/SKILL.md` — 修改（兩列同步）
  - `/home/sam/skill-reports/{sci-sediment,sci-research-distill,sci-router}-{pre,post}-20261125-*.md` + 對應 manifest — 新建

### 變更摘要
1. 重疊分析：兩技能共享「證據紀律」（no-invention／label estimate·`[待查]`／claim verbs／evidence levels／common mistakes），但骨架互補（科學結果四區塊 vs 產品→市場 11 步驟）。據此裁定「同一證據紀律、兩條領域骨架」，不是硬湊全文。
2. `sci-sediment` v2.0.0：抽出 **C1–C4 共用核心**為唯一證據紀律來源；**Branch A** 承接原四區塊展示／6 步工作流程／圖表合約／概念模型驗證（`sci-concept-valid` 已併入）；**Branch B** 承接原 `sci-research-distill` 11 步驟與 TAM/SAM/SOM／財務／認證／Paperclip deliverable；新增 Goal→Branch 路由表與合併去重後的 common mistakes。
3. `sci-research-distill` 降為 `deprecated_keep` thin alias，frontmatter 標 `deprecated: true` / `replaced_by: sci-sediment`，原文移除只留指向 Branch B 的引用。
4. `sci-router` v2.0.0 收斂為純 goal→hook router：移除 S1–S7 管線全文與 8 gates 細部（改引用 `topic-distill`／`arxiv-search`／`sci-sediment` 共用核心），新增 Goal→Hook 對照表與明確父節點表。
5. 治理同步：chain-skill 盤點表三列（sci-router／sci-research-distill／sci-sediment）+ Logic check、skill-family 兩列同步；allow-list 無增刪（僅 `sci-router` 原已在 SSOT）。

### 驗證結果
- Gate 1 pre audit：`sci-sediment` 8/100 LOW、`sci-research-distill` 0/100 SAFE、`sci-router` 10/100 LOW；三份 `-pre.sha256` 路徑已 `ls` 確認。
- Gate 2 RED：`test_v2_merge.py` 5 FAIL exit=1；`test_deprecated_alias.py` 3 FAIL exit=1；`test_v2_router.py` 3 FAIL exit=1。
- Gate 3 GREEN：三份皆全數 PASS exit=0（5/3/3）。
- Gate 4：三技能 `__pycache__`／test cache 皆清除。
- Gate 5 post audit：15/100 LOW、15/100 LOW、14/100 LOW；findings 逐條語意審查（LP3 純文件無 tool scope、AE4 既有範例、AS3 alias 枚舉、RP1 命中正是禁止未釘版安裝的句子）→ 三份 verdict 皆 `APPROVE / Low`。
- Gate 5 drift：三份皆 `CHANGED SKILL.md` + `NEW tests/*`，全部為預期檔，無非預期寫入。
- 索引核對：chain-skill 三列＋Logic check、skill-family 兩列落地。

### 上下級鏈影響
- 上級 ← `sci-router` v2.0.0（parent，goal→hook）；`chain-skill` 盤點表（index-only）。
- 下級 → `sci-sediment` v2.0.0（Branch A/B）← `sci-research-distill` deprecated alias；`topic-distill`／`arxiv-search`／`viz-router`／`push-*` by goal。
- 雙向交叉引用：`sci-sediment` 共用核心 ↔ `sci-router` 路由判準 ↔ `sci-research-distill` alias ↔ chain-skill／skill-family 索引 ↔ 本日誌。

### 待辦／已知限制
- `sci-sediment`／`sci-research-distill` 原不在 self-developed allow-list（既有索引狀態），本輪未新增；週期合規檢查只會覆蓋 allow-list 內的 `sci-router`。
- `sci-router` 的 S1–S7 管線細節改以引用方式指向 `topic-distill`／`arxiv-search`；若兩者更新，需確認引用仍成立。
- 無 commit／publish／push。

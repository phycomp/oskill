# 2026-11-26 — dev-skill 沉澱

## 沉澱 dev-skill：把「skill-family 建 parent + chain-skill 建 parent-child 鏈」封裝為技能開發編排 SOP

- **日期**：2026-11-26
- **類型**：feature + docs
- **涉及技能/檔案**：
  - `/home/sam/.agents/skills/dev-skill/SKILL.md` — 新建（v1.0.0，D0–D6 編排 SOP）
  - `/home/sam/.config/skill-timer/self-developed.list` — allow-list SSOT += `dev-skill`
  - `/home/sam/.agents/skills/chain-skill/SKILL.md` — inventory 表加一列、Logic check 註記（修改）
  - `/home/sam/.agents/skills/skill-family/SKILL.md` — v1.1.9 → v1.2.0，Index 表加一列、Version Log、Notes Logic check（修改）

### 變更摘要
1. 依使用者指令，把上輪實際執行的「`1.skill-family llm-router`、`2.chain-skill quantum-llm, em-llm`」工作流沉澱為可重用技能 `dev-skill`，置於 `~/.agents/skills/dev-skill/SKILL.md`。
2. `dev-skill` 定位為 **orchestrator**：hook 既有技能（`skill-family` 建 parent、`chain-skill` 建鏈與六階段、`skill-timer` allow-list SSOT、`task-changelog` 異動日誌），**不重述它们**的領域規則；並明確與 `impl-skill`（單一 skill 沉澱）、`skill-crud`（C/R/U/D 生命週期）、`refactor-skill`（既有重構）的邊界。
3. 固化 D0–D6 流程：拆解請求 → 目標命名與 allow-list 查重 → hook `skill-family` 建 parent → hook `chain-skill` 建 parent-child 鏈 → allow-list／交叉索引同步 → 治理規則（本機 develop 不 hook `audit-skill`）→ `task-changelog` 與交付前核對。
4. 遵守 allow-list SSOT 紀律：先改 `~/.config/skill-timer/self-developed.list`，再同步 `skill-family` Index、`chain-skill` inventory 與各自的 Logic check／Version Log；`skill-family` 升版 1.2.0。
5. 如實揭露 `envprof-evol` 內文「develop/update 仍須跑 canonical `audit_skill.py`」為舊表述，以 2026-11-26「本機 develop 不 hook、外部仍 hook」裁決為準。

### 驗證結果
- `dev-skill` 未預先存在：OK（三處 skill 目錄盤點皆無，無覆蓋風險）
- allow-list SSOT 註冊：PASS（`grep dev-skill self-developed.list` → 第 3 行）
- 交叉引用同步：PASS（`dev-skill` 於 `skill-family` 3 處、`chain-skill` 2 處可見）
- frontmatter 完整性：PASS（`name`／`description`／`version: 1.0.0` 齊全，繁體中文、Use when 開頭）
- 本機 develop 不 hook `audit-skill`：PASS（D5／Common Mistakes／Hook 清單皆一致）
- 憑證/commit：PASS（無憑證字面值、未 commit／push）

### 上下級鏈影響
- 上級 ← `skill-family`（家族 router：新增 `dev-skill` Index 列，Goal 為「建立一組技能＋建鏈」時可 hook）
- 平行／相鄰：`impl-skill`／`skill-crud`／`refactor-skill`／`chain-skill`（明確邊界，不重述規則）
- 雙向交叉引用：`dev-skill` ↔ `skill-family`／`chain-skill`／`skill-timer` allow-list／`task-changelog` 皆已對帳

### 待辦／已知限制
- `dev-skill` 為流程編排，無程式碼／scripts；一致性指 hook 目標存在且 allow-list 已註冊。
- `audit-skill` 靜描未另跑：依 2026-11-26 裁決，本機 develop 不需 hook 安全閘；外部 install／publish 仍強制。
- 所有變更皆未 commit／push。

# 2026-11-24 — topic-router 建立：topic 主題家族 + Obsidian 知識庫家族父節點

## 背景
延續 skill-family 統一 parent（goal→hook，不 inline child）與 chain-skill 六階段 + darwin-skill E0-E3 進化規則，第四個家族重構：`topic-xxx`／`xxx-topic` 命名技能 + Obsidian 相關知識管理技能，收斂到單一 `topic-router` 入口。allow-list SSOT = `~/.config/skill-timer/self-developed.list`。全程 native 執行（no worker/subagent）。

## 變更內容

### 1. 盤點（關鍵約束：雙父風險）
- `topic-*／*-topic` 命名技能：`topic-distill`（v1.2.0，`.opencode`，allow-list）、`topic-viz`（master `.opencode` + deprecated `.agents`）、`topic-post`（deprecated→topic-distill）、`topic-workflow-auto`（deprecated→topic-distill+distill-router）、原 `topic-seek` 已改名 `skill-seek`（`.agents`，v1.0.0 活動）。
- Obsidian／知識庫技能：`obsidian-automation`、`obsidian-markdown`（`.agents`）、`para-memory-files`（`.claude/skills` symlink → Paperclip 實例）；邊緣：`meeting-notes`、`weekly-report`。
- 既有主父：`topic-distill` 主父 `distill-router`，`topic-viz` 主父 `viz-router` → 不可重複 hook 形成雙父。

### 2. topic-router 建立（v1.0.0）
- 新建 `/home/sam/.agents/skills/topic-router/SKILL.md`，**只做「目標 → 轉介/hook」決策**，不 inline child 規則。
- **語意分層避免雙父**：
  - `topic-distill`／`topic-viz`：topic-router 僅「命名入口轉介」→ 主父 `distill-router`／`viz-router`；goal→hook 表標「轉介→主父」，不宣稱擁有規則。
  - `skill-seek`（承接 topic-seek 舊名）、`obsidian-automation`、`obsidian-markdown`、`para-memory-files`：無既有父，topic-router 首度直接 hook 為主父。
  - `topic-post`／`topic-workflow-auto`：deprecated，僅 historical 不 hook。
- 章節：0 雙父防護表／1 目標→轉介 hook（topic-* 轉介群 + Obsidian 直接 hook 群 + need-based predicate 細則）／2 既有 child 盤點／3 Function Set／4 閉環六階段／5 Cross-family 明確父節點／6 darwin E0-E3 + 棘輪／Version Log。
- E0 提示消除：把 description 的 `Use when` 觸發場景移到前段（原在第 250 字符後，部分 runtime 會截斷）。

### 3. 索引同步
- allow-list SSOT += `topic-router`（till `topic-distill` 後），現 **26 筆**，candidate 一致。
- `chain-skill` Inventory：`distill-router` 行後新增 `topic-router` 行。
- `skill-family` 同步 8 處：frontmatter version 1.1.0→1.1.4、Self-developed Index、Routing、Need-based predicate、predicate detail、hook 既有本機表 topic 行、Function Set 第 13 項 topic、Cross-family 表 topic-xxx 行、Version Log 1.1.4。

## 驗證
- darwin E0（4 skill）：`topic-router` **0 錯誤 0 警告 1 提示**（提示＝缺 test-prompts.json，可選）；`chain-skill`／`distill-router` 同級；`skill-family` 0 錯誤 2 既有警告（description 觸發場景、`scripts/push.sh` 引用），非本次引入。
- hook 目標存在性：12/12 全存在（含 `para-memory-files` symlink → Paperclip 實例，realpath 解析成功），缺失 0。
- 26/26 SSOT：磁碟找不到 0；11 個 router 全部在 chain-skill Inventory 與 skill-family Index 同時在列。
- 雙父檢查：`topic-distill` 仍為 `distill-router` child、`topic-viz` 仍為 `viz-router` child；`topic-router` 全表標「轉介→主父」，未奪主父。
- 全程 no commit / no publish / no push（skill-timer invariant：report-only；mono-repo 無 origin、`gh` 未安裝）。

## 待辦／裁決
- commit/push 阻塞：mono-repo 無 origin、`gh` 未安裝，所有變更多在本機未提交。
- `skill-family` 既有 2 警告是否處理（description 觸發場景、`scripts/push.sh` 引用忽略與否）。
- darwin E1/E2/E3（讀評／盲評實跑／真機）尚未對 `topic-router` 執行（目前僅 E0）；依棘輪需 E2 增益才保留微調。真機 E3 對 Obsidian 批次改寫屬不可逆，需 human checkpoint。
- 舊續辦：monthly timer Task 2、social/viz slot、`skill-logic-check.service`（exit=1）。

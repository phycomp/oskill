# 2026-11-24 — skill-family 閉環 router + mindmap-viz 抽離（draw/push/social/mindmap/svg）

## skill-family 閉環 router + mindmap-viz 抽離（draw/push/social/mindmap/svg）

- **日期**：2026-11-24
- **類型**：feature + refactor + docs
- **涉及技能/檔案**：
  - `/home/sam/.agents/skills/skill-family/SKILL.md`（新建，v1.0.0）— 閉環 router parent
  - `/home/sam/.agents/skills/mindmap-viz/SKILL.md`（新建）— SVG mindmap demo tool（input: hierarchy → output: SVG + validate）
  - `/home/sam/.agents/skills/viz-router/SKILL.md`（修改，V2）— render/validate 移交 mindmap-viz；新增 Cross-family references
  - `/home/sam/docs/superpowers/plans/2026-11-24-mindmap-viz-extraction.md`（新建）
  - `/home/sam/docs/superpowers/plans/2026-11-24-skill-family-closed-loop.md`（新建）
- **兩種實作軌道**：mindmap-viz extraction（Native/Task1-3）+ skill-family closed loop（Native/Task1-3）。
- **skill-family 六大要求（全數落地）**：
  1. 父節點：skill-family 負責「目標 → hook」決策，不自行產出圖檔/執行原子能力（§1）。
  2. hook 下級：child 原子能力 + need-based predicate，parent 不重複 child 步驟（§2）。
  3. hook 本機既有：draw/push/social/mindmap/svg 功能全數 hook 既有 skill，14/14 驗證存在（§3-§4）。
  4. 跨家族明確父節點：social→social-router、topic→topic-distill、push→push-repo/streamlit、viz→viz-router、sci→sci-router（§7）。
  5. darwin-skill 進化：S1-S6 週期性審查機制（§6）。
  6. 沉澱：Version Log 1.0.0 + 兩份 plan 檔 + 六階段閉環（§5）。
- **驗證結果**：
  - 14/14 hook 目標技能存在（不另開發 ✓）。
  - mindmap-viz 無錯字；viz-router 引用一致（grep PASS）。
  - skill-family 六大要求區段齊全（self-review PASS）。
- **裁決/續留項**：
  - allow-list SSOT：skill-family / mindmap-viz 是否納入待裁決（目前 16 項不變，未自動改動）。
  - skill-timer invariant：本次無排程/发布/commit 動作。
- **執行方式**：Native（executing-plans），no worker mechanism。

# 2026-11-24 — 五家族技能鏈閉環 GREEN 批次 + viz rename

## 五家族閉環 GREEN 批次交付

- **日期**：2026-11-24
- **類型**：refactor + docs
- **涉及技能/檔案**：
  - `/home/sam/.agents/skills/topic-viz/SKILL.md` — R1：self-reference `replaced_by` → `/home/sam/.opencode/skills/topic-viz/SKILL.md`
  - `/home/sam/.agents/skills/topic-post/SKILL.md` — R2：uncertain 合併用語去 deprecated 用語
  - `/home/sam/.agents/skills/skill-seek/SKILL.md` — R3：rename `topic-seek` → `skill-seek`（git mv）
  - `/home/sam/.opencode/skills/topic-distill/SKILL.md` — R4：version 1.1.0 → 1.2.0
  - `/home/sam/.agents/skills/topic-distill-pipeline/` — R5：刪除（備份 `/tmp/opencode/deprecation_backup/20261124-111016/`）
  - `/home/sam/.agents/skills/scenario-router/SKILL.md` — R5/R3/R6 同步
  - `/home/sam/.config/skill-timer/self-developed.list` (+ `.candidate`) — R6/S1/P1 納入
  - `/home/sam/.opencode/skills/sci-{sediment,router,research-distill}.md`、`.opencode/skills/sci-concept-valid/SKILL.md` — S2–S4
  - `/home/sam/.opencode/skills/topological-insulator/SKILL.md` — S2 hook 導向更新
  - `/home/sam/.agents/skills/social-router/SKILL.md`、`/home/sam/.opencode/skills/social-media-suite/SKILL.md` — SO1–SO4
  - `/home/sam/.opencode/skills/push-streamlit/SKILL.md`、`/home/sam/.opencode/skills/push-streamlit/scripts/push.sh` — P2/P3
  - `/home/sam/.agents/skills/viz-router/SKILL.md`、`/home/sam/.agents/skills/quant-viz/SKILL.md` — V1/V5
  - `/home/sam/.agents/skills/chain-skill/SKILL.md` — 批次級 Inventory / Example chain / Predicate / Notes / Logic check 同步

### 變更摘要
1. topic：R1–R6 全數閉環（含版本漂移、空殼刪除、rename、deprecation 用語）。
2. sci：S1–S7 閉環（concept-valid → sci-sediment 合併、版本、引用、不納 scenario-router）。
3. social：SO1–SO5 裁決落地（parent 宣告、hook 標記、suite 降級、allow-list 不納）。
4. push：P1–P3 裁決落地（allow-list 三納、去冗餘、token 安全）。
5. viz：V1/V5 裁決落地（家族 parent 鏈、description 清理）。
6. viz rename：`viz-dboard` → `viz-router`（Gate 0：全改＋舊 trigger 保留；不發布；drift 僅 SKILL.md）。

### 驗證結果
- Pre manifest（GREEN baseline）：`/home/sam/skill-reports/manifests/green-pre.sha256` — PASS（20 檔）。
- Rename baseline：`viz-dboard-pre.sha256` / post：`viz-router-20261124-103038.md`、post2：`viz-router-20261124-113913.md` — PASS（drift 僅 `CHANGED SKILL.md`，預期；0 findings）。
- Post audits：topic-viz 14/100 LOW SAFE（3×AE4）；topic-post 24/100 MEDIUM；topic-distill 0；skill-seek 0；scenario-router 16/100；sci-* 相關；social-* 0–16/100；push-streamlit 43/100 MEDIUM；quant-viz 8/100；chain-skill 0 — 多數 APPROVE / APPROVE-LEANING；push-streamlit verdict CAUTION（TM2 HIGH pre-existing）。
- 殘留掃描：舊名僅見於 approved exceptions；token-in-URL 已清；allow-list 16 項齊。

### 上下級鏈影響
- 上級 ← `chain-skill`（SSOT 索引同步）；下級 → 各家族 child（hook 依 goal）。
- 雙向：social-router ↔ social-media-suite；viz-router ↔ quant-viz / topic-viz / skill-hierarchy-viewer；sci-router ↔ sci-sediment / sci-research-distill。

### 待辦／已知限制
- `writing-plans` 撰寫「每月一次、週五 22:00」排程計畫（進行中）。
- `skill-logic-check.service` 手動 start 待驗證（exit=1 先前已記錄）。
- skill-timer / rev-skill commit 尚未 push（mono-repo 無 origin、gh 未安裝）— 待裁決。

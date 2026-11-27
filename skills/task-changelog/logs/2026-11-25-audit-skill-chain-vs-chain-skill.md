# 2026-11-25 — 技能鏈稽核

## 核實 audit-skill-chain ↔ chain-skill：八段契約稽核報告

- **日期**：2026-11-25
- **類型**：docs
- **涉及技能/檔案**：
  - `/home/sam/.opencode/skills/audit-skill-chain/SKILL.md` — 稽核對象 A
  - `/home/sam/.agents/skills/chain-skill/SKILL.md` — 稽核對象 B
  - `/home/sam/skill-reports/audit-skill-chain-vs-chain-skill.md` — 新建（127 行，八段契約全填）

### 變更摘要
1. 先建立八段空報告表（先建表、後查證），再逐格填入 #1 節點清冊／#2 逐邊雙向矩陣／#3 MANIFEST 正反向覆蓋／#4 交叉引用／#5 內容正確性／#6 語意一致性／#7 版本註冊 git／#8 最終判定。
2. 核心發現：A↔B **雙向皆無引用**（`grep` 兩端無輸出），判定「無引用」；唯一相關是 `topic-router:38` 的單向跨家族引用。
3. 語意矛盾：`chain-skill:240` 宣稱「viz-router owns demo-code compliance」，但 `viz-router:11,27,50` 自述 route-only、不驗證、children own rules → 標「須澄清」。
4. 其它如實揭露：兩技能無 `version:`、未收錄 allow-list、git 未追蹤（B 有獨立 `.git/`）；`~/薦家/布球/` 不存在但属 path invariant 設計常數；兩技能無 scripts／MANIFEST 故 #3/#5 部分格 N/A。

### 驗證結果
- 八段報告完成度：`grep -n '^## #'` = 8、無「待查／<placeholder>」殘留、127 行
- 引用驗證：`references/*` 三档存在；template `grep -c '^## #'` = 8 與 A 的 8 段契約相符；rev-skill:19,182 有 Logic Consistency Check
- 判定：#1 PASS／#2 PASS（無引用）／#3 N/A／#4 PASS／#5 PASS／#6 FAIL（須澄清）／#7 FAIL（註冊與版本缺失）

### 上下級鏈影響
- 無技能位元組變更；僅新增稽核報告與本日誌。
- 待裁決：是否新增 audit-skill-chain ↔ chain-skill 的 hook（需 rev-skill Gate 0）；是否修正 chain-skill:240 的 viz-router 職責宣稱。

### 待辦／已知限制
- 本輪只查 A↔B 一對；B 盤點表其它 30+ hook 目標未逐一驗證，不宣稱「全部已驗證」。
- 無 commit／publish／push。

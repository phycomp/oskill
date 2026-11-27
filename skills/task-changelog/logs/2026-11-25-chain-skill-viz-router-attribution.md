# 2026-11-25 — chain-skill 歸屬句修正

## 修正 chain-skill 對 viz-router 的 doc/code compliance 歸屬矛盾

- **日期**：2026-11-25
- **類型**：fix + docs
- **涉及技能/檔案**：
  - `/home/sam/.agents/skills/chain-skill/SKILL.md` — 4 處歸屬句 + 1 行 Logic check
  - `/home/sam/.agents/skills/chain-skill/tests/test_viz_router_attribution.py` — 新建（rev-skill Gate 2/3 測試）
  - `/home/sam/skill-reports/chain-skill-attribution-post-20261125-170200.md` + `manifests/chain-skill-attribution-post.sha256` — 新建（post audit）
  - `/home/sam/skill-reports/audit-skill-chain-vs-chain-skill.md` — 更新 #5/#6/#8 為「已修正」

### 變更摘要
1. 依前筆稽核 `audit-skill-chain-vs-chain-skill.md` #6 發現，`chain-skill` 宣稱「`viz-router` owns demo-code compliance」與 `viz-router:11,27,50` 的 route-only 自述矛盾。使用者裁決「是改 chain-skill 的歸屬句」（Gate 0 explicit consent），**不加 hook**。
2. 最小修正 4 處：Example chains 標註（:139）、need-based predicate（:163）、loop closure（:211–214）、Notes 歸屬句（:241）全部改為「`viz-router` 僅 goal→hook 路由；hooked child 執行 SVG／demo 驗證；`rev-skill` 管 Logic L6 文件↔實作一致」。
3. 新增 Logic check 2026-11-25（歸屬句修正），留明 consent／pre manifest／RED／GREEN 證據，符合 L7。
4. rev-skill Gate 0–5：pre audit 0/100 LOW SAFE → RED 8/9 → GREEN 8/8 → post audit 7/100 LOW SAFE → drift 僅預期檔。

### 驗證結果
- RED：`python3 tests/test_viz_router_attribution.py` → 8 check(s) failed, exit=1
- GREEN：8/8 PASS, exit=0
- Gate 4：0 pyc、0 `__pycache__`
- post audit：7/100 LOW SAFE、1 finding（LP3 MEDIUM：`SKILL.md` 無 allowed-tools 但新增測試讀取同目錄 SKILL.md 觸發 file_read 能力偵測；純方法技能既有設計、無外部讀寫 → 降級 Low），verdict `APPROVE / Low`
- drift vs pre：`CHANGED SKILL.md` + `NEW tests/test_viz_router_attribution.py`（全為預期）
- post manifest 自比對：`OK: 2 files match manifest .../chain-skill-attribution-post.sha256`

### 上下級鏈影響
- `chain-skill` 與 `viz-router` 的職責歸屬一致化；`viz-router` 維持 route-only、`mindmap-viz` 為 SVG 驗證 child、`rev-skill` 管 Logic L6。
- 未新增 `audit-skill-chain` ↔ `chain-skill` hook（仍待裁決）。
- 原稽核報告 #6 由「FAIL 須澄清」改為「修正後 PASS」，#5/#8 同步；八段契約仍完整。

### 待辦／已知限制
- `audit-skill-chain` ↔ `chain-skill` 是否建立 hook 仍未裁決（前筆稽核發現雙向無引用）。
- 本輪只改歸屬句，未動 `viz-router`、`rev-skill` 本體。
- 無 commit／publish／push。

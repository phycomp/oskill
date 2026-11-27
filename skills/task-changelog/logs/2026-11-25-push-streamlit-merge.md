# 2026-11-25 — push-streamlit 合併

## 合併 push-streamlit 入 toolkit-viz D 節並降為 deprecated alias

- **日期**：2026-11-25
- **類型**：refactor + docs
- **涉及技能/檔案**：
  - `/home/sam/.opencode/skills/toolkit-viz/SKILL.md` — D 節擴為部署唯一來源；移除既有 Known Issues／預防措施；鐵律更新
  - `/home/sam/.opencode/skills/toolkit-viz/tests/test_deployment_merge.py` — 新建（RED/GREEN）
  - `/home/sam/.opencode/skills/push-streamlit/SKILL.md` — v1.3.1 → v1.4.0 deprecated_keep thin alias（`replaced_by: toolkit-viz`）
  - `/home/sam/.opencode/skills/push-streamlit/tests/test_deprecated_alias.py` — 新建
  - `push-router`／`topic-post`／`viz-router`／`skill-family`／`skill-seek`／`skill-dependency-hook`／`chain-skill`／`social-media-suite`／`stock-market`／`sci-router`／`audit-credential`／`topic-distill`／`ai-ml-app-engineering` — 交叉引用同步
  - `/home/sam/skill-reports/{toolkit-viz,push-streamlit}-{pre4,post4}-20261125-*.md` + manifest — 新建

### 變更摘要
1. `toolkit-viz` D 節由 2 條擴為 D1–D7：repo 事實卡（origin 推導鐵律）、sync_topics 閘門（exit 1 不 push；來源覆蓋 repo）、Git／credentials hook `push-repo`（GIT_ASKPASS）、push.sh、三部署目標（Streamlit Cloud／HF Spaces 免費層硬限制／Kaggle Dataset）、驗證（health 只證明活著）、除錯與預防（合併去重）。
2. 既有「已知問題與解決方案」與「預防措施」兩節已併入 D7 並移除，避免雙份規則；**未重新引入** `__init__.py` 同步規則（同日較早剛從 A4 移除）。
3. `push-streamlit` 降為 `deprecated_keep` thin alias，5 支 scripts 保留原路徑供 toolkit-viz D 節引用。
4. 交叉引用完整同步：13 份技能中對 push-streamlit 的 hook／版本／依賴標記改指向 `toolkit-viz` D 節；歷史 deprecated 文件（`topic-workflow-auto`）與既有 Logic check／版本紀錄原文不改；allow-list 保留 `push-streamlit`（比照 `quant-algo-auto` deprecated_keep 慣例）。

### 驗證結果
- Gate 1：pre4 報告兩份（toolkit-viz 9/100 LOW、push-streamlit 43/100 MEDIUM），manifest 路徑已 `ls` 確認、verdict 填寫完成。push-streamlit 7 findings 逐條核對（TM2 惰性 shell 鏈、E1 文件化部署 API、RA2 `--wait` 說明）→ APPROVE/Low。
- Gate 2 RED：`test_deployment_merge.py` 7 項失敗 exit=1；`test_deprecated_alias.py` 4 項失敗 exit=1。
- Gate 3 GREEN：8/8 與 4/4 全數 PASS exit=0。
- Gate 4：兩技能 bytecode／test cache 清除。
- Gate 5：post4 toolkit-viz 9/100 LOW；push-streamlit raw 59/100 HIGH 但 6 項 findings 與 pre4 完全相同（只改 SKILL.md、腳本 bytes 未變），逐條舉證後降級 APPROVE/Low；drift 兩份皆僅 `CHANGED SKILL.md` + `NEW tests/*`。
- 交叉引用：13 份技能同步完成；殘留 push-streamlit 字串皆為 deprecated 標記、歷史紀錄或 scripts 路徑。

### 上下級鏈影響
- 上級 → `toolkit-viz`（Streamlit SSOT 唯一來源，A–E + D 部署）。
- 下級 → `push-repo`（Git／token 安全 hook）；`push-router`（goal→hook parent）；5 支 scripts 留存原路徑。
- 雙向交叉引用：`toolkit-viz` D ↔ `push-streamlit` alias ↔ 13 份技能引用 ↔ chain-skill 盤點／Logic check ↔ 本日誌。

### 待辦／已知限制
- `scripts/` 仍留在 `push-streamlit` 目錄（供 toolkit-viz D 節以絕對路徑引用）；若要搬移到 toolkit-viz/scripts/ 需另行裁決並更新所有路徑。
- allow-list 仍列 `push-streamlit`（deprecated_keep，與 `quant-algo-auto` 一致）。
- 無 commit／publish／push。

# 2026-11-24 physim-topics 兩套蒸餾收斂為一

## 變更類型
技能內容收斂（更新既有 skill）+ 蒸餾 master 整併。

## 背景
使用者輸入 `topic-router ~/物理模擬`（topic-router 於本輪稍後安裝）；裁決「收斂兩套為一，repo `topics/` 為 master，不重做內容」。既有兩套蒸餾不一致：

- repo `/home/sam/物理模擬/topics/`：10 檔、993 行、domain 聚類、較完整。
- skill `~/.opencode/skills/physim-topics/references/`：11 檔、553 行、功能聚類；獨有 S4 網路充實與驗收規格/概念圖。

## 執行
1. **Pre-change audit**：`APPROVE` / Low（AE4 中英混排 false positive），manifest `physim-topics.sha256`。
2. **Master 整併**（repo `topics/`，12 檔）：
   - `05_` 補入 skill 版 S4 獨有文獻（Navier-Stokes / OpenAI 2026-09，標 `⚠️ 未驗證` 與爭議）。
   - 新增 `10_驗收規格.md`、`11_概念圖.md`（由 skill 09/10 搬入，避開 repo 既有 `09_相對論` 編號）。
   - `00_索引.md` 更新地圖 10/11、修正 `~/.agents` → `~/.opencode` 路徑漂移、移除不存在的 `sci-distill-push` 改標 `distill-router`/`topic-distill`。
3. **Skill references 同步**：舊功能聚類 11 檔刪除，改用 master 的 domain 聚類 12 檔逐檔 md5 一致副本。
4. **SKILL.md**：升 1.3.0、入口 `00_索引.md`、快速路由改 domain 聚類、新增 master 關係與爭議標註鐵律。
5. **Re-audit**：`APPROVE` / Low（8→28 分，新增 9 筆同類 false positive：AE4×6 標題混排、AS3×4 來源路徑交叉引用）；post manifest `physim-topics-post.sha256`。
6. **Drift check**：`OK: 13 files match manifest`；master↔refs 12/12 md5 一致；舊名掃描僅 v1.2.0 changelog 歷史行（刻意保留）。

## 路由一致性
```
topic-router → distill-router（主父）→ topic-distill → 本次收斂
```
與 topic-router §1 決策表一致；physim-topics 為蒸餾結果索引（非 topic-* 命名技能），不在 topic-router 整合範圍，未改動它。

## 交付狀態
- 全部變動停留本機，**未 commit / 未 push**。
- Audit 報告：`~/skill-reports/physim-topics-20261124-173809.md`（pre）、`~/skill-reports/physim-topics-post-20261124-174101.md`（post）。
- 無混入 `oskill`／home 層既有無關髒改動。

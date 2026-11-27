# 變更日誌索引（Log Index）

所有日誌條目的單一查詢入口。日期 → 檔案 → 標題 → 類型。
新增一筆日誌後，請在此表最上方（最新在前）補一列。

| 日期 | 標題 | 類型 | 檔案 |
|------|------|------|------|
| 2026-11-27 | toolkit-viz 新增演示graphify觸發與 skillrule-viz UI 載入修正 | fix + docs + test | [logs/2026-11-27-toolkit-viz-graphify-trigger-ui.md](../logs/2026-11-27-toolkit-viz-graphify-trigger-ui.md) |
| 2026-11-27 | skillrule-viz 擴充 manifest/drift 解析與 Graphify 原生 HTML Streamlit 整合 | feature + docs | [logs/2026-11-27-skillrule-viz-manifest-drift-graphify-html.md](../logs/2026-11-27-skillrule-viz-manifest-drift-graphify-html.md) |
| 2026-11-27 | skill-gvnor 壓力情境 TDD：baseline 3/3 違規 → with-skill 3/3 遵守 → REFACTOR 4 反制 → meta-test「技能已清楚」 | refactor + fix + docs | [logs/2026-11-27-skill-gvnor-pressure-test.md](../logs/2026-11-27-skill-gvnor-pressure-test.md) |
| 2026-11-27 | skill-gvnor description 微測 6/6；allow-list SSOT → chain-skill → skill-family 索引同步 | docs + chore + refactor | [logs/2026-11-27-skill-gvnor-index-sync.md](../logs/2026-11-27-skill-gvnor-index-sync.md) |
| 2026-11-26 | 建立 skill-gvnor：整合 audit／inspect／revised／CRUD 四能力治理 router，skill-crud R/U 改 hook 消除全文 drift | feature + refactor + docs | [logs/2026-11-26-skill-gvnor-integration.md](../logs/2026-11-26-skill-gvnor-integration.md) |
| 2026-11-26 | 沉澱 dev-skill：把「skill-family 建 parent + chain-skill 建 parent-child 鏈」封裝為技能開發編排 SOP | feature + docs | [logs/2026-11-26-dev-skill-sedimentation.md](../logs/2026-11-26-dev-skill-sedimentation.md) |
| 2026-11-26 | em-llm 改連 OpenCode 本機 API、重算四截面並沉澱 v2；建立 LLM 技能鏈與治理規則更新 | feature + refactor + docs + chore | [logs/2026-11-26-em-llm-opencode-skill-chain.md](../logs/2026-11-26-em-llm-opencode-skill-chain.md) |
| 2026-11-25 | 修正 chain-skill 對 viz-router 的 doc/code compliance 歸屬矛盾 | fix + docs | [logs/2026-11-25-chain-skill-viz-router-attribution.md](../logs/2026-11-25-chain-skill-viz-router-attribution.md) |
| 2026-11-25 | 核實 audit-skill-chain ↔ chain-skill：八段契約稽核報告 | docs | [logs/2026-11-25-audit-skill-chain-vs-chain-skill.md](../logs/2026-11-25-audit-skill-chain-vs-chain-skill.md) |
| 2026-11-25 | 整併 push-streamlit 合併與「更新演示工具」並行變更、最終稽核 | refactor + docs + fix | [logs/2026-11-25-toolkit-viz-parallel-merge.md](../logs/2026-11-25-toolkit-viz-parallel-merge.md) |
| 2026-11-25 | toolkit-viz 去除 4 處冗餘規則（sync 重複／裸 push／docstring 重述／舊路徑） | refactor + docs | [logs/2026-11-25-toolkit-viz-dedup.md](../logs/2026-11-25-toolkit-viz-dedup.md) |
| 2026-11-25 | 整合 skill_inventory_showcase 入 toolkit-viz 並標 deprecated | feature + refactor + docs | [logs/2026-11-25-skill-inventory-into-toolkit-viz.md](../logs/2026-11-25-skill-inventory-into-toolkit-viz.md) |
| 2026-11-25 | 合併 push-streamlit 入 toolkit-viz D 節並降為 deprecated alias | refactor + docs | [logs/2026-11-25-push-streamlit-merge.md](../logs/2026-11-25-push-streamlit-merge.md) |
| 2026-11-25 | 移除 toolkit-viz SSOT A4「__init__.py 保持與 app.py 一致」 | refactor + docs | [logs/2026-11-25-toolkit-viz-a4-removal.md](../logs/2026-11-25-toolkit-viz-a4-removal.md) |
| 2026-11-25 | 移植 viz 演示工具、全站去除折疊區塊、修正 src.data 絕對 import | feature + refactor + fix | [logs/2026-11-25-quantum-website-viz-streamlit.md](../logs/2026-11-25-quantum-website-viz-streamlit.md) |
| 2026-11-25 | 合併 sci-sediment／sci-research-distill 並將 sci-router 收斂為純 router | refactor + docs | [logs/2026-11-25-science-family-merge.md](../logs/2026-11-25-science-family-merge.md) |
| 2026-11-25 | 建立 skill-crud：合併 skill-creator／writing-skills／writing-plans 為 C/R/U/D 單一全文 | feature + refactor + docs | [logs/2026-11-25-skill-crud-merge.md](../logs/2026-11-25-skill-crud-merge.md) |
| 2026-11-25 | 整合 toolkit-viz 舊副本為單一 Streamlit 規則 SSOT + 同步 allow-list／chain-skill 盤點 | refactor + docs | [logs/2026-11-25-toolkit-viz-rule-consolidation.md](../logs/2026-11-25-toolkit-viz-rule-consolidation.md) |
| 2026-11-24 | topic-router 達爾文 E1/E2 驗收：4 勝 0 負、keep、總分 88.1 | docs + chore | [logs/2026-11-24-topic-router-darwin-e2.md](../logs/2026-11-24-topic-router-darwin-e2.md) |
| 2026-11-24 | topic-router 建立：topic 主題家族 + Obsidian 知識庫家族父節點 | feature + refactor + docs | [logs/2026-11-24-topic-router-obsidian-family.md](../logs/2026-11-24-topic-router-obsidian-family.md) |
| 2026-11-24 | 家族 router 批次重構：quant-algo-auto 拆解 + vid-router + paperclip-router + 索引同步 | refactor + feature + docs | [logs/2026-11-24-family-routers-quant-vid-paperclip.md](../logs/2026-11-24-family-routers-quant-vid-paperclip.md) |
| 2026-11-24 | skill-family 閉環 router + mindmap-viz 抽離（draw/push/social/mindmap/svg） | feature + refactor + docs | [logs/2026-11-24-skill-family-mindmap-viz.md](../logs/2026-11-24-skill-family-mindmap-viz.md) |
| 2026-11-24 | distill-showcase --> toolkit-viz 改名殘留清理（含視頻展示線同步） | refactor + docs | [logs/2026-11-24-toolkit-viz-rename-cleanup.md](../logs/2026-11-24-toolkit-viz-rename-cleanup.md) |
| 2026-11-24 | 五家族技能鏈閉環 GREEN 批次交付（topic/sci/social/push/viz）+ viz rename | refactor + docs | [logs/2026-11-24-family-green-batch.md](../logs/2026-11-24-family-green-batch.md) |
| 2026-11-24 | 撰寫「每月一次、星期五 22:00」家族鏈合規排程計畫 | docs | [logs/2026-11-24-family-chain-scheduler-plan.md](../logs/2026-11-24-family-chain-scheduler-plan.md) |
| 2026-11-18 | 新建 sssn-output 技能：列舉 session + 對話匯出 Markdown（TDD 全流程） | feature | [logs/2026-11-18-sssn-output.md](../logs/2026-11-18-sssn-output.md) |
| 2026-11-18 | 推廣 audit-worker-subagent 驗證紀律到 35 個技能（軟體 10 + 電磁 19 + QA 6） | refactor + docs | [logs/2026-11-18-audit-discipline-promotion.md](../logs/2026-11-18-audit-discipline-promotion.md) |
| 2026-11-18 | 新建 audit-worker-subagent 技能：派工後獨立驗收 + 模型對接審查 | feature | [logs/2026-11-18-audit-worker-subagent.md](../logs/2026-11-18-audit-worker-subagent.md) |
| 2026-11-18 | 新建 audit-skill-chain 技能：技能鏈稽核契約與雙向證據表 | feature | [logs/2026-11-18-audit-skill-chain.md](../logs/2026-11-18-audit-skill-chain.md) |
| 2026-11-18 | heatload-coff-nist 蒸餾展示整合（論文出處/資料庫/計算 Excel） | feature | [logs/2026-11-18-heatload-showcase.md](../logs/2026-11-18-heatload-showcase.md) |
| 2026-11-18 | thermal-* 技能重命名為 heatload-* + 全引用同步 | refactor | [logs/2026-11-18-heatload-rename.md](../logs/2026-11-18-heatload-rename.md) |
| 2026-11-18 | 已停業素食餐廳不列入總覽卡與 contact sheet | fix + docs | [logs/2026-11-18-poi-closed-restaurant.md](../logs/2026-11-18-poi-closed-restaurant.md) |
| 2026-11-18 | 熱負載技能上下級鏈重構 + 新建 heatload-coff-nist + 建立 task-changelog 常態日誌機制 | refactor + feature | [logs/2026-11-18-thermal-load-chain.md](../logs/2026-11-18-thermal-load-chain.md) |

---

## 統計（可選更新）

- 累計條目：25（2026-11-25 +10：toolkit-viz 規則整合、skill-crud 建立、science family 合併、quantum_website viz 移植、toolkit-viz A4 移除、push-streamlit 合併、skill_inventory 整合、並行變更整併、技能鏈稽核、chain-skill 歸屬句修正；前次 2026-11-24 校正為 15）
- 最早：2026-11-18
- 最近：2026-11-26

## 維護規則

1. 寫完 `logs/YYYY-MM-DD-<slug>.md` 立刻補索引列，最新列置頂。
2. 標題須與日誌檔內 `## <標題>` 完全一致，便於比對。
3. 類型縮寫沿用 `format.md` 定義（feature/refactor/fix/docs/chore，複合用 ` + `）。
4. 檔案欄用相對路徑 `../logs/...` 的 Markdown 連結。
5. 同步更新上層 `CHANGELOG.md`。

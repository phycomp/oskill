# 2026-11-27 — toolkit-viz 新增演示graphify觸發與 skillrule-viz UI 載入修正

- **日期**：2026-11-27
- **標題**：toolkit-viz 新增演示graphify觸發與 skillrule-viz UI 載入修正
- **類型**：`fix + docs + test`

## 涉及技能／檔案

修改：
- `/home/sam/.opencode/skills/toolkit-viz/SKILL.md`（description/觸發條件/§E 新增「演示graphify工具、演示graphify」hook toolkit-viz）
- `/home/sam/.opencode/skills/toolkit-viz/src/views/skill_rule_viz.py`（輸出目錄偵測支援根目錄即輸出、fallback 路徑、輸出選擇改 radio）
- `/home/sam/.opencode/skills/toolkit-viz/tests/test_update_demo_trigger.py`（新增 T1b 觸發字串檢查）

更新：
- `/home/sam/.opencode/skills/task-changelog/CHANGELOG.md`
- `/home/sam/.opencode/skills/task-changelog/references/log-index.md`

## 變更摘要

1. **觸發規則**：toolkit-viz 明確 hook「演示graphify工具、演示graphify」，與既有演示工具觸發共用路由；含「更新演示工具」仍走直接實作例外。
2. **UI 載入修正**：skillrule-viz Streamlit 視圖可辨識直接指定的輸出目錄，並補常見 fallback 路徑；選擇器改 `radio` 符合 SSOT。
3. **自動化驗證**：以 agent-browser 對本機 Streamlit 進行互動驗證（切換技能規則視覺化、載入 demo、確認節點/邊/Markdown/Mermaid 渲染）。

## 驗證結果

| 檢查 | 結果 |
|---|---|
| `py_compile` | PASS（`toolkit-viz/app.py`, `src/views/skill_rule_viz.py`） |
| `pytest test_skill_inventory_integration.py test_update_demo_trigger.py -q` | **4 passed, 14 warnings**（既有環境 warnings） |
| skillrule-viz demo 重建 | PASS（`nodes=43, edges=40, graph.html` 生成） |
| Streamlit UI 自動化 | PASS（互動載入與渲染確認；server restart 後截圖證據未保留） |

## 已知限制

- 先前 UI 截圖位於 `/tmp/opencode/...`，環境重啟後遺失；本次以重建 demo 產物與測試結果核實。

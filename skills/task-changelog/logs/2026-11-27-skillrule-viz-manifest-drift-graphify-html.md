# 2026-11-27 — skillrule-viz 擴充 manifest/drift 解析與 Graphify 原生 HTML Streamlit 整合

- **日期**：2026-11-27
- **標題**：skillrule-viz 擴充 manifest/drift 解析與 Graphify 原生 HTML Streamlit 整合
- **類型**：`feature + docs`

## 涉及技能／檔案

修改：
- `/home/sam/.opencode/skills/skillrule-viz/SKILL.md`（新增 manifest/drift/report 輸入、Graphify 原生 HTML、Streamlit 整合流程與注意事項）
- `/home/sam/.opencode/skills/skillrule-viz/scripts/skillrule_viz.py`（新增 `--manifest-target`、manifest drift 比對、audit report/JSON 解析、`graphify export html` 原生輸出、result.json 摘要）
- `/home/sam/.agents/skills/skillrule-viz/SKILL.md`（同步 opencode 端）
- `/home/sam/.agents/skills/skillrule-viz/scripts/skillrule_viz.py`（同步 opencode 端）
- `/home/sam/.opencode/skills/toolkit-viz/app.py`（新增「🕸 技能規則視覺化」展示模式路由）
- `/home/sam/.opencode/skills/task-changelog/CHANGELOG.md`
- `/home/sam/.opencode/skills/task-changelog/references/log-index.md`

新增：
- `/home/sam/.opencode/skills/toolkit-viz/src/views/skill_rule_viz.py`（讀取 skillrule-viz 輸出、顯示摘要/Markdown/Mermaid、以 `components.html` 內嵌 Graphify 原生 HTML）

## 變更摘要

1. **Manifest/drift 報告解析**：`skillrule_viz.py` 支援 `--manifest <sha256>` 與 `--manifest-target <dir>`，解析 sha256 manifest 條目；有 target 時比對 `ok/changed/missing/extra`，並將 drift 節點/邊納入資料驅動圖與報告。
2. **Audit report 解析**：支援 `--report <md|json>`，萃取 verdict、risk、raw summary 與 finding 表格；同名 `.json` 存在時併入 summary 欄位。
3. **Graphify 原生 HTML**：`--graphify cli|all` 時執行 `graphify export html --graph graph.json --output graph.html`；失敗不阻斷 ingest/report 產物。
4. **Streamlit 輸出整合**：`toolkit-viz` 新增「🕸 技能規則視覺化」模式，載入 `skillrule-viz-out` 輸出目錄，顯示節點/邊/manifest/report 摘要、Markdown、Mermaid 原始碼，並以 `streamlit.components.v1.html` 內嵌本機 `graph.html`。
5. **同步與降級**：opencode/agents 兩份 skillrule-viz 同步；Streamlit 視圖避免 `expander` 以符合 toolkit-viz SSOT.B.2。

## 驗證結果（實跑）

| 檢查 | 結果 |
|---|---|
| `py_compile` | PASS（`skillrule_viz.py`、`toolkit-viz/app.py`、`skill_rule_viz.py`） |
| 既有測試 | `pytest .opencode/skills/toolkit-viz/tests/test_skill_inventory_integration.py .opencode/skills/toolkit-viz/tests/test_update_demo_trigger.py -q` → **4 passed** |
| 煙測（manifest+report+HTML） | `python3 .../skillrule_viz.py --skill skillrule-viz --manifest /home/sam/skill-reports/manifests/graphifyy.sha256 --manifest-target /home/sam/.local/share/uv/tools/graphifyy/lib/python3.12/site-packages/graphify --report /home/sam/skill-reports/graphifyy-20261127-110520.md --mode both --graphify all --out /tmp/opencode/skillrule-viz-test2` → `nodes=41, edges=38, native_html=/tmp/opencode/skillrule-viz-test2/graph.html` |
| 原生 HTML 產物 | `/tmp/opencode/skillrule-viz-test2/graph.html` 存在（約 50KB） |
| Streamlit view import | `importlib` 載入 `skill_rule_viz.py`，`render_skill_rule_viz` 存在 |

## 上下級鏈影響

- `skillrule-viz` 擴充後可作為 toolkit-viz 的技能治理視覺化子視圖；資料來源為本機產出的 manifest/drift/report/graph 產物。
- Graphify project 註冊檔（`AGENTS.md`、`.opencode/plugins/graphify.js`、`.opencode/skills/graphify/`）仍為 untracked，本輪未納入 commit。

## 待辦／已知限制

1. 未執行 Streamlit 完整互動 UI 自動化；以 py_compile、既有測試、腳本煙測與 view import 驗證。
2. manifest `extra` 計算為 best-effort（target 目錄全檔案與 manifest 比對），大型 target 可能耗時。
3. Graphify CLI 仍需本機已安裝 `graphify`；失敗時降級為 ingest 產物。
4. 未 commit/push 以外的其他髒工作樹變更；本輪僅應提交相關檔案。

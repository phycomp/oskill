---
name: skillrule-viz
description: 將技能的 Gate/Drift/Rule/Logic check 規則視覺化為 Mermaid、Markdown 與 Graphify 原生圖譜輸出；支援 manifest/drift 報告解析與 Streamlit 內嵌原生 HTML。Use when the user asks for 技能規則視覺化、gate drift rule 圖、skill gate/drift/rule visualization, manifest drift 視覺化, or wants to inspect skill governance rules with graphify.
---

# skillrule-viz

將 skill 治理規則（Gate / Drift / Rule / Logic check）轉成可讀的 Mermaid/Markdown 報告，解析 audit manifest/drift/report，並產出 Graphify 可 ingest 資料與 Graphify 原生 HTML。

## 觸發條件

- 「技能規則視覺化」
- 「gate drift rule 圖」
- 「skillrule-viz」
- 需要用 Graphify 展示 skill 的 Gate / Drift / Rule / 規則關係
- 需要解析 manifest/drift/audit report 並視覺化

## 輸入

- `--skill <path-or-name>`：單一 skill 路徑或名稱（可重複）
- `--all`：掃描預設 skill 根目錄（`.opencode/skills`, `.agents/skills`）
- `--roots <dir,dir>`：自訂掃描根目錄
- `--out <dir>`：輸出目錄，預設 `./skillrule-viz-out/<timestamp>/`
- `--mode generic|data|both`：`generic`=通用流程圖；`data`=從 SKILL.md/audit manifest 萃取實際規則；`both`=兩者（預設）
- `--graphify ingest|cli|style|all`：Graphify 角色。`ingest`=產出 graph.json/graph.md；`cli`=產生 Graphify 原生 HTML（`graphify export html`）；`style`=節點型別樣式；`all`=三者（預設）
- `--manifest <path>`：audit manifest sha256 檔案，可重複
- `--manifest-target <dir>`：manifest 驗證目標目錄；提供時會計算 missing/changed/ok/extra
- `--report <path>`：audit 報告 Markdown/JSON，可重複

## 工作流程

1. **盤點目標**：解析 skill 路徑，讀取 `SKILL.md`。
2. **萃取規則**：抽取 Gate、Drift、Rule、Logic check、Iron Law/硬規則。
3. **解析 manifest/drift**：讀取 sha256 manifest；有 `--manifest-target` 時比對 missing/changed/ok/extra。
4. **解析 audit report**：讀取 verdict/risk/raw summary/findings；若同名 `.json` 存在則併入。
5. **產出視圖**：通用 Gate/Drift/Rule Mermaid、資料驅動 Mermaid、Markdown 報告、JSON graph。
6. **Graphify 原生 HTML**：`--graphify cli|all` 時執行 `graphify export html --graph graph.json --output graph.html`。
7. **Streamlit 整合**：`toolkit-viz` 的「技能規則視覺化」模式可載入輸出目錄，顯示摘要、Mermaid/Markdown、並以 `components.html` 內嵌 `graph.html`。

## 輸出

- `report.md`：總覽、manifest/drift/report 摘要、規則表、Mermaid。
- `generic.mmd` / `data.mmd`：Mermaid 原始檔。
- `graph.json`：節點/邊資料（Graphify ingest/自用）。
- `graph.html`：Graphify 原生 HTML（CLI 成功時）。

## 最小命令

```bash
python3 ~/.opencode/skills/skillrule-viz/scripts/skillrule_viz.py \
  --skill toolkit-viz \
  --manifest /path/to/audit.sha256 --manifest-target /path/to/skill \
  --report /path/to/audit-report.md \
  --mode both --graphify all --out ./skillrule-viz-out/demo
```

## 注意事項

- 不虛構不存在的 gate；從來源文字萃取，無法判定時標記 `unknown`。
- manifest 無 target 時只列 entries，不宣稱 drift 已驗證。
- Graphify CLI 失敗時降級為 ingest 產物，不阻斷報告。
- Streamlit 內嵌 HTML 只讀取本機已產生檔案，不執行遠端腳本注入。

## Logic check

Logic check: 2026-11-27 (skill-crud / initial) — 依使用者規格建立 skillrule-viz：目標位置兩邊、視覺化通用+資料驅動、Graphify 角色 ingest/CLI/style、輸出 Mermaid/Markdown/Graphify 原生。Gate 0 explicit consent（使用者回覆規格與「同時更新 toolkit-viz 觸發規則」）；Gate 1 以最小靜態檢查/py_compile 代替完整外部審核；Gate 2 RED=技能不存在；Gate 3 GREEN=建立 SKILL.md+script；Gate 4/5 待執行驗證與 commit。

Logic check: 2026-11-27 (rev-skill / manifest+html整合) — 依使用者指令「1.加 manifest/drift 報告解析 2.Graphify 原生 HTML 在streamlit輸出整合」最小修正：腳本新增 `--manifest-target`、manifest drift 比對、audit report 解析、`graphify export html` 原生輸出；toolkit-viz 新增「技能規則視覺化」模式載入輸出並內嵌 graph.html。Gate 0 explicit consent（本輪使用者明確要求）；Gate 2 RED=缺 manifest/report/HTML 整合；Gate 3 GREEN=腳本+view+app 路由；Gate 5 後續以 py_compile/煙測/現有測試驗證。

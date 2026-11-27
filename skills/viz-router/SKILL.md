---
name: viz-router
description: >
  Use when visualizing skill hierarchies or generating a mindmap of local
  skills. Triggers on "mindmap", "skill map", "viz-router", "viz-dboard"
  (former name), or "visualize skills".
---

# Viz Router（父）

viz-router 是 viz 家族的 **parent**：僅負責「視覺化目標 → hook 哪個 child」的路由決策。實際繪製（如 mindmap SVG）由 hooked child skill 完成，viz-router 不自行產出圖檔。

## 1. Inventory the skills

List the skills under review and their parent-child relationships.

## 2. Build the hierarchy

Define nodes and edges:

- Root: the collection (e.g., "self-developed skills")
- Parents: orchestrator skills
- Children: atomic capabilities hooked by parents

## 3. Render the mindmap（由 child mindmap-viz 完成）

繪製 skill 層級 mindmap 由 `mindmap-viz` 承接；viz-router 僅負責「視覺化目標 → hook child」的路由決策，**不自行產出 SVG**。

`mindmap-viz` 介面：input = hierarchy/skill-target → output = SVG + validate。

## Family position — viz 家族 parent（V2，2026-11-24；mindmap-viz 抽離）

`viz-router` 是 viz 家族的 **parent**：目標為「視覺化／mindmap／圖表」時，先載本 skill；再依領域目標 hook child。

| Goal | Hook | Skip when |
|---|---|---|
| Skill 集合層級圖／skill mindmap／workflow 視覺化 | `mindmap-viz`（繪製 SVG + validate；viz-router 僅 route） | 純文字摘要 |
| 量子/Bloch sphere/布球/Qiskit/Aer 相關技術分析與視覺化 | `qbit-viz` | 無數據／無圖表需求 |
| 量化金融視覺化／技術分析圖／K 線／問題視覺化 | `quant-viz` | 無數據／無圖表需求；策略邏輯與風控交給 `quant-risk-bt` |
| 主題重構/蒸餾來源 → 規格→視覺化→demo 沉澱 | `topic-viz`（master：`/home/sam/.opencode/skills/topic-viz/SKILL.md`；`.agents` 舊版已封存） | 無來源 |
| 技能目錄層級視覺化 | `hierar-viz` | — |
| codebase 架構／檔案關係／graphify-out 查詢／知識圖譜 | `graphify`（codebase → persistent knowledge graph；query/path/explain；本技能只 route） | 純文字摘要／無 codebase |
| 若目錄內有 distill（如 `file-distill`）則 hook 開發演示工具 | `toolkit-viz`（展示平台 SSOT A–E；實際技能以當時清單為準） | 無 distill 目錄 |
| 要產生 mindmap SVG 格式 | `mindmap-viz`（繪製 SVG + validate） | 不是要 SVG 格式 |

### Need-based predicate

- User asks to visualize/mindmap a set of skills → hook `mindmap-viz` (draw + validate) via this router (viz-router 只 route).
- User asks about a codebase / architecture / file relationships or `graphify-out` → hook `graphify` (knowledge graph; 本技能只 route).
- User asks for a quant-finance chart or problem visualization → hook `quant-viz`.
- User asks for topic spec/demo from refactored/distilled docs → hook `topic-viz` master.
- User asks for a demo/display tool → hook `toolkit-viz`（展示平台 SSOT；其 Related 回指本技能）。
- Do not inline child steps here; children own their rules, this skill owns the goal→hook decision.

## 4. Validate（child mindmap-viz 之責；viz-router 不驗證 SVG）

SVG 合法性驗證由 `mindmap-viz` 承接（`xml.etree.ElementTree` parse）。

## 5. Cross-family references（明確父節點）

When entering another family, explicit parent is noted：

| Target Family | Explicit Parent |
|---|---|
| `social-xxx` | `social-router` (parent) |
| `topic-xxx` | `topic-distill` (parent) / `skill-seek` (index) |
| `push-xxx` | `push-repo` / `quantum-website` (parent) |
| `viz-xxx` | `viz-router` (parent) → `mindmap-viz` (hook for SVG) |
| `sci-xxx` | `sci-router` (parent) → `sci-sediment` (hook for verification) |

- 「明確寫出其父節點」：每個 family 入口處標註 parent skill，避免歧義。
- 如需跨 family 流程，以 parent → hook chain 為序。

## Notes

- 標籤/繪製細節規則（如節點標籤短、虛線 conditional hooks、階層變更後更新圖）屬 child 繪製工具，見 `mindmap-viz`、`hierar-viz`、`quant-viz` 等。
- Logic check: 2026-11-24 V2：viz-router 只 route（goal→hook 決策），不自行產出 mindmap.svg；繪製由 `mindmap-viz`（或 `hierar-viz`、`quant-viz` 等 child）負責；已新增 `mindmap-viz` 到 goal table；交叉-family  parent 標籤見上表。
- Logic check: 2026-11-24 V3：viz-router 只 route（goal→hook 決策），不自行產出 mindmap.svg；繪製由 child（`hierar-viz`、`quant-viz` 等）負責；已新增 `qbit-viz` 到 goal table；`hierar-viz` 為現行名稱（舊名已淘汰）。
- Evolution: 參見 `darwin-skill` 週期性審查機制（S1-S7），可持續在 chain-skill 六階段閉環下微調目錄/hook 映射。
Logic check: 2026-11-26 (rev-skill / quantum-website 規則搬移) — 現行引用同步指向 `quantum-website`；僅引用同步，規則語意不變。Gate 0 explicit consent；Gate 1 `viz-router-qw-move-pre.sha256`；Gate 2 RED `tests/test_quantum_website_rule_move.py`；Gate 3 GREEN；Gate 5 drift 僅預期檔。

Logic check: 2026-11-27 (chain-fix) — child 表新增 graphify（codebase knowledge graph）+ 開發演示工具明確指向 toolkit-viz；Need-based predicate 補 graphify/toolkit-viz 兩條。drift 只 SKILL.md，verdict APPROVE。

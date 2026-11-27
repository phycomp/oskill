# 2026-11-26 — skill-gvnor 整合與 skill-crud R/U hook 化

- **日期**：2026-11-26
- **標題**：建立 `skill-gvnor`：比較 writing-plans／writing-skills／superpowers 後，整合 audit／inspect／revised／CRUD 四能力為 goal→hook 單一治理入口；`skill-crud` R/U 改 hook 消除全文 drift
- **類型**：`feature + refactor + docs`

## 涉及技能／檔案

新增（`/home/sam/.agents/skills/skill-gvnor/`）：
- `SKILL.md` v1.0.0 — goal→hook 單一入口、Iron Law、四能力編排、統一 evidence bundle、別名對照
- `references/routing.md` — 11 條 goal→hook 完整語意、邊界、跨 goal 銜接、subagent 派工補充規則
- `references/evidence-bundle.md` — 七欄位契約與範本
- `scripts/assemble_evidence.py` — stdlib-only 組裝器，不執行 shell、不改技能檔
- `tests/test_contract.py` — 12 項契約測試（正向 contract，對應「產出形狀不對」的失敗形式）

修改：
- `/home/sam/.agents/skills/skill-crud/SKILL.md` — §0 對照表、衝突裁決、R 章節（移除 L1–L8 全文）、U 章節（移除 Gate 0–5 全文）、來源與維護 + Logic check

證據：
- `~/skill-reports/skill-crud-gvnor-pre-20261126-201338.md`（verdict 已填 APPROVE）
- `~/skill-reports/manifests/skill-crud-gvnor-pre.sha256`
- `~/skill-reports/skill-crud-gvnor-post-20261126-203418.md`（verdict 已填 APPROVE）
- `~/skill-reports/manifests/skill-crud-gvnor-post.sha256`
- `~/skill-reports/evidence/skill-crud-20261126-203801.md`（統一證據包）
- `~/skill-reports/skill-crud-gvnor-pre-20261126-201338.md` 的 guardrails：可修改檔白名單僅 `skill-crud/SKILL.md`

## 變更摘要

1. **比較三者**：`writing-plans` 管「決策如何被傳達」（施工圖＋self-review 五點）；`writing-skills` 管「決策如何被遵守」（TDD Iron Law＋form matching＋micro-test）；`using-superpowers` 管「決策何時被載入」（1% 就載入＋red flags）。三者共享 TDD 血統但作用在三個不同關卡。
2. **建立 router**：`skill-gvnor` 只做 goal→hook 決策與證據組裝，不重複 child 規則全文；把 audit 導向 `audit-skill`、inspect 導向 `inspec-skill`＋`using-superpowers`、revised 導向 `rev-skill` Gate 0–6、CRUD 導向 `skill-crud`。
3. **消除 drift**：`skill-crud` 原 R 章節全文轉述 `audit-skill`／`rev-skill`／`chain-skill`，U 章節全文轉述 `rev-skill` Gate 0–5（違反其自身 L4「SSOT 不重複」）；改為 hook 本技能，只保留「規則在哪裡、證據放哪」的索引。
4. **別名文件化（依裁決）**：`inspect-skill`→`chain-skill`（已改名）、`inspec-skill`（現行，少一個 t）、`skill-router`→`skill-family`，寫入 `SKILL.md` 對照表；**未改** `~/.config/skill-timer/self-developed.list`／`chain-skill`／`skill-family` 索引。
5. **統一證據包**：把 audit manifest/verdict、revised 的 RED→GREEN/drift、CRUD 的 changelog、inspect 的選用紀錄串成七欄位 bundler。

## 驗證結果（實跑）

| Gate | 結果 |
|---|---|
| Gate 1 Pre-audit | CAUTION 27/100，2 findings（AS1 HIGH `grep -rl` 引述指令、RA2 MEDIUM `nohup` 引述指令）；逐行核對降級為惰性文字，verdict APPROVE、risk Low |
| Gate 2 RED | `python3 -m unittest discover` → **12 項全部失敗**（6 failures + 6 errors）；符合 RED baseline |
| Gate 3 GREEN | 建立技能並改 hook 後 **12/12 OK**（0.004s） |
| Gate 4 Cleanup | 清除 `tests/__pycache__` 等 bytecode/cache，OK |
| Gate 5 Post-audit | CAUTION 35/100，3 findings（新增 AS3 MEDIUM = U 章節 hook 路徑 `~/.agents/skills/rev-skill/SKILL.md`，惰性文字）；無新 HIGH/CRITICAL、無新信任錨，verdict APPROVE |
| Gate 5 Drift | `--verify` 對 pre manifest：**CHANGED SKILL.md**（唯一預期變更），無非預期檔 |

## 上下級鏈影響

- `skill-gvnor` 為 skill 治理家族 parent，hook 8 個既有技能（writing-skills／writing-plans／audit-skill／inspec-skill／rev-skill／chain-skill／skill-crud／using-superpowers），不新增重複技能。
- `skill-crud` Create／Delete 規則仍以自身為 SSOT；Review／Update 規則改以 `audit-skill`／`rev-skill`／`skill-gvnor` 為準，衝突裁決已改寫。
- 別名表寫在新技能內；索引同步（allow-list／chain-skill／skill-family）留下一輪，故本輪**不宣稱**家族索引完整。

## 待辦／已知限制

1. **TDD 完整壓力情境未跑**：planner 與 subagent 因 `Free usage limit reached` 中斷，無法派 subagent 跑 writing-skills 要求的 3+ 複合壓力情境與 no-guidance 控制組（每變體 ≥5 reps）。本輪只完成可程式驗證的契約測試 RED→GREEN；**不宣稱**已通過 writing-skills 的完整部署 checklist。下輪配額恢復後補跑。
2. **索引同步下一輪**（使用者裁決）：`self-developed.list`／`chain-skill` inventory／`skill-family` Index 尚未加入 `skill-gvnor`；別名也未改指向。
3. **post-audit 属 CAUTION**：已逐行判定並填 verdict；三個 finding 皆為文件內惰性文字，guardrails 見報告 Notes。
4. **未 commit／push**：本輪無 push 授權；本機 commit 亦未執行（依 push-router 鐵律，純本機改檔不需 commit）。

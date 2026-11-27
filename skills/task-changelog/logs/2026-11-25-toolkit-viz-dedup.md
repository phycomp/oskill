# 2026-11-25 — toolkit-viz 去除 4 處冗餘規則

## 核實後移除重複/衝突/過時規則，SSOT 定義+引用型重複保留

- **日期**：2026-11-25
- **類型**：refactor + docs
- **涉及技能／檔案**：
  - `~/.opencode/skills/toolkit-viz/SKILL.md`（修改：使用方式段去sync重複、裸push改hook、Logic check）
  - `~/.opencode/skills/toolkit-viz/src/views/skill_inventory/__init__.py`（修改：docstring 改引用 SSOT）
  - `~/.opencode/skills/toolkit-viz/src/views/skill_inventory/data.py`（修改：舊 showcase 路徑註解）
  - `~/.opencode/skills/toolkit-viz/tests/test_no_redundant_rules.py`（新建，4 項 RED/GREEN）
  - `references/log-index.md`／`CHANGELOG.md`（本 skill，同步）

### 變更摘要
核實 toolkit-viz 規則重複後，區分「定義+引用型合理重複」（GIT_ASKPASS／sync_topics／同源快照／Logic check 歷史）與「真冗餘」，移除 4 處：
1. `SKILL.md`「同步至 quantum_website repo」段的 `sync_topics.py` 指令與 SSOT.D2 完整重複 → 改為「見 SSOT.D2–D4」引用（指令只餘 1 處）。
2. 「推送至 Streamlit Cloud」裸 `git commit && git push` 繞過 D3 GIT_ASKPASS／D4 push.sh → 改 hook 引用（規則衝突，非僅重複）。
3. 整合進來的 `src/views/skill_inventory/__init__.py` docstring 重述 SSOT 規則（selectbox→radio／直接呈現不折疊／相對路徑等）→ 改「遵循 SSOT A–E，見 SKILL.md，此處不重複」。
4. `data.py` 舊 showcase 路徑註解（「本 showcase 上一層」「skill_inventory_showcase/src/」）→ 改為 toolkit-viz 新路徑。

SSOT A–E 規則本體、定義+引用型重複、Logic check 歷史記錄均未動（核實判定為合理，非冗餘）。

### 驗證結果
- Gate 1 pre manifest `toolkit-viz-dedup-pre.sha256`（62/100 HIGH，178 findings 均為快照 JSON 惰性文字）
- Gate 2 RED `tests/test_no_redundant_rules.py` 4/4 失敗
- Gate 3 GREEN 4/4；sync_topics.py 指令 1 次、裸 git push 0 次
- Gate 4 cleanup：清 bytecode（py_compile 短暫產生的 11 個 .pyc 已清，SC8/SC9 消失）
- Gate 5 post audit 62/100（與 pre 同 findings，無新增）、drift 僅 4 個預期檔（較上輪整合更乾淨，無非預期 test_b2 變化）
- 既有測試仍 GREEN：`test_skill_inventory_integration.py` 4/4、`test_b2_direct_render.py` all checks
- py_compile PASS；expander/selectbox/use_container_width 實際呼叫全 0

### 上下級鏈影響
- 規則來源：toolkit-viz Streamlit SSOT A–E（唯一來源，本輪只去除重複副本，不改本體）。
- 上級：toolkit-viz skill U 修改（Gate 0–5）。
- 下級：`src/views/skill_inventory/` 的 docstring／路徑註解；`tests/test_no_redundant_rules.py`。

### 待辦／已知限制
- post audit 178 findings 為快照 JSON 惰性文字（PE3/AS3/AST3/AE4），與 pre 相同、非新增，如實記錄不誤判為本次引入。
- 未跑 `streamlit run` 實際 UI 渲染；無 commit/publish/push。

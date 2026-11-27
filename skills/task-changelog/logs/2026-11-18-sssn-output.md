# 新建 sssn-output 技能：列舉 session + 對話匯出 Markdown（TDD 全流程）

日期：2026-11-18
類型：feature
關聯 session：`ses_e31c0c0d2ffe1U0sLGPXeO41O7`（router）

## 背景與動機

使用者需求（`@writing-skills`）：① 能列舉 session、② 把「方法 A」（自動抓 session 轉 markdown）內建、③ 沉澱成 `sssn-output` skill。先前已在 `/home/sam/opencode-session-export/session-export-to-md.py` 做過一次性的 session→md 轉換，但那是 /tmp 起家的臨時腳本，且沒有 skill 讓代理在遇到「列 session / 備份對話 / compact 前存檔」時被觸發。本 skill 把可行流程 + 陷阱知識固化為可重用程序。

## 變更內容

- 新建 `/home/sam/.agents/skills/sssn-output/SKILL.md`（144 行）
- 新建 bundled tool `scripts/session-export-to-md.py`（273 行），由既有轉換器增強：保留已驗證的 render 邏輯，新增 `--list`（`--limit` 預設 50、`--top-only`、`--format json`，查 `session_v2`）、`--current`（讀 `$OPENCODE_SESSION_ID`）、DB 一律 `file:...?mode=ro` 唯讀；對「不帶 `--session` 的 fallback」加 stderr 警示
- SKILL.md 內容：Quick Reference 決策表（CLI list / `--list` / api GET / `--current` 四種列法的範圍與陷阱）、標準流程 3 步 + Step 2.5「最近更新 id 映射規則」、已知限制（有損 md / 不含 child / snapshot / 時區）、Common Mistakes 對照表、路徑慣例（`$SSSN` 絕對路徑）
- 稽核報告 `AUDIT.md`：SkillSpector 24/MEDIUM，3 個 issue 全溯源到同一行必要的 `subprocess.run(["opencode","session","export",sid])`，逐條判定良性 → APPROVE；sha256 manifest（2 核心檔）+ drift check PASS

## 開發方法（writing-skills RED → GREEN → REFACTOR）

- **RED**：3 個全新 context、無 skill 的 baseline subagent（不同問法：list+export、list only、CLI 語義），擷取 6 個共通失敗模式 F1–F6（不知有現成工具 / CLI list 70≠DB 188 / DB 表格陷阱 / 目前 id 找不到 / export 不含 child+有損 / 最近更新是移動標靶）。逐字證據記錄於 `/tmp/opencode/sssn-output-red-baseline.md`。
- **form 判斷**：失敗主因是「技術 how-to 缺口 + output 形狀」而非紀律違反 → 用 positive recipe + decision table，非 prohibition list（依 writing-skills「Match the Form to the Failure」）。
- **GREEN**：寫 minimal SKILL.md + bundled script；3 個 with-skill 對照 subagent（完整流程 / 目前 id / 陷阱问答）全部核心通過，皆避開 F1–F6，且正確引用 skill 章節。
- **REFACTOR**：3 個 GREEN 一致指出缺口 → 補 7 項：① 路徑慣例（`$SSSN` 絕對路徑，修「相對路徑找不到檔」）② Step 2.5 最近更新 id 映射規則（意圖三分 + 精確毫秒/parent_id 打破平手 + 必須揭露 top/child 選擇）③ `--list --limit 1000`（修預設 50 截斷）④ 數字標為撰寫時快照 ⑤ 不依赖 fallback 警告 ⑥ API `{"data":...}` 解析 ⑦ DB 硬編碼標註。
- **REFACTOR 重測**：全新 subagent 讀修改後 skill，4 題（路徑 / Step 2.5 / 快照標註 / 明確 id 實際匯出）全數通過；代理確認兩個缺口皆修好。

## 驗證結果

PASS：
- Quality checks：name 合法（sssn-output）、description 348 字（<500）、"Use when" 開頭、不-summarize 流程、frontmatter <1024、body 141 行、含 Quick Reference / Common Mistakes / 已知限制 / bundled script 引用
- 功能實測：`--list`、`--list --top-only --format json`、`--current`、`--session` 匯出（1596 則 / 2.5MB）、`--json` 全部實際跑通
- TDD：3 RED + 3 GREEN + 1 REFACTOR 重測 = 7 個 scenario，全數通過
- audit-skill：APPROVE（24/MEDIUM，3 issues 全良性且必要）、manifest drift check PASS
- 已由系統自動註冊為可用 skill（`<skill id="sssn-output">`）

## 產出檔案

- `/home/sam/.agents/skills/sssn-output/SKILL.md`
- `/home/sam/.agents/skills/sssn-output/scripts/session-export-to-md.py`
- `/home/sam/.agents/skills/sssn-output/AUDIT.md`
- `/tmp/opencode/sssn-output-red-baseline.md`（RED 證據）

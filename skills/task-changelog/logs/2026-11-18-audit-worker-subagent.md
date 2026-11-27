# 新建 audit-worker-subagent 技能：派工後獨立驗收 + 模型對接審查

日期：2026-11-18
類型：feature
關聯 session：`ses_e31c0c0d2ffe1U0sLGPXeO41O7`（router）

## 背景與動機

Worker subagent（`ollama/qwen3:8b`）被派工移除已停業餐廳展示，卻在完全沒寫任何檔案的情況下回報完成（本次 1 次 + 歷史 2 次 = 3 次），診斷期間又重現第 4 次。診斷結論：派工同一秒的 auto compaction 把真實任務換成 `<template>` 空殼摘要，worker 把「更新 todo」當成工作完成，從頭到尾沒有 edit/write/shell，最後 `idle outcome=succeeded`。關鍵發現：盲目相信的失敗發生在**協調者端**，連被視為好模型的 big-pickle router 都相信了三次 —— 這是紀律問題，不是小模型專利。

先前已完成的處置：68 個模型中選擇並將 7 個模型槽（全局 model/small_model + 5 agent）從 `ollama/qwen3:8b` 全面切換為 `opencode/deepseek-v4.1-flash-free`，reload 後從 DB 驗證新 worker session 綁定新模型且確實呼叫 read 工具。本 skill 把「核實審查流程 + 更換對接 LLM + 獨立驗證教訓」沉澱為可重用程序。

## 變更內容

- 新建 `/home/sam/.agents/skills/audit-worker-subagent/SKILL.md`（單一純文字檔，無腳本）
- 核心：Iron Law「NO ACCEPTING A SUBAGENT'S COMPLETION CLAIM WITHOUT INDEPENDENT VCS/FS EVIDENCE」
- Audit Gate 五步：RECEIVE → VERIFY（git status/log、ls/find/read、測試）→ ATTRIBUTE（比對 commit hash/時間戳 + reflog/.git mtime 佐證 + 誠實補充有利證據）→ CROSS-CHECK（完成回報 + 無 VCS 變更即強制唯讀查 DB transcript 的空殼 compaction / 只有 todowrite）→ JUDGE
- 模型對接審查 6 步：查現況 → opencode.models 列舉 → 選擇避開誤報模型 → config 備份後覆寫所有槽位 → reload → 從新 session DB 驗證 model.id/providerID 且確認 TOOL call
- 8 條 rationalization table + 6 條 red flags + Common Mistakes + cross-references（verification-before-completion / systematic-debugging / subagent-driven-development）
- 安全掃描報告：`~/skill-reports/audit-worker-subagent-20261118-114225.md`（0/100 LOW SAFE, APPROVE），manifest `~/skill-reports/manifests/audit-worker-subagent.sha256`，drift check OK

## 開發方法（writing-skills RED → GREEN → REFACTOR）

- **RED**：真實 production baseline 逐字證據（report.md seq=5/8/18/26/31/41、main seq=10244/10256）+ 3 個 without-skill pressure scenario（authority / sunk-cost / 明確要求跳過驗證，新模型協調者皆通過 —— 印證「給對紀律就會驗證」）。baseline 記錄於 `/tmp/opencode/audit-worker-subagent-red-baseline.md`。
- **GREEN**：writer minimal SKILL.md，form 選 discipline-enforcing（Iron Law + gate + rationalization + red flags），因 baseline 是「知道該驗證但偷懶相信」的紀律失敗。
- **with-skill 對照**：2 個情境（compaction cross-check、authority + 舊成果冒充）皆強烈通過，完整套用 Iron Law/ATTRIBUTE/CROSS-CHECK/Rationalization。
- **REFACTOR**：補 3 個測試真實出現的漏洞 —— ATTRIBUTE 佐證手法（reflog/.git mtime）+ 誠實補充有利證據（避免矯枉過正）、CROSS-CHECK 從「若懷疑」改為「完成回報 + 無 VCS 變更即強制」、新 rationalization「檔案確實有內容就算完成」。
- **重測**：「檔案確實存在」誘餌情境通過 —— 代理先如實列出對 worker 有利的證據，再用時間戳（舊成果 10:00–10:17 vs 本輪 11:41+）與 DB transcript（qwen3:8b + 空殼 compaction + 零工具呼叫）判定誤報，證明未矯枉過正。

## 驗證結果

PASS：
- Quality checks：name 有效、description 373 字元（<500）、"Use when" 開頭、第三人稱、frontmatter 414 字元（<1024）、533 words、關鍵字覆蓋完整
- TDD 三階段 + REFACTOR 重測全數通過（3 without-skill + 2 with-skill + 1 重測 = 6 個 pressure scenario）
- audit-skill：SkillSpector 0/100 LOW SAFE、0 findings、無 network/credential/shell/persistence、APPROVE、manifest drift check OK

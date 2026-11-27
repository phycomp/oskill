# 2026-11-18 — 驗證紀律推廣到 35 個技能

## 推廣 audit-worker-subagent 驗證紀律到 35 個技能（軟體 10 + 電磁 19 + QA 6）

- **日期**：2026-11-18
- **類型**：refactor + docs
- **涉及技能/檔案**（35 個 SKILL.md，皆只在檔尾新增段落）：
  - 軟體開發 10（`.agents/skills/`）：subagent-driven-development、dispatching-parallel-agents、finishing-a-development-branch、requesting-code-review、verification-before-completion（例外：只補 cross-ref + 本輪歸屬句）、ai-code-not-slop、executing-plans、receiving-code-review、test-driven-development、systematic-debugging
  - 電磁模擬/工程測試 19（`.opencode/skills/` 15 + `.agents/skills/` 2 + hub 2）：heatload-simulation、heatload-measurement、heatload-sop、heatload-units、heatload-coff-nist、electrical-test-sop、electrical-spec、nbtii-test-sop、component-integration、crosstalk-calc、connector、three-view、generic-qcable、quantum-cryogenic-cable、physim-topics、em-simulation-llm、em-llm、qcable-index(hub)、qcable-usage(hub)
  - 交付驗收/QA 6（`.agents/skills/`）：kpi-contract-impl、shorts-acceptance、audit-skill、character-animation-qa、contract-review、seo-audit
  - 輔助檔：`/tmp/opencode/audit-discipline-promotion-template.md`（統一範本）、`/tmp/opencode/verify-discipline-promotion.sh`（驗證腳本）

### 變更摘要

1. 溯源：沿用 `audit-worker-subagent` 已用真實 RED baseline 驗證過的 Iron Law（宣稱≠證據）與六要素（Iron Law／VERIFY／ATTRIBUTE／CROSS-CHECK／JUDGE／REQUIRED BACKGROUND），注入其它需要驗證的技能。
2. 先完成三大類盤點（軟體開發／電磁模擬／交付驗收），逐技能列出缺口、改法、優先級，經使用者逐項核准後才動檔；明確排除 `writing-plans`、`brainstorming`、`ljg-qa`（後者為問答提取誤匹配）。
3. 建立統一推廣範本與修改守則：只新增不改既有、語言跟隨、六要素逐字照抄、cross-ref 用技能名（技能分散兩個 root，不用絕對路徑）、各類客製行。
4. 3 個 worker 並行修改 35 檔（software 10／電磁 19／QA 6），全部在檔尾附加；hub 用「結果驗證紀律（總則）」標題省力覆蓋家族；`verification-before-completion` 因已有完整 Iron Law 走例外（只補單向 cross-ref + 本輪歸屬句）。
5. 高位技能客製 gate：軟體類加「empty diff / HEAD==base 即停、不派 reviewer 不給合併選單」；電磁類加「實際執行腳本 + 與 heatload-coff-nist 交叉比對 + 量級 sanity check（10mK<10μW/ch）+ PASS 附原始儀器檔」；QA 類加「只認本輪重跑、比對 verify.json mtime」；audit-skill / shorts-acceptance 另加與既有 False-positive discipline / Stop-the-line 相容的強化句。

### 驗證結果

- **35/35 結構驗證 PASS**（`verify-discipline-promotion.sh` v2）：cross-ref ≥1、REQUIRED BACKGROUND、六要素、驗證段落齊備；3 個例外（verification-before-completion 走 crossref 模式、qcable-usage 無 frontmatter、contract-review 非標準 frontmatter 在 line 6）經查證皆為**驗證腳本假設錯誤，非修改缺陷**。
- **只新增未改既有**：標題比對確認驗證段落是每個檔案唯一新增的 `##` 標題，既有標題全保留；git 追蹤檔 `git diff --numstat` 顯示 +15/0（ superconductivity 類因兩 skill root 皆 untracked，無 git 基線，改用行數差 + 頭部不變 + 標題清單比對佐證）。
- **audit-skill 全量掃描 35 檔**：27 檔 0–8/100 LOW SAFE；3 檔高分（subagent-driven-development 42 MEDIUM、systematic-debugging 77 HIGH、audit-skill 100 CRITICAL、heatload-coff-nist 100 CRITICAL）逐檔查 finding 行號（如 SDD 的 114/127、systematic-debugging 的 90/98/106/283、audit-skill 的 1–213、coff-nist 的 1/34/128/164）**全部落在驗證段落起始行之前**（分別 343/287/217/169），確認為既有內容（git clean -fdx、scripts 引用、Unicode frontmatter、__pycache__），本次新增段落未引入任何 finding。
- **壓力測試 A（軟體空 diff 場景）GREEN**：load `subagent-driven-development` + `audit-worker-subagent` 後，代理獨立重跑 `git status --porcelain`（空）、`git log cbfc0be..HEAD --stat`（空）、reflog（最新 commit 10:15 vs 現在 13:33）、README mtime（10:00 早於 commit）、DB `mode=ro` transcript 交叉查，判定空 diff = 舊成果冒充本輪 → 不派 reviewer、不給合併選單。
- **壓力測試 B（電磁無輸出場景）GREEN**：load `heatload-simulation` + background 後，代理對「50 μW/channel 可直接寫報告」保持不予採信；實際執行兩套模型貼出原始輸出，DK 10mK 段 ≈ 0.75–0.99 μW/ch、本地量測 ≈ 14.5 nW、MXC 整級冷卻僅 30 μW → 50 μW 超標 5 倍、與 coff-nist 差 50–67 倍、與量測差約 3600 倍且單通道超過整機冷卻功率 → 判定物理不可能，拒絕寫入報告，列出 4 項放行條件。
- **客製行對類抽查 PASS**：軟體（empty diff/reviewer）、電磁（coff-nist 交叉比對/sanity check）、hub（qcable-index + qcable-usage 總則）、QA（verify.json mtime）4 類代表皆正確；35 檔客製行涵蓋率檢查僅 verification-before-completion 例外（用本輪歸屬句等價物，已確認 line 128）。

### 上下級鏈影響

- 上級 ← `audit-worker-subagent`（唯一真相來源；35 檔全數 REQUIRED BACKGROUND 指回它，形成單向依賴星狀結構，避免路徑耦合）
- 下級 → 無（本次只加驗證紀律段落，不改既有流程邏輯）
- 雙向交叉引用：刻意只用技能名引用（skill name-based），因技能分散 `/home/sam/.agents/skills` 與 `/home/sam/.opencode/skills` 兩個 root，絕對路徑會隨部署失效。

### 待辦／已知限制

- 兩個 skill root 皆 git untracked，無機器級逐行 diff 證明「只新增」；已用行數 + 頭部 + 標題清單三重間接佐證，但非 hash 級證明。若需永久可稽核，建議將兩 root 納入版控或改動前 tar 快照。
- `verify-discipline-promotion.sh` v1 因 quoted heredoc 未展開 `$A/$O` 全數 FAIL、v2 因 sed 破壞路徑 — 均為驗證工具自身 bug，已修正後 35/35 PASS；此事本身再次印證「工具輸出也要獨立驗證」。
- 壓力測試 B 執行模型 import 更新了 `/home/sam/軟體/代理人/__pycache__/計算.cpython-314.pyc`（mtime 13:38），原始檔未變，屬執行必然副作用。
- audit-skill 全掃的 3 個 CRITICAL/HIGH 評級是既有內容既有 finding，未在本次「驗證紀律推廣」範圍內處置；不因掃描分數竄改既有技能。

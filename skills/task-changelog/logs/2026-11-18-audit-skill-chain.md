# 2026-11-18 — 技能鏈稽核技能建立

## 新建 audit-skill-chain 技能：技能鏈稽核契約與雙向證據表

- **日期**：2026-11-18
- **類型**：feature
- **涉及技能/檔案**：
  - `/home/sam/.opencode/skills/audit-skill-chain/SKILL.md` — 新建
  - `/home/sam/.opencode/skills/audit-skill-chain/references/audit-report-template.md` — 新建
  - `/home/sam/.opencode/skills/audit-skill-chain/references/checklist.md` — 新建
  - `/home/sam/.opencode/skills/audit-skill-chain/references/worked-example-heatload.md` — 新建
  - `/home/sam/.opencode/skills/task-changelog/logs/2026-11-18-audit-skill-chain.md` — 新建（本檔）

### 變更摘要

1. RED baseline（無專門技能時核實 qcable-index 定義的熱負載鏈）觀察到 7 個偏差：
   1. 缺結構化稽核思維——「讀到哪查哪」，PASS/FAIL 與證據表事後回頭整理（最主要）。
   2. MANIFEST 只跑 `sha256sum -c` 正向驗證，沒反向比對「實際檔案 vs MANIFEST 條目」。
   3. 雙向核實是被動的——看到「雙向可核實」這句才去 grep，沒先建逐邊雙向矩陣。
   4. 交叉引用不完整——沒系統列反引號路徑；`功能.xlsx` 到最後才查，程式入口靠全機 `find`。
   5. 只驗「能不能動」——只跑 `--list`（54 材料、exit 0），沒算係數對帳 Table 4 κ，沒讀原始碼確認實作等於公式。
   6. 沒質疑語意矛盾——「上級是論文，不可能反向引用技能」是寫報告時才意識到。
   7. 其他遺漏——版本號同步規則、註冊機制、git 狀態、heatload-sop 在索引出現兩次是否重複。
2. 依 `writing-skills` 的 **Match the Form to the Failure** 做 form matching 決策：
   - 歸類為「輸出形狀不對 + 遺漏必要元素」，正確形式是**正向契約／模板**（狀態報告是什麼、有哪些部分、按什麼順序 + REQUIRED 欄位插槽），不是 prohibition list。
   - 稽核報告表格定位為**查證過程的驅動結構**：先建空的逐邊×雙向×證據表，邊查邊填，而非查完再補。
   - 常見藉口對照表與 red flags 做為輔助自檢，不作主力（7 個 RED 偏差逐條對應）。
3. 建立 `audit-skill-chain/`：`SKILL.md`（The Contract 八段 + 7 步 recipe + 常見藉口對照表 + red flags + 職責切分）+ 3 個 references（報告模板／檢查清單／完整 worked example）。
4. worked example 來源：真實 heatload 鏈查證結果（查證日期 2026-11-18），如實呈現 4 個真實缺陷：
   - 語意不閉合：索引 L20「單向鏈」vs `heatload-coff-nist` L148「雙向可核實」；實測僅 `qcable-index ↔ heatload-coff-nist` 真雙向，其餘 4 個下級技能（simulation/measurement/units/sop）SKILL.md 完全不提索引或相鄰節點。
   - MANIFEST 漏檔：`00_熱負載總覽.md` 與 `Quantum_Microwave_Stripline_Thermal_Calculator.xlsx` 未列（正向 6/6 仍全綠）。
   - `功能.xlsx` 矛盾：索引 L33 引用不存在檔案，與 `00_總覽.md:L53–54`「未納入」衝突。
   - 溯源路徑不可解析：`pages/10nist低溫庫.py`／`pages/16柔性八階擬合.py` 現址不存在。
   - 如實標註非缺陷：`heatload-sop` 在索引 L46、L74 各一次為刻意重複（不同分類），避免技能誤判。

### 驗證結果

- 技能建立與檔案齊全：OK（4 個新檔皆建立，frontmatter `name` 與目錄名相符，已被技能發現機制認得）。
- 真實查證指令：`sha256sum -c` 6/6、`comm` 反向差集、`grep -rn` 逐邊雙向、`--list` 54 項、實際 `--coeffs` 計算 exit 0、原始碼 `thermal_load.py:L62–63/L79` 等於 `SKILL.md:L20` 公式 — PASS（實際輸出已貼於 worked example）。
- **整體技能效果：PASS（REFACTOR 壓力場景對照已完成）** — 派 3 個 fresh-context subagent 對照驗證：Control（無技能，`ses_e1360a1b9ffdqe8OutSh7BF6n1`）、Treatment A（有技能／task-changelog 機制，`ses_e1360a19dffeUu13B1HAWdvD8c`）、Treatment B（有技能／toolkit-viz 資料鏈，`ses_e1360a199ffeR5CDAAvopov0fW`）。兩 treatment 皆先建表後查證（A：9 節點+17 邊；B：11 邊查證前固定）、逐邊雙向、MANIFEST 正反向即使 N/A 仍跑 `comm` 差集、內容對帳、語意質疑、如實揭露限制；Control 則自白「讀到哪查哪、報告事後整理、雙向 ad-hoc、反引號最後補做」。兩 treatment 都在壓力下被技能拉回：A 在「快速帶過」誘惑下補齊八段並抓 3 真問題；B 在「最後一天直接簽核」催促下，見 py_compile/AppTest/count 全綠仍被契約拉回，抓「重建刪手工條目／宣告 4 來源實作 3 來源／43 vs 41-42 口徑矛盾」等 7 項並拒絕簽核。技能有效。

### 上下級鏈影響

- 本技能為稽核者，不改動既有技能內容；稽核對象是 `qcable-index` 定義的熱負載鏈。
- 上級 ← `writing-skills`（form matching／TDD GREEN 方法論）、`task-changelog`（日誌契約）。
- 下級 → `references/worked-example-heatload.md`（引用真實熱負載鏈查證結果）。
- 職責切分：`audit-skill`（單一技能安全掃描）、`hierarchy-visualization`／`skill-hierarchy-viewer`（畫依賴圖、不稽核判定）皆不重複。

### 待辦／已知限制

- REFACTOR 已完成（3 路對照如上），結論：技能有效、不需大幅微調。細部強化（見下方 CHANGELOG）已補入 checklist：①非技能節點的「字面命中」不等於結構性反向引用（Treatment A 的 E1/E2 誤判風險）；②單向資料流鏈的 #2 應標「契約不適用」而非硬套真雙向（Treatment B）。
- Treatment 查出的稽核對象缺陷（非本技能缺陷）：toolkit-viz 的索引口徑 41/42/43 矛盾、全量重建刪手工條目、src/views 4 檔斷鏈、功能.xlsx 不存在、缺 name/version frontmatter；task-changelog 索引缺驗證狀態欄。這些屬各技能自身待修項，本技能如實記錄不代修。
- worked example 中「獨立 Table 4 κ 數值對帳」本機無資料，如實標「未驗證」，未偽裝 PASS。
- 版本號同步規則查無明確規範；`git status` 顯示 `.opencode/` 整體未追蹤，如實揭露。

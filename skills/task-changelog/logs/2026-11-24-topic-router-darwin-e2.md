# 2026-11-24 — topic-router 達爾文 E1/E2 驗收：4 勝 0 負、keep、總分 88.1

## 背景
延續 `topic-router`（v1.0.0）重構後的進化驗收。E0 已做（0 錯 0 警 0 提示）；本輪補 E1 讀評 + E2 實跑盲評，依照 `darwin-skill` 3.0（9 維 rubric、keep/revert 棘輪、執行者／評委互斥、反例 #8 事實大於票數）。本輪為 darwin 盲評唯一例外，派 3 位獨立子 agent 當評委；其餘全流程 native。全程 no commit／no publish／no push。

## 變更內容

### 1. 測评準備（Phase 0–1）
- W = `/tmp/opencode/topic-router-eval-20261124`；s0 快照 md5 `bc4d530e8b23fd5723a592a6f6991799` 與原件一致，無檢查項外洩。
- `test-prompts.json` 4 條（dev-1/dev-2 source=real 取自使用者真實需求；holdout-1=user、holdout-2=doc），checks 共 17。

### 2. E2 實跑與對照純度
- 8/8 執行者完成（4 測試 × 帶 skill／裸跑），產 answer.md + transcript.md。
- dev-1 裸跑污染（自行 `read s0/SKILL.md`）隔離至 `audit/dev-1-contaminated/`，乾淨重跑；x/dev-1 污染路徑稽核 0；A/B 12-gram Jaccard 全 0。

### 3. 盲評與 tally
- `darwin.py pair --seed 20261124` 隨機 A/B，移除 3 份 `e0-check.txt` 來歷線索，24 檔材料；3 評委（j3 加「核實 skill 路徑真實性」指令）只讀各自 jN 目錄。
- `tally`：4 勝 0 平 0 負；檢查項 a=11 b=17；SKILL.md 11742→11742 位元組（+0%）；裁決 keep（嚴格更好）。

### 4. 事實指控核實（darwin 反例 #8）
- 9 條 fact_claim 逐條驗證（A/B 按 key 解碼組別）。
- 勝者 s0 的 4 條**全不成立**：`e0-check.txt` 原始檔確實存在（盲評遮蔽時人為移除才讓評委看不到）、`quota-mnpl` 確實存在於 `.opencode/skills`（SSOT 只收自行開發 26 筆故不在內）。
- 敗者裸跑組的 5 條**成立**：把已 deprecated 的 `topic-post` 當現行 child（frontmatter `deprecated: true` / `replaced_by: topic-distill`）、把 `para-memory-files` symlink 底層平台層誤判給 `skill-family`（s0 §5 明指 `paperclip-router`）。
- 事实方向與票數方向一致 → keep 不翻盤。

### 5. E1 讀評與總分
- 9 維：dim1=9、dim2=9、dim3=8、dim4=9、dim5=8、dim6=9、dim7=8、dim8=10、dim9=9。
- dim8 換算：dev 集 9/9 × 10 = 10（全部 17 項亦全過），多數勝無封頂。
- **總分 88.1 / 100**。結構短板：§3/§4 輕微重複、缺 if-fail 降級分支——僅診斷排序，依反例 #5 不為湊分改動。

### 6. 產出與索引同步
- W：`e1.md`（九維讀評＋行為證據）、`e2-report.md`（完整評估報告）、`tally-output.txt`、`votes/r1/j1-3.json`。
- `darwin-skill/results.tsv` 新建（baseline／verify-s0／final 三列）。
- `task-changelog`：本日誌＋`log-index.md` 累計 15（原統計 12 低估 2，本次如實校正）＋`CHANGELOG.md` 同步。

## 驗證
- tally：4 勝 0 平 0 負、檢查項 17 vs 11，工具輸出 `裁決：keep（嚴格更好）`（PASS）。
- 事實核實：9/9 條完成驗證（PASS）。
- dim8 換算：dev 9/9、全部 17/17（PASS）。
- s0 快照 md5 與原件一致；無檢查項外洩（PASS）。
- no commit／no publish／no push（PASS）。

## 上下級鏈影響
- 上級：`darwin-skill`（進化規則 owner）、`chain-skill`（六階段閉環）。
- 下級：`topic-router`（本次驗收對象，v1.0.0 未改本體）。
- 交叉引用：`topic-post`（deprecated 事實來源）、`paperclip-router`（symlink 底層 parent）。

## 待辦／已知限制
- E3 真機未跑：`topic-router` 涉及 Obsidian 批次改寫／knowledge base 重整，屬不可逆，需 human checkpoint。
- commit/push 阻塞：mono-repo 無 origin、`gh` 未安裝；近期變更多在本機未提交。
- 舊續辦：monthly timer Task 2、social/viz slot、`skill-logic-check.service`（exit=1）。

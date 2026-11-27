# 2026-11-24 — 家族 router 批次重構：quant-algo-auto 拆解 + vid-router + paperclip-router + 索引同步

## 背景
延續 skill-family 統一 parent（goal→hook）與 chain-skill 六階段 + darwin-skill E0-E3 進化規則，把本機自行開發 skill 家族逐一收斂到單一 router 入口，不另開發重複技能。allow-list SSOT = `~/.config/skill-timer/self-developed.list`。全程 native 執行（no worker/subagent）。

## 變更內容

### 1. quant-algo-auto 拆解 deprecated（交易面＋頻道面＋影片面）
- 核實：`quant-algo-auto` 交易面與既有 `quant-risk-bt` 100% 重複（`backtest-checklist.md` / `risk-rules.md` / `strategy_template.py` 三位元組完全相同）；唯一未覆蓋資產為 `references/content-plan.md`（量化頻道選題）。
- 新建 `quant-channel`（v1.0.0）承接唯一獨有層：內容支柱／12 週 content plan／SEO 標題／頻道 KPI；`content-plan.md` 遷入其 `references/`。
- `quant-algo-auto` 設 `deprecated: true` + `replaced_by: "quant-risk-bt + quant-channel (+ yt-vid)"` + description `[DEPRECATED]` + 正文 banner；保留原文供追溯（依 `skill-router` 先例）。
- 引用同步：`quant-risk-bt`（Not for channel → quant-channel / yt-vid）、`quant-viz`（頻道營運 → quant-channel / yt-vid）、`yt-vid`（引用改為 quant-risk-bt + quant-channel）、`quant-router`（goal→hook、child 盤點、Version Log 1.0.1）。

### 2. vid-router 建立（影片家族 parent）
- 新建 `vid-router`（v1.0.0）：goal→hook 收斂 vid-xxx／xxx-vid／video-*／video-autopilot／remotion-* 共 30+ child；分群＝全流程調度／素材取得／腳本分鏡／配音視覺／剪輯翻譯／Pipeline／Remotion／發布。
- `video-agent-jianying-editor` 已 deprecated（→ `video-agent-editor`），標註不為現行 hook。
- HyperFrames／Shorts 家族各有自己的 parent，明確標為跨家族、不重複 hook。

### 3. paperclip-router 建立（公司營運 + 市場家族 parent）
- 盤點：`paperclip-*`（6 項：本體／board／converting-plans-to-tasks／create-agent／deploy-push／launch）+ `market-*`／`marketing-*`（13 項）皆未被任何 router hook。
- 新建 `paperclip-router`（v1.0.0）：goal→hook 收斂兩群；設計邏輯＝paperclip 為公司/agent 組織骨架、market 為行銷職能，合為「公司營運 + 市場」複合家族。
- 雙父節點防護：`video-market-analysis` 主父標為 `vid-router`（影片脈絡），paperclip-router 僅行銷視角跨家族參考、不重複 hook。
- `paperclip-create-agent` 在 `.agents`/`.claude` 雙路徑，標註以 `.agents` 為主來源。

### 4. allow-list / 索引同步
- allow-list SSOT += `quant-channel`、`vid-router`、`paperclip-router`（candidate 同步，diff 一致）。
- `chain-skill` Inventory 新增 router 行 + deprecated 標註；`skill-family` Index／Routing／Need-based predicate／hook 表／Function Set／Cross-family 表／Version Log（1.1.1→1.1.3）同步。
- `topic-workflow-auto` 補 YAML frontmatter 並設 `deprecated: true`（S1–S6 → topic-distill/distill-router + ytauto/social-post/push-streamlit/gws-drive-upload + audit-*）。

## 驗證
- darwin E0：`paperclip-router`／`vid-router`／`quant-router`／`quant-channel`／`chain-skill` 皆 **0 錯誤 0 警告 1 提示**（提示＝缺 test-prompts.json，可選）；`skill-family` 0 錯誤 2 既有警告（description 觸發場景、`scripts/push.sh` 引用），非本次引入。
- hook 目標存在性：paperclip-router 引用 20 個候選全部存在，缺失 0。
- allow-list：25/25 行，主檔與 candidate 一致；router 在列 10 個。
- 雙父檢查：`video-market-analysis` 主父 vid-router 標註一致。
- 全程 no commit / no publish / no push（mono-repo 無 origin、`gh` 未安裝；skill-timer invariant：report-only）。

## 待辦／裁決
- commit/push 阻塞：mono-repo 無 origin、`gh` 未安裝，所有變更多在本機未提交。
- `skill-family` 既有 2 警告是否處理（description 觸發場景、`scripts/push.sh` 引用忽略與否）。
- 舊續辦：monthly timer Task 2 install/enable、social/viz slot、`skill-logic-check.service` 手動 start（exit=1）。
- E2 實跑盲評／E3 真機尚未對新 router 執行（目前僅 E0）；依 darwin 棘輪需 E2 增益才保留微調。

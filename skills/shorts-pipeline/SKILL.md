---
name: shorts-pipeline
description: Use when the user wants to run or plan an end-to-end Short-form video pipeline (topic selection, production, acceptance, caption/upload packages, YouTube upload, scheduling/weekly ops) for a Traditional-Chinese investment/finance or similar channel, or asks to 選訂主題、製作 Shorts、驗收、產出上傳包、上傳影片（unlisted 預設）、每週更新、短影音流程、Shorts pipeline、upload/verify/schedule Shorts, especially when they need safe handoffs and stop-the-line rules.
---

# Shorts Pipeline（端到端調度）

全域可移植的 Shorts 流程入口。`~/ytauto` 是**參考實作範例**，不是唯一真相；以工作區設定與腳本契約為準。

## 決策點（先判斷）

1. **目標是什麼？** 選題/寫規格 → `shorts-production`；已有成品要檢查 → `shorts-acceptance`；要上傳 → 先確認驗收 PASS，再選上傳路線。
2. **上傳路線？** 有可用 Studio 瀏覽器登入 profile 且接受 UI 風險 → `youtube-studio-browser-upload`。有自有 OAuth 用戶端且授權可用 → `youtube-oauth-upload`。都不穩或要人工發佈 → 使用 `upload_package/` 手動上傳。卡住時 → `shorts-upload-troubleshooting`。
3. **排程？** `publishAt` 僅規範欄位/語意與範本；**不自動部署排程器**。API 路線才較可控，瀏覽器路線排程不可靠。
4. **隱私預設？** 一律 `unlisted`（或專案設定的 `privacy_default`）；**不自動轉 public**，金融/敏感內容需人工確認。

## 端到端流程（交棒順序）

```
[1] 選訂主題 → content/<slug>.json（或等價規格）
      ↓ 交棒 shorts-production
[2] 製作 → output/<slug>/（video/thumbnail/captions/metadata/subtitle/upload_package）
      ↓ 交棒 shorts-acceptance
[3] 驗收 → verify.json + 報告；verdict 必須 PASS
      ↓ PASS 才可繼續；FAIL 拒絕上傳並回到 [1]/[2]
[4] 上傳包/上傳 → 依路線交棒 browser 或 oauth skill；預設 unlisted
      ↓ 寫入 upload_result.json / upload_summary.json
[5] 核對 → Studio/YouTube 連結、隱私、標題、頻道、排程狀態
[6] 留言/社群/週報 → 依專案 ops 流程（非本技能自動執行）
```

## 契約與指令（參考實作：`~/ytauto`）

工作區可透過 `--config`、`--workspace`、`YTAUTO_*`、`.ytauto/config.json` 或 `ytauto.config.json` 參數化（優先序：CLI > env > 專案設定檔 > 預設）。

```bash
# 範例（~/ytauto）
cd ~/ytauto
make build                              # 或 python scripts/make_shorts.py --all|--slug <slug>
python scripts/verify_shorts.py --all   # 必須 PASS 才可上傳
python scripts/upload_browser.py --login
python scripts/upload_browser.py --slug <slug>   # unlisted, 需 PASS
python scripts/upload_youtube.py --check
python scripts/upload_youtube.py --slug <slug> --dry-run
```

關鍵輸出：`output/<slug>/verify.json`、`output/<slug>/upload_result.json`、`output/upload_summary.json`（`schema_version=1`）。

## 已知限制（D1/D2，誠實揭露）

- **OAuth/API：** 自有 OAuth 用戶端可能遇同意畫面驗證/Test users 阻擋（歷史案例：`qcryo` 專案）；`gcloud` ADC 路線不可用於 YouTube 上傳 scope。需依 Google 規範設定測試使用者/驗證狀態。
- **瀏覽器/Studio：** UI 可能變動（selector/scrim）；曾出現「儲存中…」但無 `video-id`、next button hidden、3 秒測試片重現等阻塞。無法確認 `videoId`/狀態時**不得宣稱成功**。
- **排程：** API `publishAt` 需符合 YouTube 狀態限制（通常排程公開需合規隱私狀態與未來時間），以 YouTube 實際結果為準；瀏覽器排程不可靠。
- **內容：** 可能無授權 BGM；字幕/旁白品質依規格與 TTS；金融內容不可自動公開。

## Stop-the-line（不可違反）

- 驗收 `verify.json` 非 PASS → **拒絕上傳**，指出 `verify.json` 路徑與失敗數。
- 頻道/帳號非目標 `channel_id` → **中止**，不宣稱成功。
- 無 `videoId`、逾時、或狀態不可確認 → **failed/pending_manual + 存證**，不盲目重試。
- 未經人工確認 → **不轉 public**。

## 交棒

| 情境 | 交棒到 |
|---|---|
| 寫規格、TTS/圖卡/ffmpeg/字幕/縮圖/metadata | `shorts-production` |
| 48 項檢查、verify.json、拒傳判定 | `shorts-acceptance` |
| Playwright Studio 上傳、profile、video-id 驗證 | `youtube-studio-browser-upload` |
| OAuth client/consent/token、API 上傳、publishAt | `youtube-oauth-upload` |
| 儲存中無 video-id、scrim/selector、草稿、授權阻擋 | `shorts-upload-troubleshooting` |

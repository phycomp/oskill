---
name: youtube-oauth-upload
description: Use when the user wants to upload or schedule a Short/video via the YouTube Data API with an OAuth client (desktop app credentials), manage auth/token/consent/test-user blockers, check target channel, run dry-run uploads, or use publishAt with API constraints, or asks to 用 API 上傳、OAuth 上傳、upload_youtube、client_secret/token、授權失敗、Test users、排程 publishAt，especially when channel mismatch or unverified consent must stop the flow.
---

# YouTube OAuth Upload（API 上傳）

可移植的 YouTube Data API 上傳技能。`~/ytauto/scripts/upload_youtube.py` 為參考實作。需**自有 OAuth 用戶端**；`gcloud` ADC 路線不適用於 `youtube.upload`（歷史限制）。

## 決策點

1. **驗收 PASS？** 缺 `verify.json` 或 `verdict != PASS` → 拒絕上傳（交回 `shorts-acceptance`）。`--dry-run` 仍應遵守專案安全策略；若實作允許 dry-run 檢查欄位，明確標示未上傳。
2. **憑證與路徑？** `client_secret_path`/`token_path` 由設定決定（CLI > env > 專案設定檔 > 預設）。參考相容預設：`~/.config/ytauto/client_secret.json`、`~/.config/ytauto/token.json`。**不得提交/列印憑證內容**。
3. **授權狀態？** 先 `--check`/授權流程。若遇同意畫面驗證/Test users 阻擋（D1 歷史案例：`qcryo`）→ 停止，說明需在 Google Cloud 專案設定測試使用者/驗證狀態，或改走瀏覽器/手動上傳包。
4. **頻道核對？** 授權後頻道必須等於目標 `channel_id`。不符 → **中止**，不宣稱成功。
5. **隱私與排程？** 預設 `unlisted`。`publishAt`（ISO8601）僅在 API 路線較可控，且需符合 YouTube 規則（通常排程公開需合規隱私狀態與未來時間；實際以 API/Studio 結果為準）。

## 契約與指令（參考實作）

```bash
# 範例（~/ytauto）
cd ~/ytauto
python scripts/upload_youtube.py --auth-manual      # 無瀏覽器/跨裝置
python scripts/upload_youtube.py --auth             # 可開瀏覽器
python scripts/upload_youtube.py --check            # 核對授權與目標頻道
python scripts/upload_youtube.py --slug <slug> --dry-run
python scripts/upload_youtube.py --slug <slug> --privacy unlisted
python scripts/upload_youtube.py --slug <slug> --privacy private --publish-at 2026-11-11T04:00:00Z
python scripts/upload_youtube.py --all
# 可選：--config .ytauto/config.json --workspace .
```

保留既有核心旗標相容（`--auth`、`--auth-manual`、`--check`、`--all`、`--slug`、`--privacy`、`--publish-at`、`--dry-run`）。結果寫入 `output/<slug>/upload_result.json`（`schema_version=1`, `backend=api`），批次寫 `output/upload_summary.json`。

## 結果語意

- `uploaded`：API 成功且有 `videoId`/URL（仍建議到 Studio 核對內容/隱私/排程）。
- `dry_run`：未上傳。
- `failed`：驗收未通過、頻道不符、API/授權錯誤等；`videoId`/`url` 應為 `null`。
- 不得憑空填入 `videoId`。

## 已知限制（D1）

- **OAuth 同意畫面/Test users 阻擋：** 專案未完成驗證或未加入測試使用者時，授權會失敗（歷史案例：`qcryo`）。這是帳號/專案設定問題，非盲重試能解。
- **ADC 限制：** `gcloud`/Cloud SDK ADC 路線不可用於 `youtube.upload`；需自有 OAuth 用戶端。
- **`publishAt`：** YouTube 對排程狀態有規則；API 接受不等於排程符合預期，必須事後核對。
- **配額/權限：** YouTube API 配額、scope、帳號狀態可能導致失敗；失敗要存證/記錄錯誤，不宣稱成功。

## 交棒

- 驗收未 PASS → `shorts-acceptance`。
- 需要瀏覽器手動/半自動上傳 → `youtube-studio-browser-upload`。
- 授權阻擋、排程困惑、結果不明 → `shorts-upload-troubleshooting`。
- 製作/規格 → `shorts-production`。
- 端到端調度 → `shorts-pipeline`。

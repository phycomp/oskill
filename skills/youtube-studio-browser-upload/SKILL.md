---
name: youtube-studio-browser-upload
description: Use when the user wants to upload a Short/video to YouTube Studio through browser automation (Playwright/profile), verify Studio UI state, handle login/profile/channel checks, or debug browser upload selectors/scrim/non-kids/visibility/video-id, or asks to 用瀏覽器上傳、YouTube Studio 上傳、upload_browser、Playwright 上傳、Studio 草稿/儲存、取得 video-id，especially when stop-the-line evidence is required and success must not be assumed.
---

# YouTube Studio Browser Upload（瀏覽器上傳）

可移植的 Studio 瀏覽器上傳技能。`~/ytauto/scripts/upload_browser.py` 為參考實作；UI 會變動，必須以「可確認證據」判斷結果。

## 決策點（上傳前）

1. **驗收 PASS？** 先確認 `output/<slug>/verify.json` 的 `verdict == PASS`。未 PASS → 拒絕上傳（交回 `shorts-acceptance`）。
2. **目標頻道明確？** 設定 `channel_id`/`channel_name`（或等價欄位）必須指向目標頻道。Studio 當前頻道不符 → **中止**。
3. **登入/profile 可用？** 需要已登入的瀏覽器 profile（參考：`browser_profile_dir` / `--login`）。不得索取密碼、不得輸出 cookie/profile 私密內容。
4. **隱私與排程？** 預設 `unlisted`；不自動轉 `public`。`--publish-at` 在瀏覽器路線**不保證可靠**，只能視為風險/存證輔助；要可靠排程優先 `youtube-oauth-upload`。
5. **能否承擔 UI 變動風險？** Studio selector/scrim/步驟可能改版；失敗時走 `shorts-upload-troubleshooting`，不要盲重試。

## 契約與指令（參考實作）

```bash
# 範例（~/ytauto）
cd ~/ytauto
python scripts/upload_browser.py --login                    # 一次性登入，profile 存於設定路徑
python scripts/upload_browser.py --slug <slug>              # 需 verify PASS，預設 unlisted
python scripts/upload_browser.py --all
python scripts/upload_browser.py --slug <slug> --debug      # 排查
python scripts/upload_browser.py --slug <slug> --config .ytauto/config.json --workspace .
# 可選逾時（若實作支援）：--save-timeout / --video-id-timeout
# 可選：--publish-at ISO8601（僅記錄風險/存證，不保證可靠）
```

每次上傳應寫入 `output/<slug>/upload_result.json`（`schema_version=1`, `backend=browser`），並在批次寫 `output/upload_summary.json`。成功狀態僅 `uploaded`，且需可確認 `videoId`。**Schema 裁決：** `failed` / `pending_manual` 時，必要欄位 `videoId` / `url` **必須為 `null`**；任何未驗證的候選 ID/URL 僅可放在 `evidence` 或額外欄位，**不得**填入必要欄位（D1 誠實、無虛假成功）。

## Studio 操作要點（會漂移，僅作參考）

- 入口/遮罩：可能需處理 `tp-yt-iron-overlay-backdrop` 的 pointer-events/scrim；被遮罩擋住時避免盲點擊。
- 檔案輸入：Studio 可能使用動態 `input[type=file]` / file picker；依實作策略設定檔案。
- 必填：標題/說明、**非兒少內容**（例如 `VIDEO_MADE_FOR_KIDS_NOT_MFK`）、可見度（`UNLISTED`）。
- 步驟：DETAILS → VIDEO_ELEMENTS → CHECKS → VISIBILITY；以實際可見狀態判斷，不硬編等待。
- 完成：需確認 `videoId`/Studio edit URL/可見度/標題等證據。

## Stop-the-line（不可違反）

- 驗收未 PASS → 拒絕上傳。
- 頻道不符 → 中止，不上傳、不宣稱成功。
- **無 `videoId`、儲存中逾時、dialog 狀態不明、無法確認可見度/標題** → 結果必須是 `failed` 或 `pending_manual`，附上存證（截圖、dialog 文字/HTML、URL、log 路徑等）；必要欄位 `videoId`/`url` **必須 `null`**，未驗證候選僅可留在 `evidence`/額外欄位，**不得宣稱成功**，**不得盲目重試**。
- 有 `videoId` 但驗證不足（標題/隱私/狀態未確認） → 至少 `pending_manual`/需人工確認；不虛報完全成功。
- 不得製造/累積未確認草稿後假裝完成；連續操作前清理 stale browser/profile lock 依實作策略。

## 已知限制（D1）

- Studio UI 可能改版，selector 會失效；歷史阻塞包括「儲存中…」無 `video-id`、`#next-button` hidden、scrim 擋住、短測試片仍卡住。
- 瀏覽器自動化存在反自動化/網路/帳號狀態不確定性；OAuth/API 路線通常更可驗證（但有授權門檻）。
- 截圖/DOM 存證不得包含敏感憑證；若畫面可能含個資，僅保存必要片段並妥善存放。

## 交棒

- 驗收問題 → `shorts-acceptance`。
- 製作/規格問題 → `shorts-production`。
- 需要 API/OAuth 或可靠排程 → `youtube-oauth-upload`。
- 儲存中無 video-id、selector 漂移、草稿、連續重試風險 → `shorts-upload-troubleshooting`。
- 整體調度 → `shorts-pipeline`。

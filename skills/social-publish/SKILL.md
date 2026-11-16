---
name: social-publish
description: "社群發佈技能：小紅書/Facebook/LINE/Instagram/TikTok 發佈貼文、成立群組、下載相簿，含 API 設定與 OAuth。Use when the user wants to publish to social media, create groups, download albums, or manage social media content."
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---
# Social Publish — 社群發佈

## 功能
- `發佈貼文(平台, 內容, 圖片)`：發佈貼文。
- `成立群組(平台, 群組名, 描述)`：成立群組。
- `下載相簿(平台, URL, 輸出路徑)`：下載相簿。
- `line_login(token)`：LINE 登入。
- `下載LINE相簿(群組ID, 日期, 輸出路徑)`：下載 LINE 群組特定日期相簿。
- `測試社群功能()`：測試所有功能。
- `列出平台()` / `取得平台資訊(平台)`。

## 平台
| 平台 | API | 認證 |
|------|-----|------|
| xiaohongshu | xiaohongshu.com | OAuth |
| facebook | graph.facebook.com | OAuth |
| line | api.line.me | Token |
| instagram | graph.instagram.com | OAuth |
| tiktok | open.tiktokapis.com | OAuth |

## 使用
```python
from social_media import 發佈貼文, 成立群組, 下載相簿, 列出平台
print(列出平台())
發佈貼文("facebook", "Hello", ["img.jpg"])
成立群組("line", "My Group", "desc")
下載相簿("instagram", "https://...", "./downloads")
```

## 觸發條件
- 「社群發佈」「social publish」「小紅書」「Facebook」「LINE」「發佈貼文」「成立群組」「下載相簿」
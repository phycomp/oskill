---
name: fb-app-post
description: Use when posting to Facebook via Graph API, setting up Facebook App for page posting, obtaining Page Access Token with pages_manage_posts permission, or troubleshooting Facebook API posting errors. Triggers include "Facebook 發文", "Graph API 發文", "Page Access Token", "pages_manage_posts", "Facebook App 設定", "fb-app-post", "臉書自動化貼文".
---

# fb-app-post — Facebook Graph API 自動發文

## 核心原則

**Facebook Graph API 不支援個人動態發文**（自 2018 年 Cambridge Analytica 事件後移除 `publish_actions`）。所有自動化發文必須透過 **Facebook Page** + **Page Access Token** + **`pages_manage_posts` 權限**。

## 腳本總覽

| 腳本 | 職責 |
|------|------|
| `scripts/fb_post.py` | Graph API 發文（文字/連結/圖片） |
| `scripts/fb_token_check.py` | Token 驗證與權限檢查 |
| `scripts/fb_page_setup.py` | Page 建立引導與 Token 取得 |

## 前置條件

### 1. Facebook App 設定

**App 類型必須為「Consumer」或「Business」，不能是「Games」。**

遊戲 App 不支援 `pages_manage_posts` 權限。

#### 建立 App 步驟
1. 前往 https://developers.facebook.com/apps/
2. 點擊「建立 App」
3. 選擇 **「Consumer」** 或 **「Business」**（⚠️ 不要選「Games」）
4. 填寫 App 名稱和聯絡信箱
5. 建立完成後，記下 **App ID** 和 **App Secret**（設定 → 基本）

#### 加入產品
6. 左側選單 → **「產品」** → **「新增產品」**
7. 加入 **「Facebook Login」**
8. 加入 **「Pages API」**

#### 設定測試者
9. 左側選單 → **「角色」** → **「測試者」** → 新增您的 Facebook 帳號

### 2. 取得 Page Access Token（帶有 pages_manage_posts）

#### 步驟
1. 前往 **https://developers.facebook.com/tools/explorer/**
2. 右上角選擇您的 App
3. 在「權限」欄位，搜尋並勾選：
   - ✅ `pages_manage_posts`（**關鍵**）
   - ✅ `pages_manage_metadata`
   - ✅ `pages_read_engagement`
   - ✅ `pages_show_list`
4. 點擊 **「Generate Access Token」**
5. 登入並授權
6. 執行 `GET /me/accounts?fields=id,name,access_token`
7. 找到您的 Page，複製 `access_token`

#### 驗證 Token
```bash
python3 -c "
import requests, json
token = 'YOUR_PAGE_TOKEN'
r = requests.get('https://graph.facebook.com/v19.0/debug_token', params={'input_token': token, 'access_token': token})
data = r.json()
scopes = data.get('data', {}).get('scopes', [])
print('Scopes:', scopes)
print('Has pages_manage_posts:', 'pages_manage_posts' in scopes)
"
```

**必須確認 scopes 中包含 `pages_manage_posts`。**

## 發文

### 基本發文

```bash
python3 ~/.agents/skills/social-post/scripts/fb_post.py \
  --message "貼文內容" \
  --page-token "YOUR_PAGE_TOKEN" \
  --page-id "YOUR_PAGE_ID"
```

### 發文腳本 (fb_post.py)

```python
#!/usr/bin/env python3
"""Facebook Graph API 自動發文"""
import argparse, json, os, requests, sys

def post_to_facebook(page_id, access_token, message, link=None, image_path=None, dry_run=False):
    if dry_run:
        print(f"[DRY RUN] 將發文到 Page {page_id}:")
        print(f"  內容: {message[:200]}")
        if link:
            print(f"  連結: {link}")
        if image_path:
            print(f"  圖片: {image_path}")
        return {"dry_run": True}

    url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    params = {"access_token": access_token, "message": message}

    if link:
        params["link"] = link

    if image_path:
        photo_url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
        with open(image_path, 'rb') as f:
            files = {"source": f}
            photo_resp = requests.post(photo_url, data={"access_token": access_token, "published": "false"}, files=files)
            photo_data = photo_resp.json()
            if "id" in photo_data:
                params["attached_media"] = json.dumps([{"media_fbid": photo_data["id"]}])
            else:
                print(f"圖片上傳失敗: {photo_data}")
                return photo_data

    resp = requests.post(url, data=params)
    result = resp.json()

    if "id" in result:
        print(f"發文成功！Post ID: {result['id']}")
        print(f"連結: https://www.facebook.com/{result['id']}")
    else:
        print(f"發文失敗: {result}")

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Graph API 自動發文")
    parser.add_argument("--page-id", required=True, help="Facebook Page ID")
    parser.add_argument("--page-token", required=True, help="Page Access Token")
    parser.add_argument("--message", "-m", required=True, help="貼文內容")
    parser.add_argument("--link", "-l", help="連結")
    parser.add_argument("--image", "-i", help="圖片路徑")
    parser.add_argument("--dry-run", action="store_true", help="測試模式，不實際發文")
    args = parser.parse_args()

    post_to_facebook(args.page_id, args.page_token, args.message, args.link, args.image, args.dry_run)
```

### Token 檢查腳本 (fb_token_check.py)

```python
#!/usr/bin/env python3
"""Facebook Token 驗證與權限檢查"""
import argparse, json, requests, sys

def check_token(token):
    r = requests.get("https://graph.facebook.com/v19.0/debug_token",
                     params={"input_token": token, "access_token": token})
    data = r.json().get("data", {})
    print(f"Token 類型: {data.get('type', 'N/A')}")
    print(f"App: {data.get('application', 'N/A')} (ID: {data.get('app_id', 'N/A')})")
    print(f"有效: {data.get('is_valid', False)}")
    scopes = data.get("scopes", [])
    print(f"Scopes: {scopes}")
    print(f"Has pages_manage_posts: {'pages_manage_posts' in scopes}")
    if "pages_manage_posts" not in scopes:
        print("\n⚠️ 缺少 pages_manage_posts 權限！")
        print("請在 Graph API Explorer 中新增此權限並重新生成 Token。")
        return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Facebook Token 檢查")
    parser.add_argument("--token", "-t", required=True, help="Access Token")
    args = parser.parse_args()
    ok = check_token(args.token)
    sys.exit(0 if ok else 1)
```

## 錯誤對策表

| 症狀 | 對策 |
|------|------|
| `Invalid Scopes: publish_pages` | 使用 `pages_manage_posts`（新版權限名稱） |
| `(#200) ... requires pages_manage_posts` | Token 缺少 `pages_manage_posts`，重新取得帶有此權限的 Token |
| `Can only call this method on valid test users` | App 類型為 Games，需建立 Consumer/Business 類型 App |
| `Unsupported get request` | App 不存在或類型不支援，檢查 App ID 與類型 |
| Token 無效/過期 | 重新生成 Token（短期 1-2h，長期 60 天） |
| 2FA 阻擋瀏覽器自動化 | 使用 Graph API Explorer 手動取得 Token |
| `(#152) Invalid Page Category` | 使用正確的 Facebook Page 類別名稱 |

## 常見問題

**Q: 為什麼不能發文到個人動態？**
A: Facebook 自 2018 年 Cambridge Analytica 事件後移除了 `publish_actions` 權限。個人動態發文必須透過瀏覽器自動化或手動操作。

**Q: Page Access Token 會過期嗎？**
A: 如果 User Token 是長期的（60 天），Page Token 不會過期。短期 User Token（1-2h）產生的 Page Token 也會短期有效。

**Q: 如何取得長期 Token？**
A: 使用 `GET /oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN`

**Q: App 類型為什麼重要？**
A: Games 類型 App 的可用權限受到限制，不支援 `pages_manage_posts`。Consumer 或 Business 類型才有完整權限。

## 參考資源

- Facebook Graph API: https://developers.facebook.com/docs/graph-api
- Pages API: https://developers.facebook.com/docs/pages-api
- Pages Manage Posts: https://developers.facebook.com/docs/permissions/reference/pages_manage_posts
- Graph API Explorer: https://developers.facebook.com/tools/explorer/
- App Dashboard: https://developers.facebook.com/apps/
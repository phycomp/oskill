#!/usr/bin/env python3
"""Facebook Graph API 自動發文"""

import argparse, json, os, sys, requests


def post_to_facebook(
    page_id, access_token, message, link=None, image_path=None, dry_run=False
):
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
        with open(image_path, "rb") as f:
            files = {"source": f}
            photo_resp = requests.post(
                photo_url,
                data={"access_token": access_token, "published": "false"},
                files=files,
            )
            photo_data = photo_resp.json()
            if "id" in photo_data:
                params["attached_media"] = json.dumps(
                    [{"media_fbid": photo_data["id"]}]
                )
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

    post_to_facebook(
        args.page_id, args.page_token, args.message, args.link, args.image, args.dry_run
    )

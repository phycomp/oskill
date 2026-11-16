#!/usr/bin/env python3
"""Facebook Token 驗證與權限檢查"""

import argparse, json, requests, sys


def check_token(token):
    r = requests.get(
        "https://graph.facebook.com/v19.0/debug_token",
        params={"input_token": token, "access_token": token},
    )
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

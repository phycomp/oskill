# Skill: remotion-social

# Remotion Social — 社群平台錄製與 Remotion 整合技能

## 目標
使用 Playwright 錄製社群/平台登入與操作流程，轉換為 MP4，並整合至 Remotion 視頻專案。

## 核心流程

```
[目標平台 URL + 操作流程]
 -> 1. Playwright 錄製 (WebM, 1920x1080, slow_mo)
 -> 2. Cursor 視覺化注入 (CSS + JS)
 -> 3. Cookie banner 自動 dismiss
 -> 4. 等待 networkidle + 適當延遲
 -> 5. FFmpeg 轉換 WebM -> MP4 (h264, CRF 18, slow preset)
 -> 6. 移動至 Remotion public/demos/
 -> 7. Remotion <Video> 組件引用
```

## 錄製腳本範本

```python
import asyncio
from playwright.async_api import async_playwright

async def record(url, output_dir="/tmp/opencode/recordings"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=80,
            args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=output_dir,
            record_video_size={"width": 1920, "height": 1080},
        )
        page = await context.new_page()
        # Inject cursor visualization
        await page.add_init_script("...cursor CSS/JS...")
        # Navigate
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)
        # Dismiss cookie banners
        # ... cookie selectors ...
        # Custom actions
        await page.wait_for_timeout(2000)
        await context.close()
        await browser.close()

asyncio.run(record())
```

## FFmpeg 轉換

```bash
ffmpeg -y -i recording.webm -c:v libx264 -crf 18 -preset slow -movflags faststart output.mp4
```

## Remotion 整合

```tsx
import { Video, staticFile } from "remotion";

export const Demo = () => (
  <Video src={staticFile("demos/recording.mp4")} />
);
```

## 已完成範例

### Streamlit Cloud 登入流程
- 腳本：/home/sam/軟體/代理人/scripts/record_streamlit_login.py
- 輸出：/tmp/opencode/streamlit_login.mp4 (28s, 1920x1080, h264)
- 流程：首頁 -> 滾動 -> 登入按鈕 -> 跳轉 -> 回首頁

## 觸發條件
- 「Remotion 錄製」「社群錄製」「瀏覽器錄製」「login recording」
- 「streamlit login」「錄製流程」「demo video」
- 「remotion-social」「錄製轉換」「webm to mp4」

## 依賴
- Playwright (chromium)
- FFmpeg (libx264)
- Remotion (Video component)

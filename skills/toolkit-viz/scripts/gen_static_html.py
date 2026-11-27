#!/usr/bin/env python3
"""Generate static HTML index from collected topics."""
import json, sys
from pathlib import Path

INDEX = Path(__file__).parent.parent / "data" / "topics_index.json"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist")

def main():
    topics = json.loads(INDEX.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    html = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><title>Toolkit Viz</title>
<style>body{font-family:sans-serif;max-width:900px;margin:0 auto;padding:20px;}
.topic{border:1px solid #ddd;border-radius:8px;padding:15px;margin:10px 0;}
.topic h2{margin:0 0 10px;} .meta{color:#666;font-size:0.9em;}
a{color:#0066cc;}</style></head><body>
<h1>📚 Toolkit Viz — 蒸餾成果展示</h1>
"""
    for name, info in sorted(topics.items()):
        html += f'<div class="topic"><h2>{name}</h2>'
        html += f'<p class="meta">來源: {info["source"]} | 檔案數: {info["count"]}</p>'
        html += f'<p>路徑: <code>{info["path"]}</code></p>'
        html += '<ul>'
        for f in info.get("md_files", []):
            html += f'<li>{Path(f).name}</li>'
        html += '</ul></div>\n'
    html += "</body></html>"
    (OUT / "index.html").write_text(html)
    print(f"Generated {OUT / 'index.html'} ({len(topics)} topics)")

if __name__ == "__main__":
    main()

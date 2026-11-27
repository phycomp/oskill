#!/usr/bin/env python3
"""Generate Markdown index from collected topics."""
import json, sys
from pathlib import Path

INDEX = Path(__file__).parent.parent / "data" / "topics_index.json"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("README.md")

def main():
    topics = json.loads(INDEX.read_text())
    lines = ["# Toolkit Viz — 蒸餾成果索引\n", f"\n> 生成日期：{__import__('datetime').date.today()}\n", "\n## 主題清單\n"]
    for name, info in sorted(topics.items()):
        lines.append(f"\n### {name}")
        lines.append(f"- 來源：{info['source']}")
        lines.append(f"- 檔案數：{info['count']}")
        lines.append(f"- 路徑：`{info['path']}`")
        for f in info.get("md_files", []):
            lines.append(f"  - {Path(f).name}")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"Generated {OUT} ({len(topics)} topics)")

if __name__ == "__main__":
    main()

"""RED/GREEN：toolkit-viz skill 內不得殘留展開式元件的字串與用法。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
APP = ROOT / "app.py"
TOKEN = "exp" + "ander"  # 避免測試原始碼自身出現字面字串


def main():
    skill = SKILL.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    section_b = skill.split("### B. 互動元件強制規則", 1)[1].split("### C.", 1)[0]

    texts = {
        p.relative_to(ROOT): p.read_text(encoding="utf-8")
        for p in ROOT.rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and "tests" not in p.parts
        and p.name != "SKILL.md"  # SKILL.md 的 B2 已單獨檢查；Logic check 屬歷史敘述
        and p.suffix in (".md", ".py")
    }

    checks = [
        ("B2 為直接呈現規則", "直接呈現（不折疊）" in section_b),
        (
            f"skill 內無 {TOKEN} 字串",
            all(TOKEN not in t.lower() for t in texts.values()),
        ),
        ("app.py 無 with 包裹", "with st." not in app),
    ]

    failed = []
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}: {name}")
        if not ok:
            failed.append(name)

    if failed:
        print(f"RED: {len(failed)} check(s) failed")
        return 1
    print("GREEN: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

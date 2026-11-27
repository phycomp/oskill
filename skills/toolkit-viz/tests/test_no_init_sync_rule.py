"""RED/GREEN：toolkit-viz SSOT A 節不得再有 __init__.py/app.py 同步規則。"""

import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def main():
    text = SKILL.read_text(encoding="utf-8")
    section_a = text.split("### A. 架構與狀態", 1)[1].split("### B.", 1)[0]
    checks = [
        ("無「保持與 app.py 一致」", "保持與 `app.py` 一致" not in section_a),
        ("無「__init__.py 同步」條目", "**`__init__.py` 同步**" not in section_a),
        ("相對路徑已遞補為 A4", "4. **相對路徑**" in section_a),
        ("A 節不再有第 5 條", "5. **" not in section_a),
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

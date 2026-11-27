"""RED/GREEN：涉及 credential 的 push repo 必須推至 private repo。"""

import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def main():
    text = SKILL.read_text(encoding="utf-8")
    section_0 = text.split("## 0. 鐵律", 1)[1].split("## 1. Parent Node", 1)[0]
    checks = [
        ("R1 §0 明定 credential 情境", "credential" in section_0.lower()),
        ("R2 §0 明定 private repo", "private repo" in section_0.lower()),
        (
            "R3 §0 禁止 public repo",
            (
                "不得 push 至 public" in section_0
                or "public repo 視為未授權" in section_0
            ),
        ),
        ("R4 description 含 private 觸發詞", "private" in text.split("---")[1].lower()),
        ("R5 version 升 1.2.0", 'version: "1.2.0"' in text),
        ("R6 changelog 記錄", "1.2.0" in text.split("## Version Log")[-1]),
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

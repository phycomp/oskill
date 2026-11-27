"""RED/GREEN：「更新演示工具」為 toolkit-viz 直接實作觸發字眼（免 §E 提案等待）。"""

import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def main():
    text = SKILL.read_text(encoding="utf-8")
    trigger = text.split("## 觸發條件", 1)[1].split("## Streamlit 規則", 1)[0]
    section_e = text.split("### E. 寫入前 Gate", 1)[1].split("## 鐵律", 1)[0]
    logic_lines = [
        line for line in text.splitlines() if line.startswith("Logic check:")
    ]
    checks = [
        ("T1 觸發條件含「更新演示工具」", "更新演示工具" in trigger),
        ("T1b 觸發條件含演示graphify工具", "演示graphify工具" in trigger and "演示graphify" in trigger),
        ("T2 §E 含直接實作例外", "直接實作" in section_e),
        ("T3 §E 例外明確引用觸發字眼", "更新演示工具" in section_e),
        (
            "T4 §E 例外明示免提案免等待",
            ("免提案" in section_e or "不需提出" in section_e)
            and ("免等待" in section_e or "不需等待" in section_e),
        ),
        ("T5 §E 保留其餘情況的提案等待", "停止並等待明確裁決" in section_e),
        (
            "T6 Logic check 記錄本輪裁決",
            any("更新演示工具" in line for line in logic_lines),
        ),
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

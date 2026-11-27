"""RED/GREEN：quantum-website D 節須為推送/部署唯一來源（自 toolkit-viz SSOT.D 搬移）。"""

import sys
from pathlib import Path

TV_SKILL = Path("/home/sam/.opencode/skills/toolkit-viz/SKILL.md")
NEW_SKILL = Path("/home/sam/.opencode/skills/quantum-website/SKILL.md")


def main():
    text = NEW_SKILL.read_text(encoding="utf-8")
    tv = TV_SKILL.read_text(encoding="utf-8")
    section_d = tv.split("### D. 發布與同步", 1)[1].split("### E.", 1)[0]
    checks = [
        ("D1 repo 事實卡", "Repo 事實卡" in text),
        ("D2 sync_topics 閘門", "sync_topics.py" in text),
        ("D3 push-repo hook", "push-repo" in text),
        ("D5 Streamlit Cloud", "Streamlit Cloud" in text),
        ("D5 HF Spaces", "HF Spaces" in text),
        ("D5 Kaggle Dataset", "Kaggle" in text),
        ("既有 Known Issues 已移除", "已知問題與解決方案" not in text),
        ("push-streamlit 標為已合併來源", "push-streamlit" in text),
        (
            "toolkit-viz D 節只留指標",
            "quantum-website" in section_d and "sync_topics.py" not in section_d,
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

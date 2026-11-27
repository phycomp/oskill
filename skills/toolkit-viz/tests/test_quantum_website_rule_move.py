"""RED/GREEN：toolkit-viz SSOT.D 搬移至 quantum-website 技能，舊引用同步更新。"""

import sys
from pathlib import Path

OP = Path("/home/sam/.opencode/skills")
AG = Path("/home/sam/.agents/skills")
NEW = OP / "quantum-website" / "SKILL.md"
TV = OP / "toolkit-viz" / "SKILL.md"


def live_lines(path):
    """排除 Logic check 歷史行（依使用者裁決保留原樣）。"""
    text = Path(path).read_text(encoding="utf-8")
    return "\n".join(l for l in text.splitlines() if "Logic check:" not in l), text


def test_new_skill_exists():
    checks = [
        ("新技能目錄存在", NEW.is_file()),
        (
            "frontmatter name",
            NEW.is_file()
            and "name: quantum-website" in NEW.read_text(encoding="utf-8"),
        ),
        (
            "description 以 Use when 開頭",
            NEW.is_file()
            and 'description: "Use when' in NEW.read_text(encoding="utf-8"),
        ),
    ]
    return checks


def test_new_skill_rules():
    if not NEW.is_file():
        return [("新技能規則出處", False)]
    t = NEW.read_text(encoding="utf-8")
    anchors = [
        "D1. Repo 事實卡",
        "D2. 同源同步閘門",
        "D3. Git",
        "D4. 提交與推送腳本",
        "D5. 三個部署目標",
        "D6. 驗證",
        "D7. 除錯與預防",
        "git remote get-url origin",
        "sync_topics.py",
        "GIT_ASKPASS",
        "push.sh",
        "push_hf_space.sh",
        "push_kaggle_dataset.sh",
        "_stcore/health",
        "data/topics_index.json",
        "Repository not found",
        "## 觸發條件",
        "## 歷史追溯",
        "Logic check: 2026-11-26",
    ]
    return [(f"新技能含 {a}", a in t) for a in anchors]


def test_toolkit_viz_pointer_only():
    t = TV.read_text(encoding="utf-8")
    section_d = t.split("### D. 發布與同步", 1)[1].split("### E.", 1)[0]
    checks = [
        ("D 節指向 quantum-website", "quantum-website" in section_d),
        (
            "D 節指向新技能 SKILL.md",
            "quantum-website/SKILL.md" in section_d or "`quantum-website`" in section_d,
        ),
    ]
    for forbidden in [
        "Repo 事實卡",
        "sync_topics.py",
        "git remote get-url origin",
        "phycomp/quantum-website",
        "GIT_ASKPASS",
        "Streamlit Cloud",
        "HF Spaces",
        "Kaggle",
    ]:
        checks.append((f"D 節已移除 {forbidden}", forbidden not in section_d))
    return checks


def test_history_lines_kept():
    _, t = live_lines(TV)
    kept = [
        "quantum_website 不在寫入範圍",
        "來源取已去折疊、相對 import 已修復的 `quantum_website/src/views/skill_inventory/` 移植版",
        "改為「見 SSOT.D2–D4」引用",
        "`quantum_website` 未觸碰",
    ]
    return [(f"歷史行保留 {k[:20]}", k in t) for k in kept]


def test_cross_skill_refs():
    cases = [
        (OP / "da-xue/SKILL.md", ["`toolkit-viz` SSOT.D"], ["`quantum-website`"]),
        (OP / "stock-market/SKILL.md", ["`toolkit-viz` D 節"], ["`quantum-website`"]),
        (OP / "topic-distill/SKILL.md", ["`toolkit-viz` D 節"], ["`quantum-website`"]),
        (
            OP / "topic-distill/references/02_提示詞範例.md",
            ["push-streamlit 技能", "topic-post × push-streamlit"],
            ["quantum-website 技能"],
        ),
        (
            OP / "topic-distill/references/00_完整流程.md",
            ["push-streamlit 技能"],
            ["quantum-website 技能"],
        ),
        (
            OP / "push-streamlit/SKILL.md",
            [
                "replaced_by: toolkit-viz",
                "toolkit-viz` D 節",
                "由 toolkit-viz D 節引用",
            ],
            ["replaced_by: quantum-website", "Logic check: 2026-11-26"],
        ),
        (
            AG / "push-router/SKILL.md",
            [
                "`toolkit-viz`（D 節）",
                "`toolkit-viz`（D 節，",
                "`toolkit-viz` D 節",
                "`toolkit-viz` (D 節)",
            ],
            ["`quantum-website`"],
        ),
        (
            AG / "topic-post/SKILL.md",
            ["`toolkit-viz` D 節"],
            ["`toolkit-viz` SSOT.C", "`quantum-website`"],
        ),
        (
            AG / "skill-dependency-hook/SKILL.md",
            ["`toolkit-viz` D 節", "`toolkit-viz` (D 節)", "toolkit-viz (D 節"],
            ["`quantum-website`"],
        ),
        (AG / "viz-router/SKILL.md", ["`toolkit-viz` (D 節)"], ["`quantum-website`"]),
        (AG / "skill-family/SKILL.md", ["`toolkit-viz` (D 節)"], ["`quantum-website`"]),
        (AG / "skill-seek/SKILL.md", ["`toolkit-viz`（D 節）"], ["`quantum-website`"]),
        (
            AG / "chain-skill/SKILL.md",
            ["`toolkit-viz` (D 節)", "`toolkit-viz` D 節"],
            ["`quantum-website`"],
        ),
        (
            OP / "social-media-suite/SKILL.md",
            ["`toolkit-viz` (D 節)", "toolkit-viz (D 節)"],
            ["`quantum-website`"],
        ),
        (
            OP / "sci-router/SKILL.md",
            ["`toolkit-viz` D 節", "`toolkit-viz` (D 節)"],
            ["`quantum-website`"],
        ),
        (
            OP / "audit-credential/SKILL.md",
            ["`toolkit-viz` (D 節)"],
            ["`quantum-website`"],
        ),
        (
            OP / "ai-ml-app-engineering/SKILL.md",
            ["toolkit-viz D5", "`toolkit-viz` D 節"],
            ["`quantum-website`"],
        ),
    ]
    checks = []
    for path, forbidden, required in cases:
        text, full = live_lines(path)
        checks.append(
            (
                f"{path.parent.name}/{path.name} 無舊引用",
                all(f not in text for f in forbidden),
            )
        )
        checks.append(
            (
                f"{path.parent.name}/{path.name} 有新引用",
                all(r in full for r in required),
            )
        )
    return checks


def test_legacy_tests_updated():
    for name in [
        "test_deployment_merge.py",
        "test_no_redundant_rules.py",
        "test_topic_index_default_no_register.py",
    ]:
        p = OP / "toolkit-viz/tests" / name
        checks = [
            (
                f"{name} 改指向新技能",
                p.is_file() and "quantum-website" in p.read_text(encoding="utf-8"),
            )
        ]
    return checks


def main():
    groups = [
        ("新技能存在", test_new_skill_exists),
        ("新技能規則", test_new_skill_rules),
        ("toolkit-viz 只留指標", test_toolkit_viz_pointer_only),
        ("歷史行保留", test_history_lines_kept),
        ("跨技能引用", test_cross_skill_refs),
        ("舊測試更新", test_legacy_tests_updated),
    ]
    failed = []
    for title, fn in groups:
        print(f"--- {title} ---")
        for name, ok in fn():
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

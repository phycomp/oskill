from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def test_moat_rule_present():
    text = SKILL.read_text(encoding="utf-8")
    assert "護城河檢核" in text
    assert "moat" in text.lower()
    assert "假說" in text
    assert "切換成本" in text
    assert "網路效應" in text


def test_moat_trigger_in_description():
    text = SKILL.read_text(encoding="utf-8")
    # frontmatter description should expose moat-related triggers
    lower = text.lower()
    assert "護城河" in text
    assert "moat" in lower or "defensibility" in lower

"""rev-skill fix3 RED→GREEN：驗證 push-repo 的
『Policy-based auto-push：預先授權載體取代每次 push 字眼』規則節存在。"""
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def _text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_policy_section_exists():
    assert "Policy-based auto-push" in _text()


def test_three_authorization_carriers():
    t = _text()
    for carrier in ["automation", "allow-list", "systemd"]:
        assert carrier in t, f"缺少授權載體: {carrier}"


def test_carrier_equals_gate1_authorization():
    t = _text()
    assert "等同" in t and "gate 1" in t
    assert "明確授權" in t


def test_no_carrier_falls_back_to_gate1():
    t = _text()
    assert "載體不存在" in t or "無有效載體" in t
    assert "退回" in t and "gate 1" in t


def test_fail_closed():
    t = _text()
    assert "fail-closed" in t or "任一項不過就停" in t


def test_policy_still_bound_by_gate2_credential_private():
    """政策自動 push 仍受 gate 2 credential private 約束，不可繞過。"""
    t = _text()
    assert "仍受" in t and "gate 2" in t
    assert "private" in t


def test_logic_check_fix3():
    assert "Logic check: 2026-11-26 (fix3)" in _text()

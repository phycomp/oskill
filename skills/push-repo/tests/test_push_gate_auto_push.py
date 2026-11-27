"""rev-skill RED→GREEN：驗證 push-repo 的
『五項 gate 全綠 → 自動 push（免再次核准）』規則存在於 SKILL.md。"""
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def _text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_push_gate_section_exists():
    assert "## Push 時機：五項 gate 全綠 → 自動 push（免再次核准）" in _text()


def test_five_gates_listed():
    t = _text()
    for token in ["明確授權", "remote 就緒", "commit 完成且驗證通過", "機密檢查通過", "一批一次"]:
        assert token in t, f"缺少 gate: {token}"


def test_auto_push_no_reapproval_rule():
    t = _text()
    assert "五項全數成立" in t
    assert "不需再次核准" in t


def test_logic_check_record():
    assert "Logic check: 2026-11-26" in _text()

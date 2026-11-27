"""rev-skill fix4 RED→GREEN：驗證政策載體承認 type:shell（本機 git 唯一可達路徑）。

fix3 規則節僅承認 type:code，但 type:code 只能呼叫 box.shell（遠端 /workspace、無 .git），
碰得到本機 /home/sam repo 的只有 type:shell。修正承認 type:shell 並維持 fail-closed。
"""

from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "weekly_gate_check.sh"


def _text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_shell_carrier_recognized():
    """政策表要含 type:shell 載體列與本機可達說明。"""
    t = _text()
    assert "type:shell" in t or 'type:"shell"' in t
    assert "本機" in t


def test_shell_carrier_fail_closed():
    """type:shell 載體仍 fail-closed 不豁免 gate 2-5。"""
    t = _text()
    assert "fail-closed" in t
    assert "type:shell" in t or 'type:"shell"' in t


def test_shell_carrier_readonly_mode():
    """type:shell 示範為只讀檢查，不 stage/commit/push。"""
    t = _text()
    assert "只讀" in t and "不 push" in t


def test_weekly_script_exists():
    assert SCRIPT.exists(), "缺少 scripts/weekly_gate_check.sh"


def test_logic_check_fix4():
    assert "Logic check: 2026-11-26 (fix4)" in _text()

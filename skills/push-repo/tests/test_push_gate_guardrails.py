"""rev-skill fix2 RED→GREEN：驗證 4 項 side-effect／merge 防護規則存在於 SKILL.md。

修補上一輪「五項 gate 全綠自動 push」核實出的 4 個風險：
1. credential repo 必須 private（push-router §0.6）
2. 精確 stage 白名單，禁用 git add -A（避免誤收其它流程變更）
3. gate 1 限本次 session 明確意圖（不沿用舊授權）
4. Phase 5 分支名稱用變數，不硬編碼 main
"""
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


def _text() -> str:
    return SKILL.read_text(encoding="utf-8")


def test_gate2_credential_repo_must_be_private():
    """風險1：五項 gate 的 gate 2 要含 credential repo 必須 private。"""
    t = _text()
    assert "credential repo 一律 private" in t or "必須 private repo" in t
    assert "含 credential" in t or "涉及 credential" in t


def test_gate5_explicit_stage_no_add_all():
    """風險2：gate 5 要寫精確 stage 白名單，明確禁用 git add -A。"""
    t = _text()
    assert "精確 stage" in t
    assert "git add -A" in t and ("禁用" in t or "不得" in t)


def test_gate1_session_scoped_no_old_auth():
    """風險3：gate 1 要限本次 session，移除『授權涵蓋五項成立即自動 push』永久授權讀法。"""
    t = _text()
    assert "本次 session" in t
    assert "不沿用舊授權" in t or "不沿用前次" in t


def test_phase5_branch_variable_not_hardcoded_main():
    """風險4：Phase 5 push 指令不得硬編碼 main，要用分支變數。"""
    t = _text()
    assert "push -u origin main" not in t
    assert "push -u origin \"$BRANCH\"" in t or "push -u origin <branch>" in t


def test_logic_check_fix2():
    assert "Logic check: 2026-11-26 (fix2)" in _text()

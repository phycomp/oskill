"""RED/GREEN：4 處冗餘規則去除的驗收測試。

修正前應 RED（4 項失敗），修正後 GREEN。
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
NEW_SKILL = Path("/home/sam/.opencode/skills/quantum-website/SKILL.md")
INIT = ROOT / "src" / "views" / "skill_inventory" / "__init__.py"
DATA = ROOT / "src" / "views" / "skill_inventory" / "data.py"


def test_no_duplicate_sync_command():
    """#1: sync_topics.py 指令只能出現在新技能 D2（一次），不得重複。"""
    text = NEW_SKILL.read_text(encoding="utf-8")
    n = text.count("scripts/sync_topics.py")
    assert n == 1, (
        f"sync_topics.py 指令出現 {n} 次（應只 1 次，位於 quantum-website D2）"
    )


def test_no_bare_git_push():
    """#2: 不得有裸 git push 繞過 GIT_ASKPASS/push.sh。"""
    text = NEW_SKILL.read_text(encoding="utf-8")
    assert 'git commit -m "sync" && git push' not in text, (
        "仍有裸 git push（應 hook D3/D4）"
    )


def test_no_ssot_rules_echoed_in_view_docstring():
    """#3: bundled view 的 docstring 不得重述 SSOT 規則。"""
    text = INIT.read_text(encoding="utf-8")
    for cue in ("selectbox→radio", "直接呈現不折疊", "同源快照不編造", "相對路徑"):
        assert cue not in text, f"__init__.py docstring 重述 SSOT 規則：{cue}"


def test_no_stale_showcase_path_note():
    """#4: data.py 不得殘留 showcase 舊路徑註解。"""
    text = DATA.read_text(encoding="utf-8")
    for cue in ("本 showcase", "skill_inventory_showcase/src/"):
        assert cue not in text, f"data.py 殘留舊 showcase 路徑註解：{cue}"


if __name__ == "__main__":
    checks = [
        ("#1 sync 指令唯一", test_no_duplicate_sync_command),
        ("#2 無裸 git push", test_no_bare_git_push),
        ("#3 view docstring 不重述 SSOT", test_no_ssot_rules_echoed_in_view_docstring),
        ("#4 無舊 showcase 路徑註解", test_no_stale_showcase_path_note),
    ]
    failed = 0
    for name, fn in checks:
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as e:
            failed += 1
            print(f"RED  {name}: {e}")
    print(f"RED {failed}/4" if failed else "GREEN 4/4")
    raise SystemExit(1 if failed else 0)

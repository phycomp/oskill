"""RED 測試：skill_inventory 整合入 toolkit-viz 的驗收條件。

整合前此檔應失敗（RED）：視圖目錄不存在、app.py 無路由。
整合後應通過（GREEN）。fixture 來源唯讀，永不刪使用者檔。
"""

from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
VIEW_DIR = SKILL / "src" / "views" / "skill_inventory"
APP = SKILL / "app.py"
SNAPSHOT = SKILL / "data" / "skill_inventory_viz_data.json"


def test_skill_inventory_view_dir_exists():
    assert (VIEW_DIR / "data.py").is_file()
    assert (VIEW_DIR / "__init__.py").is_file()
    assert (VIEW_DIR / "views").is_dir()
    for name in ("overview", "types", "hierarchy", "uncertain", "catalog"):
        assert (VIEW_DIR / "views" / f"{name}.py").is_file(), name


def test_no_expander_in_integrated_views():
    assert VIEW_DIR.is_dir(), "整合視圖目錄不存在，無從驗證無折疊"
    assert list(VIEW_DIR.rglob("*.py")), "整合視圖目錄內沒有 .py"
    for py in VIEW_DIR.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        text = py.read_text(encoding="utf-8")
        assert "expander" not in text, f"{py.name} 仍有 expander（違反 SSOT.B.2）"


def test_app_has_skill_inventory_route():
    text = APP.read_text(encoding="utf-8")
    assert "skill_inventory" in text
    assert "render_skill_inventory" in text
    assert "skill_inventory_sidebar" in text


def test_snapshot_exists():
    assert SNAPSHOT.is_file()
    assert "skill_inventory" in SNAPSHOT.name
    assert SNAPSHOT.stat().st_size > 1000

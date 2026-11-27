"""同源資料載入與降級顯示。

唯一資料來源（SSOT）：``skill_inventory_viz_data.json``（相對於本模組上溯三層的 ``data/``）。
本模組只讀取與驗證快照，不在視圖中另存副本、不重擬合、不編造欄位。
缺檔／讀取失敗／欄位異常時把原因寫入 bundle["errors"] 並降級顯示。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

# data.py 位於 toolkit-viz/src/views/skill_inventory/；上溯三層即 toolkit-viz/ 根。
REPO_ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT_PATH = REPO_ROOT / "data" / "skill_inventory_viz_data.json"

# 視圖所需的頂層欄位與預期型別；只做驗證，不補值。
_EXPECTED: dict[str, type] = {
    "meta": dict,
    "views": list,
    "overview": dict,
    "types": dict,
    "hierarchy": dict,
    "origin": dict,
    "skills": list,
    "deliverables": list,
    "reproduce": str,
    "errors": list,
}


@st.cache_data(show_spinner=False)
def _load_snapshot(path_str: str) -> dict[str, Any]:
    """讀取 JSON 並驗證必要欄位，回傳統一的 snapshot / errors / available。"""
    errors: list[str] = []
    snapshot: dict[str, Any] = {}
    path = Path(path_str)

    if not path.is_file():
        errors.append(f"找不到同源快照：{path}")
        return {"snapshot": snapshot, "errors": errors, "available": False}

    try:
        with path.open(encoding="utf-8") as fh:
            loaded = json.load(fh)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"讀取同源快照失敗：{path}（{type(exc).__name__}: {exc}）")
        return {"snapshot": snapshot, "errors": errors, "available": False}

    if not isinstance(loaded, dict):
        errors.append(f"同源快照根節點不是物件：{path}（實際 {type(loaded).__name__}）")
        return {"snapshot": snapshot, "errors": errors, "available": False}

    snapshot = loaded

    # JSON 自身的 errors 一併轉為可追蹤訊息（可能為空陣列）。
    own_errors = snapshot.get("errors", [])
    if isinstance(own_errors, list):
        for item in own_errors:
            errors.append(f"快照內建錯誤：{item}")
    elif own_errors:
        errors.append(f"快照 errors 欄位型別異常：{type(own_errors).__name__}")

    for key, expected in _EXPECTED.items():
        if key not in snapshot:
            errors.append(f"缺少必要欄位：{key}")
        elif not isinstance(snapshot[key], expected):
            errors.append(
                f"欄位型別異常：{key} 預期 {expected.__name__}，"
                f"實際 {type(snapshot[key]).__name__}"
            )

    # 嵌套欄位異常也記入 errors；視圖本身以安全取值降級，不中斷渲染。
    for parent, child, expected in (
        ("overview", "roots_scanned", list),
        ("types", "distribution", list),
        ("hierarchy", "hubs", list),
        ("origin", "uncertain", list),
        ("origin", "empty_use_case_locally_developed", list),
    ):
        section = snapshot.get(parent)
        if not isinstance(section, dict):
            continue
        if child not in section:
            errors.append(f"缺少嵌套欄位：{parent}.{child}")
        elif not isinstance(section[child], expected):
            errors.append(
                f"嵌套欄位型別異常：{parent}.{child} 預期 {expected.__name__}，"
                f"實際 {type(section[child]).__name__}"
            )

    return {
        "snapshot": snapshot,
        "errors": errors,
        "available": len(errors) == 0,
    }


def load_bundle() -> dict[str, Any]:
    """組裝視圖共用的 bundle；缺檔或異常時仍回傳可用（空）結構。"""
    result = _load_snapshot(str(SNAPSHOT_PATH))
    return {
        "snapshot": result["snapshot"],
        "errors": result["errors"],
        "available": result["available"],
        "path": str(SNAPSHOT_PATH),
    }


def as_list(bundle: dict[str, Any], key: str) -> list[Any]:
    """安全取列；欄位缺失或型別異常時回傳空列表，不補值。"""
    value = bundle.get("snapshot", {}).get(key)
    return value if isinstance(value, list) else []


def as_dict(bundle: dict[str, Any], key: str) -> dict[str, Any]:
    """安全取映射；欄位缺失或型別異常時回傳空字典，不補值。"""
    value = bundle.get("snapshot", {}).get(key)
    return value if isinstance(value, dict) else {}


def dict_list(parent: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """從映射安全取出由 dict 組成的列；非 dict 項目略過，不補值。"""
    value = parent.get(key)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def view_label(bundle: dict[str, Any], view_id: str, default: str = "") -> str:
    """由快照 views 取得視圖標籤，避免視圖自行命名。"""
    for item in as_list(bundle, "views"):
        if isinstance(item, dict) and item.get("id") == view_id:
            label = item.get("label")
            return label if isinstance(label, str) else default
    return default


def fmt_int(value: Any) -> str:
    """整數千分位；非整數或缺失時回傳「—」，不猜測。"""
    if isinstance(value, bool) or not isinstance(value, int):
        return "—"
    return f"{value:,}"


def show_degradation(
    bundle: dict[str, Any], extra_errors: list[str] | None = None
) -> None:
    """以折疊區塊呈現降級與錯誤紀錄（具可識別標籤）。"""
    errors = list(bundle.get("errors", [])) + list(extra_errors or [])
    st.caption("降級與資料完整性檢查")
    st.caption(f"同源快照：{bundle.get('path', '—')}")
    if errors:
        st.warning("資料不完整，以下畫面僅顯示可由快照驗證的內容；未編造缺漏值。")
        for item in errors:
            st.write(f"- {item}")
    else:
        st.success("快照讀取成功，必要欄位齊備；視圖內容全部來自同源快照。")

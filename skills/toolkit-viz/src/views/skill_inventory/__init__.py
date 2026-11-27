"""技能盤點展示 — 由同源快照驅動。

遵循 toolkit-viz「Streamlit 規則（SSOT）」A–E（見 SKILL.md），此處不重複抄寫規則。
"""

import streamlit as st

from .data import as_dict, as_list, load_bundle
from .views import catalog, hierarchy, overview, types, uncertain

ROUTES = {
    "overview": overview.render,
    "types": types.render,
    "hierarchy": hierarchy.render,
    "origin": uncertain.render,
    "skills": catalog.render,
}


def _options():
    """選項順序與標籤皆取自同源快照 views；未登錄 ROUTES 的 id 不顯示、不補造。"""
    bundle = load_bundle()
    view_defs = as_list(bundle, "views")
    labels = {
        item.get("id"): item.get("label", item.get("id", "—"))
        for item in view_defs
        if isinstance(item, dict)
    }
    options = [
        item.get("id")
        for item in view_defs
        if isinstance(item, dict) and item.get("id") in ROUTES
    ]
    return options, labels


def skill_inventory_sidebar():
    """側邊欄視圖選擇；回傳選定 id，無可用視圖則回傳 None。"""
    options, labels = _options()
    if not options:
        st.sidebar.error("同源快照未提供可辨識的 views，無法路由至任何視圖。")
        return None
    return st.sidebar.radio(
        "選擇檢視",
        options,
        format_func=lambda key: labels.get(key, key),
        key="skill_inventory_view_pick",
        horizontal=True,
    )


def render_skill_inventory(selected=None):
    """主畫面：只渲染選定視圖，失敗時降級顯示 errors，不編造內容。"""
    bundle = load_bundle()
    if selected not in ROUTES:
        st.error("同源快照未提供可辨識的 views，無法路由至任何視圖。")
        return

    meta = as_dict(bundle, "meta")
    source = meta.get("source")
    st.caption("同源快照與完整性")
    st.caption(f"同源快照：{bundle.get('path', '—')}")
    st.caption(f"可用狀態：{bundle.get('available', False)}")
    st.caption(f"錯誤筆數：{len(bundle.get('errors', []))}")
    if isinstance(source, dict):
        st.caption(f"原始來源：{source.get('path', '—')}")
        st.caption(f"來源 sha256：{source.get('sha256', '—')}")
    st.caption(meta.get("scope_policy", ""))

    ROUTES[selected](bundle)

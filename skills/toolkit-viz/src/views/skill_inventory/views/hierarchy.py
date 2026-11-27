"""視圖 3：hierarchy 樞紐 top10（references + referenced_by 複合排序）。"""

import streamlit as st

from ..data import as_dict, dict_list, fmt_int, show_degradation, view_label


def render(bundle: dict) -> None:
    h = as_dict(bundle, "hierarchy")
    st.header(view_label(bundle, "hierarchy", "hierarchy 樞紐"))
    st.caption(h.get("method", ""))

    hubs = dict_list(h, "hubs")
    legend = h.get("role_legend")
    roles = (
        ["全部角色"] + [k for k in legend if isinstance(k, str)]
        if isinstance(legend, dict)
        else ["全部角色"]
    )

    if not hubs:
        st.info("快照未提供 hierarchy.hubs，樞紐清單從缺。")
    else:
        st.caption(f"快照收錄樞紐筆數：{fmt_int(len(hubs))}")
        role_pick = st.radio(
            "依結構角色篩選",
            roles,
            key="hierarchy_role_filter",
            horizontal=True,
        )
        shown = (
            hubs
            if role_pick == "全部角色"
            else [item for item in hubs if item.get("role") == role_pick]
        )
        rows = [
            {
                "name": item.get("name"),
                "references": item.get("references"),
                "referenced_by": item.get("referenced_by"),
                "total": item.get("total"),
                "role": item.get("role"),
                "origin": item.get("origin"),
                "hint": item.get("hint"),
            }
            for item in shown
        ]
        st.dataframe(rows, width="stretch")

    st.caption("hierarchy 方法與角色圖例")
    st.write(h.get("method", "—"))
    if isinstance(legend, dict) and legend:
        for role, desc in legend.items():
            st.write(f"- **{role}**：{desc}")
    else:
        st.caption("快照未提供 role_legend。")

    show_degradation(bundle)

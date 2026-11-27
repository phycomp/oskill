"""視圖 2：七類 type 分布（可複選，合計大於入冊數属正常）。"""

import streamlit as st

from ..data import as_dict, dict_list, fmt_int, show_degradation, view_label


def render(bundle: dict) -> None:
    td = as_dict(bundle, "types")
    st.header(view_label(bundle, "types", "type 分布"))

    rows = [
        {
            "type": item.get("type"),
            "count": item.get("count"),
            "pct_of_enrolled": item.get("pct_of_enrolled"),
            "definition": item.get("definition"),
        }
        for item in dict_list(td, "distribution")
    ]

    st.metric("七類合計（可複選標籤出現次數）", fmt_int(td.get("sum_of_counts")))
    st.caption(td.get("multi_select_note", ""))

    if not rows:
        st.info("快照未提供 types.distribution，type 分布從缺。")
    else:
        sort_choice = st.radio(
            "排序方式",
            ["依快照順序", "依計數遞減"],
            key="types_sort_choice",
            horizontal=True,
        )
        shown = rows
        if sort_choice == "依計數遞減":
            shown = sorted(
                rows,
                key=lambda row: row["count"] if isinstance(row["count"], int) else 0,
                reverse=True,
            )
        st.dataframe(shown, width="stretch")

    st.caption("type 定義（取自快照 definitions）")
    definitions = td.get("definitions")
    if isinstance(definitions, dict) and definitions:
        for key, text in definitions.items():
            st.write(f"- **{key}**：{text}")
    else:
        st.caption("快照未提供 definitions。")

    show_degradation(bundle)

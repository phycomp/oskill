"""視圖 4：origin 分布、11 筆 uncertain 與 11 筆 locally use_case 從缺，如實標註。"""

import streamlit as st

from ..data import as_dict, dict_list, fmt_int, show_degradation, view_label


def _as_rows(items: list[dict], with_use_case: bool) -> list[dict]:
    rows = []
    for item in items:
        row = {
            "name": item.get("name"),
            "type": item.get("type"),
            "origin": item.get("origin"),
            "note": item.get("note"),
            "use_case_status": item.get("use_case_status"),
        }
        if with_use_case:
            row["use_case"] = item.get("use_case")
        rows.append(row)
    return rows


def render(bundle: dict) -> None:
    o = as_dict(bundle, "origin")
    st.header(view_label(bundle, "origin", "origin / uncertain"))

    dist = dict_list(o, "distribution")
    if dist:
        st.dataframe(
            [
                {
                    "origin": item.get("origin"),
                    "count": item.get("count"),
                    "label": item.get("label"),
                }
                for item in dist
            ],
            width="stretch",
        )
    else:
        st.info("快照未提供 origin.distribution。")

    uncertain = dict_list(o, "uncertain")
    empty_local = dict_list(o, "empty_use_case_locally_developed")
    st.caption(o.get("uncertain_label", ""))

    mode = st.radio(
        "如實標註切換",
        [
            f"uncertain（{fmt_int(len(uncertain))} 筆，use_case 為內容推估）",
            f"locally_developed（{fmt_int(len(empty_local))} 筆，use_case 從缺）",
        ],
        key="origin_uncertain_mode",
        horizontal=True,
    )

    if mode.startswith("uncertain"):
        st.dataframe(_as_rows(uncertain, with_use_case=True), width="stretch")
    else:
        st.dataframe(_as_rows(empty_local, with_use_case=False), width="stretch")

    st.caption("uncertain 標註依據與快照差異說明")
    st.write(o.get("uncertain_label", "—"))
    st.write(o.get("discrepancy_note", "—"))
    st.caption(
        f"uncertain 列數：{fmt_int(len(uncertain))}；"
        f"use_case 從缺（自建）列數：{fmt_int(len(empty_local))}。"
        "兩者不可互換：前者有 use_case 但屬內容推估，非歸屬佐證。"
    )

    show_degradation(bundle)

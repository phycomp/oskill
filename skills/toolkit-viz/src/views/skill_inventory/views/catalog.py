"""視圖 5：173 技能表；type / origin 篩選與關鍵字搜尋（只讀快照）。"""

from collections import Counter

import streamlit as st

from ..data import as_dict, as_list, dict_list, fmt_int, show_degradation, view_label


def render(bundle: dict) -> None:
    st.header(view_label(bundle, "skills", "完整技能表"))
    skills = [item for item in as_list(bundle, "skills") if isinstance(item, dict)]

    type_order = as_dict(bundle, "types").get("order")
    type_options = (
        ["全部 type"] + [item for item in type_order if isinstance(item, str)]
        if isinstance(type_order, list)
        else ["全部 type"]
    )

    origin_options = ["全部 origin"]
    for item in dict_list(as_dict(bundle, "origin"), "distribution"):
        origin_value = item.get("origin")
        if isinstance(origin_value, str):
            origin_options.append(origin_value)

    type_pick = st.radio(
        "依 type 篩選",
        type_options,
        key="catalog_type_filter",
        horizontal=True,
    )
    origin_pick = st.radio(
        "依 origin 篩選",
        origin_options,
        key="catalog_origin_filter",
        horizontal=True,
    )
    keyword = st.text_input(
        "關鍵字搜尋（name / note / use_case / trigger / location）",
        key="catalog_keyword",
    )

    needle = keyword.strip().lower()
    filtered = []
    for item in skills:
        if type_pick != "全部 type" and type_pick not in item.get("type", []):
            continue
        if origin_pick != "全部 origin" and item.get("origin") != origin_pick:
            continue
        if needle:
            haystack = " ".join(
                str(item.get(field, ""))
                for field in ("name", "note", "use_case", "trigger", "location")
            ).lower()
            if needle not in haystack:
                continue
        filtered.append(item)

    rows = [
        {
            "name": item.get("name"),
            "type": item.get("type"),
            "origin": item.get("origin"),
            "role": item.get("role"),
            "hierarchy_total": (item.get("hierarchy") or {}).get("total"),
            "use_case_empty": item.get("use_case_empty"),
            "location": item.get("location"),
            "use_case": item.get("use_case"),
        }
        for item in filtered
    ]
    st.caption(
        f"顯示 {fmt_int(len(rows))} / {fmt_int(len(skills))} 筆；"
        "內容皆取自同源快照 skills。"
    )
    st.dataframe(rows, width="stretch")

    st.caption("同名重複說明（由快照 name 推導）")
    counts = Counter(item.get("name") for item in skills)
    duplicates = {name: n for name, n in counts.items() if n > 1}
    if duplicates:
        for name, n in sorted(duplicates.items()):
            st.write(f"- **{name}**（{n} 筆）")
            for item in skills:
                if item.get("name") == name:
                    st.caption(f"  - {item.get('location', '—')}")
    else:
        st.caption("快照未發現同名重複。")

    st.caption("欄位與篩選說明")
    st.caption("type 為可複選標籤，篩選為「含有該標籤」；origin 為單一歸屬值。")
    st.caption("use_case_empty 為快照原始旗標；use_case 為快照原文，未截斷。")

    show_degradation(bundle)

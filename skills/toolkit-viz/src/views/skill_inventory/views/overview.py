"""視圖 1：total / 入冊 / 自建 / uncertain / 未入冊與掃描根（全部取自快照）。"""

import streamlit as st

from ..data import (
    as_dict,
    as_list,
    dict_list,
    fmt_int,
    show_degradation,
    view_label,
)


def render(bundle: dict) -> None:
    ov = as_dict(bundle, "overview")
    meta = as_dict(bundle, "meta")
    st.header(view_label(bundle, "overview", "總覽"))
    st.caption(meta.get("ssot_note", ""))

    cols = st.columns(5)
    metrics = (
        ("掃描技能總數", ov.get("total_skills")),
        ("入冊技能", ov.get("enrolled_skills")),
        ("自建 locally_developed", ov.get("locally_developed_count")),
        ("歸屬未定 uncertain", ov.get("uncertain_count")),
        ("未入冊", ov.get("not_enrolled")),
    )
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, fmt_int(value))

    roots = ov.get("roots_scanned")
    if isinstance(roots, list) and roots:
        st.subheader("掃描根目錄")
        st.dataframe(
            [{"roots_scanned": item} for item in roots if isinstance(item, str)],
            width="stretch",
        )
    else:
        st.info("快照未提供可辨識的 roots_scanned，掃描根目錄從缺。")

    st.caption(ov.get("snapshot_caveat", ""))
    st.caption(ov.get("hierarchy_caveat", ""))

    st.caption(f"未入冊 {fmt_int(ov.get('not_enrolled'))} 明細（快照僅提供計數）")
    st.write(f"未入冊計數：{fmt_int(ov.get('not_enrolled'))}")
    st.caption(
        f"同源快照僅記載 not_enrolled = {fmt_int(ov.get('not_enrolled'))}，"
        "未提供逐筆技能清單；此處不列名、不推補內容。"
    )
    st.caption(
        f"可由快照驗證的關係：掃描總數 {fmt_int(ov.get('total_skills'))} "
        f"− 入冊 {fmt_int(ov.get('enrolled_skills'))} "
        f"= 未入冊 {fmt_int(ov.get('not_enrolled'))}。"
    )

    st.caption("一致性檢查（同源欄位交叉比對）")
    ov_local = ov.get("locally_developed_count")
    ov_uncertain = ov.get("uncertain_count")
    ov_enrolled = ov.get("enrolled_skills")
    ov_total = ov.get("total_skills")
    ov_not = ov.get("not_enrolled")
    skills_n = len(as_list(bundle, "skills"))
    type_sum = as_dict(bundle, "types").get("sum_of_counts")
    actual_type_sum = sum(
        item.get("count", 0)
        for item in dict_list(as_dict(bundle, "types"), "distribution")
        if isinstance(item.get("count", 0), int)
    )
    origin = as_dict(bundle, "origin")
    uncertain_n = len(dict_list(origin, "uncertain"))
    empty_local_n = len(dict_list(origin, "empty_use_case_locally_developed"))

    checks = (
        (
            "入冊 = 自建 + uncertain",
            ov_enrolled == ov_local + ov_uncertain,
            f"{fmt_int(ov_enrolled)} = {fmt_int(ov_local)} + {fmt_int(ov_uncertain)}",
        ),
        (
            "掃描總數 = 入冊 + 未入冊",
            ov_total == ov_enrolled + ov_not,
            f"{fmt_int(ov_total)} = {fmt_int(ov_enrolled)} + {fmt_int(ov_not)}",
        ),
        (
            "skills 列數 = 入冊數",
            skills_n == ov_enrolled,
            f"{fmt_int(skills_n)} / {fmt_int(ov_enrolled)}",
        ),
        (
            "type 各類合計 = sum_of_counts",
            actual_type_sum == type_sum,
            f"{fmt_int(actual_type_sum)} / {fmt_int(type_sum)}",
        ),
        (
            "uncertain 列數 = uncertain_count",
            uncertain_n == ov_uncertain,
            f"{fmt_int(uncertain_n)} / {fmt_int(ov_uncertain)}",
        ),
    )
    for label, passed, detail in checks:
        st.write(f"{'✅' if passed else '⚠️'} {label}：{detail}")
    st.caption(
        "另外：uncertain 有 use_case 但為內容推估；"
        f"use_case 從缺者為 {fmt_int(empty_local_n)} 筆 locally_developed（如實取自快照）。"
    )

    show_degradation(bundle)

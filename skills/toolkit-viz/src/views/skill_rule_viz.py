"""技能規則視覺化 - 讀取 skillrule-viz 輸出並在 Streamlit 內嵌 Graphify 原生 HTML。"""

from __future__ import annotations

import json
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

DEFAULT_OUT = Path("skillrule-viz-out")
FALLBACK_OUTS = [
    Path("skillrule-viz-out"),
    Path("/home/sam/skillrule-viz-out"),
    Path("/home/sam/.opencode/skills/toolkit-viz/skillrule-viz-out-demo"),
    Path("/tmp/opencode/skillrule-viz-ui/demo"),
]


def _is_output_dir(p: Path) -> bool:
    return p.is_dir() and ((p / "report.md").exists() or (p / "result.json").exists() or (p / "graph.html").exists())


def _list_outputs(base: Path) -> list[Path]:
    candidates: list[Path] = []
    if base.exists():
        candidates.append(base)
        if base.is_dir():
            candidates.extend([p for p in base.iterdir() if p.is_dir()])
    for fb in FALLBACK_OUTS:
        if fb.exists():
            candidates.append(fb)
            if fb.is_dir():
                candidates.extend([p for p in fb.iterdir() if p.is_dir()])
    outs = [p for p in candidates if _is_output_dir(p)]
    uniq = {p.resolve(): p for p in outs}
    return sorted(uniq.values(), key=lambda p: p.stat().st_mtime, reverse=True)


def render_skill_rule_viz() -> None:
    st.subheader("技能規則視覺化（Gate / Drift / Rule）")
    st.caption("資料來源：skillrule-viz 輸出目錄；Graphify 原生 HTML 以本機檔案內嵌顯示。")

    base_str = st.sidebar.text_input("skillrule-viz 輸出根目錄", value=str(DEFAULT_OUT), key="skillrule_viz_base")
    base = Path(base_str).expanduser()
    outs = _list_outputs(base)
    if not outs:
        st.warning("找不到 skillrule-viz 輸出。先執行 skillrule-viz 產生 report/graph.html。")
        st.code(
            "python3 ~/.opencode/skills/skillrule-viz/scripts/skillrule_viz.py "
            "--skill toolkit-viz --mode both --graphify all --out ./skillrule-viz-out/demo",
            language="bash",
        )
        return

    labels = {str(p): p.name for p in outs}
    pick_key = st.sidebar.radio(
        "選擇輸出",
        options=[str(p) for p in outs],
        format_func=lambda k: labels.get(k, k),
        key="skillrule_viz_pick",
    )
    pick = Path(pick_key)
    result = {}
    rp = pick / "result.json"
    if rp.exists():
        try:
            result = json.loads(rp.read_text(encoding="utf-8"))
        except Exception as e:
            st.error(f"result.json 讀取失敗：{e}")

    cols = st.columns(4)
    cols[0].metric("節點", result.get("nodes", "—"))
    cols[1].metric("邊", result.get("edges", "—"))
    cols[2].metric("Manifests", len(result.get("manifests", [])))
    cols[3].metric("Reports", len(result.get("reports", [])))

    report_p = pick / "report.md"
    if report_p.exists():
        st.markdown("### 報告（Markdown）")
        st.markdown(report_p.read_text(encoding="utf-8", errors="ignore"))

    generic = pick / "generic.mmd"
    data_mmd = pick / "data.mmd"
    if generic.exists() or data_mmd.exists():
        st.markdown("### Mermaid 原始碼")
        if generic.exists():
            st.caption("generic.mmd")
            st.code(
                generic.read_text(encoding="utf-8", errors="ignore"), language="mermaid"
            )
        if data_mmd.exists():
            st.caption("data.mmd")
            st.code(
                data_mmd.read_text(encoding="utf-8", errors="ignore"),
                language="mermaid",
            )

    html_p = pick / "graph.html"
    graphify_info = (
        result.get("graphify", {}) if isinstance(result.get("graphify"), dict) else {}
    )
    native = graphify_info.get("native_html")
    if native:
        html_p = Path(native)
    if html_p.exists():
        st.subheader("Graphify 原生 HTML")
        html = html_p.read_text(encoding="utf-8", errors="ignore")
        components.html(html, height=820, scrolling=True)
        st.caption(f"來源：{html_p}")
    else:
        st.info(
            "未找到 graph.html。請使用 --graphify cli/all 產生 Graphify 原生 HTML。"
        )

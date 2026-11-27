import streamlit as st
import json, os
from pathlib import Path

st.set_page_config(page_title="Toolkit Viz", layout="wide")

from src.views.skill_inventory import (
    render_skill_inventory,
    skill_inventory_sidebar,
)

BASE = Path(__file__).parent
INDEX = BASE / "data" / "topics_index.json"


@st.cache_data
def load_index():
    if INDEX.exists():
        return json.loads(INDEX.read_text())
    return {}


def read_md(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return ""


def main():
    st.title("📚 Toolkit Viz — 蒸餾成果展示平台")

    # 頂層展示模式（SSOT.B.1：radio、帶穩定 key；單一 goal 只 hook 一條路徑）
    mode = st.sidebar.radio(
        "展示模式",
        ["蒸餾主題", "🧭 技能盤點", "🕸 技能規則視覺化"],
        key="viz_display_mode",
        horizontal=True,
    )
    if mode == "🧭 技能盤點":
        selected_view = skill_inventory_sidebar()
        if selected_view:
            render_skill_inventory(selected_view)
        return
    if mode == "🕸 技能規則視覺化":
        from src.views.skill_rule_viz import render_skill_rule_viz
        render_skill_rule_viz()
        return

    topics = load_index()
    if not topics:
        st.warning("尚無蒸餾主題。請執行 scripts/collect_topics.py")
        return

    # Check URL query params for pre-selected topic
    query_params = st.query_params
    pre_selected = query_params.get("topic", None)

    # Sidebar: topic selection
    st.sidebar.header("主題選擇")
    topic_names = sorted(topics.keys())
    if pre_selected and pre_selected in topic_names:
        default_idx = topic_names.index(pre_selected)
    else:
        default_idx = 0
    selected = st.sidebar.radio(
        "選擇主題", topic_names, index=default_idx, horizontal=True
    )
    search_query = st.sidebar.text_input("🔍 搜尋關鍵字")

    # Main content
    if search_query:
        st.subheader(f"搜尋結果：{search_query}")
        results = []
        for name, info in topics.items():
            for f in info.get("md_files", []):
                content = read_md(f)
                if search_query.lower() in content.lower():
                    results.append((name, f, content))
        if results:
            for name, f, content in results:
                st.markdown(f"### {name} — {Path(f).name}")
                st.markdown(content[:2000])
        else:
            st.info("無搜尋結果")
        return

    if selected:
        info = topics[selected]
        md_files = info.get("md_files", [])
        if not md_files:
            st.info("無檔案")
            return

        # Extract title from each md file (first # heading)
        file_labels = []
        for f in md_files:
            c = read_md(f)
            title = Path(f).name
            for line in c.splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            file_labels.append(title)

        # Left/Right columns layout
        left, right = st.columns([3, 7])

        with left:
            st.subheader("子檔案選擇")
            selected_label = st.radio("選擇檔案", file_labels, key="subfile_radio")
            selected_idx = file_labels.index(selected_label)
            selected_path = md_files[selected_idx]
            selected_file = Path(selected_path).name

        with right:
            st.header(f"📁 {selected}")
            st.caption(f"來源：{info['source']} | 檔案數：{info['count']}")
            st.markdown(f"**路徑**：`{info['path']}`")

            if selected_path:
                content = read_md(selected_path)
                st.markdown(content)
                st.download_button(
                    "下載", content, file_name=selected_file, mime="text/markdown"
                )

            # 附加檔案（Excel / CSV）：動態掃描目前主題目錄，不影響既有 md 呈現
            attachments = sorted(
                list(Path(info["path"]).glob("*.xlsx"))
                + list(Path(info["path"]).glob("*.xls"))
                + list(Path(info["path"]).glob("*.csv"))
            )
            if attachments:
                st.divider()
                st.subheader("附加檔案（Excel / CSV）")
                for ef in attachments:
                    ext = ef.suffix.lower()
                    if ext == ".xlsx":
                        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    elif ext == ".csv":
                        mime = "text/csv"
                    else:
                        mime = "application/octet-stream"
                    st.download_button(
                        f"下載 {ef.name}",
                        data=ef.read_bytes(),
                        file_name=ef.name,
                        mime=mime,
                        key=f"xdl_{ef.name}",
                    )


if __name__ == "__main__":
    main()

import datetime
import streamlit as st

# 必须第一个执行
st.set_page_config(page_title="Daily Schedule Analyzer", layout="wide")

from src.data_loader import fetch_calendar_data
from src.visualization import plot_interactive_timeline, plot_pie_chart

# --- CSS 样式注入：将 Tertiary 按钮变成蓝色链接风格 ---
st.markdown("""
<style>
/* 针对 "View Detail" 按钮的样式定制 */
button[kind="tertiary"] {
    color: #0078D4 !important; /* 微软蓝/链接蓝 */
    text-decoration: none;
    padding: 0px !important;
    border: none !important;
    background: none !important;
    font-size: 14px !important;
    box-shadow: none !important;
    height: auto !important;
    min-height: 0px !important;
    line-height: 1.5 !important;
    margin-top: 2px;
}
button[kind="tertiary"]:hover {
    color: #005A9E !important;
    text-decoration: underline;
    background-color: transparent !important;
}
button[kind="tertiary"]:focus {
    color: #005A9E !important;
    box-shadow: none !important;
    outline: none !important;
}
/* 表格头部样式微调 */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    border: none;
    background: transparent;
    font-weight: bold;
    color: #555;
    padding-left: 0;
}
/* 分隔线微调 */
hr {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# --- 原生模态弹窗 ---
@st.dialog("📝 Note Details")
def show_note_details(row_data):
    """显示详细笔记的模态窗口"""
    c1, c2 = st.columns([2, 1])
    with c1:
        st.caption("Event Activity")
        st.markdown(f"### {row_data['Cat Emoji']} {row_data['Event Name']}")
    with c2:
        st.caption("Time & Duration")
        st.markdown(f"**{row_data['Date']}**")
        st.markdown(f"{row_data['Time Span']} ({row_data['Duration Label']})")

    st.divider()

    st.markdown("#### Full Notes")
    if row_data['Markdown Description'] and row_data['Markdown Description'] != "_No additional notes_":
        st.markdown(row_data['Markdown Description'])
    else:
        st.info("No detailed notes available for this event.")


def main():
    st.title("📅 Daily Schedule Analyzer Dashboard")
    st.markdown("---")

    today = datetime.date.today()
    c1, c2, c3 = st.columns([1, 2, 1])

    with c1:
        mode = st.selectbox("Analysis Mode", ["Specific Day", "Last N Days", "Specific Week", "Custom Range"])

    start_date = end_date = today
    with c2:
        if mode == "Specific Day":
            start_date = st.date_input("Select Date", today)
            end_date = start_date
        elif mode == "Last N Days":
            days = st.slider("Window", 1, 30, 7)
            start_date = today - datetime.timedelta(days=days)
        elif mode == "Specific Week":
            pick_date = st.date_input("Select Week", today)
            start_date = pick_date - datetime.timedelta(days=pick_date.weekday())
            end_date = start_date + datetime.timedelta(days=6)
        elif mode == "Custom Range":
            rng = st.date_input("Range", [today - datetime.timedelta(days=3), today])
            if len(rng) == 2: start_date, end_date = rng

    with c3:
        st.write("")
        if st.button("🔄 Sync & Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    df, _ = fetch_calendar_data(start_date, end_date)

    if not df.empty:
        if mode == "Specific Day":
            st.subheader(f"📅 Daily Timeline ({start_date})")
            plot_interactive_timeline(df, selected_date_obj=start_date)
            st.markdown("---")

        st.subheader("🍩 Aggregated Stats")
        _, col_pie, _ = st.columns([1, 1, 1])
        with col_pie:
            plot_pie_chart(df)

        st.markdown("---")

        st.subheader("📝 Detailed Log")

        # --- 自定义排序逻辑 ---
        if 'sort_col' not in st.session_state:
            st.session_state.sort_col = 'Local Start'
            st.session_state.sort_asc = False

        def toggle_sort(col_name):
            if st.session_state.sort_col == col_name:
                st.session_state.sort_asc = not st.session_state.sort_asc
            else:
                st.session_state.sort_col = col_name
                st.session_state.sort_asc = True

        # 应用排序
        df_sorted = df.sort_values(by=st.session_state.sort_col, ascending=st.session_state.sort_asc)

        # --- 自定义表头 (Custom Header) ---
        # 使用列布局模拟表头
        h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([1.2, 2, 1, 1.5, 3])

        # 使用 button 模拟可点击的表头
        if h_col1.button(f"Date {'⬇️' if st.session_state.sort_col == 'Date' else ''}", key="sort_date"):
            toggle_sort('Date')
            st.rerun()
        if h_col2.button(f"Activity {'⬇️' if st.session_state.sort_col == 'Event Name' else ''}", key="sort_name"):
            toggle_sort('Event Name')
            st.rerun()
        # 其他列头可以是静态文本
        h_col3.markdown("**Hrs**")
        h_col4.markdown("**Time Range**")
        h_col5.markdown("**Notes (Preview)**")

        st.markdown("---")  # 表头分隔线

        # --- 自定义行渲染 (Custom Row Loop) ---
        for index, row in df_sorted.iterrows():
            # 定义列宽，保持与表头一致
            c1, c2, c3, c4, c5 = st.columns([1.2, 2, 1, 1.5, 3])

            # 1. Date
            c1.write(row['Date'].strftime('%Y-%m-%d'))

            # 2. Activity (Emoji + Name)
            c2.write(f"{row['Cat Emoji']} {row['Event Name']}")

            # 3. Duration
            c3.write(row['Duration Label'])

            # 4. Time Range
            c4.write(row['Time Span'])

            # 5. Notes + View Detail Button (同列显示)
            with c5:
                # 使用 col 再次分割，实现左边文本，右边按钮的紧凑布局
                sub_c1, sub_c2 = st.columns([3, 1])
                sub_c1.write(row['Short Notes'] if row['Short Notes'] else "-")

                # [核心交互]
                # 这是一个真正的 Button，但通过 CSS 伪装成了蓝色链接
                # 点击它直接触发 Python 函数，没有网络跳转
                if sub_c2.button("🔍 View Detail", key=f"btn_{row['Event ID']}", type="tertiary"):
                    show_note_details(row)

            # 行分隔线 (可选，为了像表格)
            st.markdown("<hr style='margin: 0; opacity: 0.2;'>", unsafe_allow_html=True)

    else:
        st.info("No events found for the selected period.")


if __name__ == '__main__':
    main()
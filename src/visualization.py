import datetime
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import streamlit as st
from src.utils import solve_overlaps

# 设置字体以支持中文
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


def plot_interactive_timeline(df, selected_date_obj=None):
    """
    绘制 Plotly 交互式泳道图 (保持不变)
    """
    if selected_date_obj:
        ref_date = selected_date_obj
    elif not df.empty:
        if 'Date' in df.columns:
            ref_date = df.iloc[0]['Date']
        else:
            ref_date = df.iloc[0]['Local Start'].date()
    else:
        ref_date = datetime.date.today()

    unique_events = sorted(df['Event Name'].unique(), reverse=True)

    fig = go.Figure()

    SUB_LANE_OFFSET = 0.4
    BAR_THICKNESS = 15

    y_tick_vals = []
    y_tick_text = []
    current_y_base = 0

    for event_name in unique_events:
        subset = df[df['Event Name'] == event_name].copy()
        sub_lanes, max_sub = solve_overlaps(subset)

        category_height = (max_sub + 1) * SUB_LANE_OFFSET
        center_y = current_y_base + (category_height / 2) - (SUB_LANE_OFFSET / 2)
        y_tick_vals.append(center_y)
        y_tick_text.append(event_name)

        for i, ((idx, row), sub_idx) in enumerate(zip(subset.iterrows(), sub_lanes)):
            y_pos = current_y_base + (sub_idx * SUB_LANE_OFFSET)

            hover_html = (
                    f"<b>{row['Event Name']}</b><br>" +
                    f"🕒 {row['Time Span']} ({row['Duration Label']})<br>" +
                    f"------------------------------<br>" +
                    f"{row['Tooltip Description']}"
            )

            fig.add_trace(go.Scatter(
                x=[row['Local Start'], row['Local End']],
                y=[y_pos, y_pos],
                mode='lines',
                line=dict(color=row['Hex Color'], width=BAR_THICKNESS),
                name=row['Event Name'],
                text=hover_html,
                hoverinfo='text',
                showlegend=False
            ))

            day_end_limit = row['Local Start'].normalize() + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            clamped_end = min(row['Local End'], day_end_limit)
            is_clipped = row['Local End'] > day_end_limit

            mod = i % 3
            fixed_yshift = 16

            if mod == 0:
                x_pos = row['Local Start'] + (clamped_end - row['Local Start']) / 2
                x_anchor = 'center'
                x_shift = 0
            elif mod == 1:
                if is_clipped:
                    x_pos = clamped_end
                    x_anchor = 'right'
                    x_shift = -5
                else:
                    x_pos = row['Local End']
                    x_anchor = 'left'
                    x_shift = 5
            else:
                x_pos = row['Local Start']
                x_anchor = 'right'
                x_shift = -5

            fig.add_annotation(
                x=x_pos,
                y=y_pos,
                yshift=fixed_yshift,
                xshift=x_shift,
                xanchor=x_anchor,
                text=f"{row['Time Span']} ({row['Duration Label']})",
                showarrow=False,
                font=dict(size=10, color="black")
            )

        fig.add_shape(
            type="rect", xref="paper", yref="y", x0=0, x1=1,
            y0=current_y_base - 0.2, y1=current_y_base + category_height - 0.2,
            fillcolor="gray", opacity=0.05, layer="below", line_width=0,
        )

        current_y_base += category_height + 0.5

    start_range = datetime.datetime.combine(ref_date, datetime.time.min)
    end_range = datetime.datetime.combine(ref_date, datetime.time.max)

    fig.update_layout(
        height=max(400, current_y_base * 50),
        xaxis=dict(
            title="Hour of Day (Local Time)",
            type='date',
            tickformat='%H:%M',
            gridcolor='rgba(0,0,0,0.1)',
            range=[start_range, end_range]
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=y_tick_vals,
            ticktext=y_tick_text,
            tickfont=dict(size=12, family="Microsoft YaHei", weight="bold"),
            gridcolor='rgba(0,0,0,0)'
        ),
        plot_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="sans-serif",
            align="left"
        )
    )

    st.plotly_chart(fig, width="stretch")


# --- [核心修改] 更新饼图逻辑 ---
def plot_pie_chart(df):
    dist = df.groupby(['Event Name', 'Hex Color'])['Duration Val'].sum().reset_index()

    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = pct * total / 100.0
            # [修改点] 将 \n 改为空格，强制单行显示，减少对垂直空间的占用
            return f'{pct:.1f}% ({val:.2f}h)'

        return my_autopct

    fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
    ax_pie.pie(
        dist['Duration Val'],
        labels=dist['Event Name'],
        autopct=make_autopct(dist['Duration Val']),
        startangle=140,
        colors=dist['Hex Color'],
        textprops={'fontsize': 10, 'fontfamily': 'Microsoft YaHei'}
    )
    ax_pie.set_title(f"Total: {df['Duration Val'].sum():.2f} hrs", fontweight='bold')
    st.pyplot(fig_pie)
import os
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- 0. 字体配置 (中文支持) ---
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# --- 1. 系统配置 (名称已修改) ---
st.set_page_config(page_title="Daily Schedule Analyzer", layout="wide")
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

COLOR_MAP = {
    '1': {'label': 'Lavender', 'hex': '#7986cb', 'emoji': '🟣'},
    '2': {'label': 'Sage', 'hex': '#33b679', 'emoji': '🟢'},
    '3': {'label': 'Grape', 'hex': '#8e24aa', 'emoji': '🍇'},
    '4': {'label': 'Flamingo', 'hex': '#e67c73', 'emoji': '🦩'},
    '5': {'label': 'Banana', 'hex': '#f6bf26', 'emoji': '🍌'},
    '6': {'label': 'Tangerine', 'hex': '#f4511e', 'emoji': '🍊'},
    '7': {'label': 'Peacock', 'hex': '#039be5', 'emoji': '🦚'},
    '8': {'label': 'Graphite', 'hex': '#616161', 'emoji': '📓'},
    '9': {'label': 'Blueberry', 'hex': '#3f51b5', 'emoji': '🫐'},
    '10': {'label': 'Basil', 'hex': '#0b8043', 'emoji': '🌿'},
    '11': {'label': 'Tomato', 'hex': '#d50000', 'emoji': '🍅'},
    'Default': {'label': 'Default', 'hex': '#039be5', 'emoji': '🔵'}
}


# --- 2. 认证模块 ---
def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


# --- 3. 数据获取 (核心修复：自动获取日历时区) ---
@st.cache_data(ttl=300)
def fetch_calendar_data(start_date, end_date):
    try:
        service = get_calendar_service()

        # [Step A] 获取用户日历的真实时区设置 (例如 'America/New_York')
        # 这确保了图表显示的时间和你 Google Calendar 看到的一模一样
        calendar_info = service.calendars().get(calendarId='primary').execute()
        user_timezone = calendar_info.get('timeZone', 'UTC')

        # 扩大查询窗口 (UTC)
        query_start = (start_date - datetime.timedelta(days=1))
        query_end = (end_date + datetime.timedelta(days=1))

        start_iso = datetime.datetime.combine(query_start, datetime.time.min).isoformat() + 'Z'
        end_iso = datetime.datetime.combine(query_end, datetime.time.max).isoformat() + 'Z'

        events_result = service.events().list(
            calendarId='primary', timeMin=start_iso, timeMax=end_iso,
            singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events: return pd.DataFrame(), user_timezone

        rows = []
        for event in events:
            start_raw = event['start'].get('dateTime')
            end_raw = event['end'].get('dateTime')

            if start_raw and end_raw:
                # [Step B] 强制转换到用户日历的时区
                start_dt = pd.to_datetime(start_raw).tz_convert(user_timezone)
                end_dt = pd.to_datetime(end_raw).tz_convert(user_timezone)

                # 过滤日期 (使用本地日期比较)
                if start_dt.date() < start_date or start_dt.date() > end_date:
                    continue

                duration = (end_dt - start_dt).total_seconds() / 3600
                name = event.get('summary', 'Untitled').strip()  # 保持中文原样

                date_str = start_dt.strftime('%Y-%m-%d')
                time_range_str = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
                full_time_label = f"{date_str}, {time_range_str}"

                raw_color = event.get('colorId', 'Default')
                color_info = COLOR_MAP.get(raw_color, COLOR_MAP['Default'])

                rows.append({
                    'Event Name': name,
                    'Duration': round(duration, 2),
                    'Hex Color': color_info['hex'],
                    'Cat Emoji': color_info['emoji'],
                    'Local Start': start_dt,
                    'Local End': end_dt,
                    'Time Interval': full_time_label,
                    # [Step C] 计算小时数时，现在使用的是正确的本地小时
                    'Start Hour': start_dt.hour + start_dt.minute / 60.0,
                    'Start Time Str': start_dt.strftime('%H:%M'),
                    'End Time Str': end_dt.strftime('%H:%M')
                })
        return pd.DataFrame(rows), user_timezone
    except Exception as e:
        st.error(f"API Connection Error: {e}")
        return pd.DataFrame(), "UTC"


# --- 4. 渲染引擎 ---
def solve_overlaps(df_subset):
    df_subset = df_subset.sort_values('Local Start')
    lanes = []
    assignments = []

    for _, row in df_subset.iterrows():
        start = row['Local Start']
        placed = False
        for i, end_time in enumerate(lanes):
            if start >= (end_time - datetime.timedelta(minutes=5)):
                lanes[i] = row['Local End']
                assignments.append(i)
                placed = True
                break
        if not placed:
            lanes.append(row['Local End'])
            assignments.append(len(lanes) - 1)
    return assignments, len(lanes)


def plot_swimlane_timeline(df, timezone_name):
    unique_events = df['Event Name'].unique()
    unique_events = sorted(unique_events, reverse=True)

    total_sub_lanes = 0
    for evt in unique_events:
        _, max_sub = solve_overlaps(df[df['Event Name'] == evt])
        total_sub_lanes += max_sub

    fig_height = max(3, total_sub_lanes * 0.8 + len(unique_events) * 0.5)
    fig, ax = plt.subplots(figsize=(14, fig_height))

    y_cursor = 0
    y_ticks = []
    y_labels = []

    LANE_HEIGHT = 0.6
    BAR_HEIGHT = 0.15

    for event_name in unique_events:
        subset = df[df['Event Name'] == event_name].copy()
        sub_lanes, max_sub = solve_overlaps(subset)

        category_total_height = max_sub * LANE_HEIGHT

        center_y = y_cursor + category_total_height / 2
        y_ticks.append(center_y)
        y_labels.append(event_name)

        ax.axhspan(y_cursor, y_cursor + category_total_height, color='gray', alpha=0.05)

        for (idx, row), sub_idx in zip(subset.iterrows(), sub_lanes):
            bar_y = y_cursor + (sub_idx * LANE_HEIGHT) + 0.1

            # 绘制条形
            ax.broken_barh([(row['Start Hour'], row['Duration'])],
                           (bar_y, BAR_HEIGHT),
                           facecolors=row['Hex Color'],
                           edgecolor='none', alpha=0.9)

            # 绘制上方文字
            text_y = bar_y + BAR_HEIGHT + 0.05
            label_text = f"{row['Start Time Str']}-{row['End Time Str']} ({row['Duration']}h)"

            ax.text(row['Start Hour'] + row['Duration'] / 2, text_y,
                    label_text,
                    ha='center', va='bottom',
                    color='black', fontsize=8, fontweight='normal')

        y_cursor += category_total_height + 0.2

    ax.set_xlim(0, 24)
    ax.set_xticks(range(0, 25, 1))
    ax.set_xlabel(f"Hour of Day ({timezone_name} Time)", fontsize=10, fontweight='bold')

    ax.set_ylim(0, y_cursor)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=11, fontweight='bold')
    ax.grid(axis='x', linestyle=':', alpha=0.3)

    if not df.empty:
        date_str = df.iloc[0]['Local Start'].strftime('%A, %d %B %Y')
        ax.set_title(f"Activity Timeline - {date_str}", loc='left', pad=15, fontsize=14)

    st.pyplot(fig)


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = pct * total / 100.0
        return f'{pct:.1f}%\n({val:.1f}h)'

    return my_autopct


# --- 5. 主程序 ---
def main():
    # 名称修改 2: 主标题更新
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

    df, user_tz = fetch_calendar_data(start_date, end_date)

    if not df.empty:
        if mode == "Specific Day":
            st.subheader("📅 Daily Timeline")
            plot_swimlane_timeline(df, user_tz)
            st.markdown("---")

        st.subheader("🍩 Aggregated Stats")
        _, col_pie, _ = st.columns([1, 1, 1])
        with col_pie:
            dist = df.groupby(['Event Name', 'Hex Color'])['Duration'].sum().reset_index()
            fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
            ax_pie.pie(
                dist['Duration'],
                labels=dist['Event Name'],
                autopct=make_autopct(dist['Duration']),
                startangle=140,
                colors=dist['Hex Color'],
                textprops={'fontsize': 10}
            )
            ax_pie.set_title(f"Total: {df['Duration'].sum():.2f} hrs", fontweight='bold')
            st.pyplot(fig_pie)

        st.markdown("---")

        st.subheader("📝 Detailed Log")
        df_sorted = df.sort_values(by='Local Start', ascending=False)
        display_df = df_sorted[['Event Name', 'Duration', 'Time Interval', 'Cat Emoji']]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Duration": st.column_config.NumberColumn("Hrs", format="%.2f ⏳", width="small"),
                "Time Interval": st.column_config.TextColumn("Date & Time Range", width="medium"),
                "Cat Emoji": st.column_config.TextColumn("Cat", width="small")
            }
        )
    else:
        st.info("No events found for the selected period.")


if __name__ == '__main__':
    main()
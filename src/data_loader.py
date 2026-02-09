import datetime
import re
import pandas as pd
import streamlit as st
from src.auth import get_calendar_service
from src.config import COLOR_MAP


def parse_html_description(raw_html):
    """
    智能解析 Google Calendar 的 HTML 备注
    返回: (tooltip_str, markdown_str, short_str)
    """
    if not raw_html:
        return "<i>(No notes)</i>", "_No additional notes_", ""

    text = raw_html.replace('<li>', '\n- ')
    text = re.sub(r'</li>|<br>|<br/>|</p>|</div>|</ul>', '\n', text)

    cleanr = re.compile('<.*?>')
    text = re.sub(cleanr, '', text)

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    tooltip_str = "<br>".join(lines)
    markdown_str = "\n".join(lines)

    # 生成表格用的短摘要
    full_text = " ".join(lines)
    if len(full_text) > 50:
        short_str = full_text[:50] + "..."
    else:
        short_str = full_text

    return tooltip_str, markdown_str, short_str


@st.cache_data(ttl=300)
def fetch_calendar_data(start_date, end_date):
    """从 Google Calendar 获取数据并清洗为 DataFrame"""
    try:
        service = get_calendar_service()

        calendar_info = service.calendars().get(calendarId='primary').execute()
        user_timezone = calendar_info.get('timeZone', 'UTC')

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
                start_dt = pd.to_datetime(start_raw).tz_convert(user_timezone)
                end_dt = pd.to_datetime(end_raw).tz_convert(user_timezone)

                if start_dt.date() < start_date or start_dt.date() > end_date:
                    continue

                duration = (end_dt - start_dt).total_seconds() / 3600
                name = event.get('summary', 'Untitled').strip()

                raw_desc = event.get('description', '')
                tooltip_desc, markdown_desc, short_desc = parse_html_description(raw_desc)

                raw_color = event.get('colorId', 'Default')
                color_info = COLOR_MAP.get(raw_color, COLOR_MAP['Default'])

                date_obj = start_dt.date()
                time_range = f"{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}"
                event_id = str(start_dt.value)

                rows.append({
                    'Event ID': event_id,
                    'Date': date_obj,
                    'Event Name': name,
                    'Duration Val': duration,
                    'Duration Label': f"{duration:.2f}h ⏳",
                    'Hex Color': color_info['hex'],
                    'Cat Emoji': color_info['emoji'],
                    'Local Start': start_dt,
                    'Local End': end_dt,
                    'Time Span': time_range,
                    'Tooltip Description': tooltip_desc,
                    'Markdown Description': markdown_desc,
                    'Short Notes': short_desc,  # 纯文本
                })
        return pd.DataFrame(rows), user_timezone
    except Exception as e:
        st.error(f"API Connection Error: {e}")
        return pd.DataFrame(), "UTC"
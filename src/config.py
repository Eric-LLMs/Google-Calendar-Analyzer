# src/config.py

# Scope for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Updated Color Map with Professional Execution Emojis
COLOR_MAP = {
    '1':  {'label': 'Lavender',  'hex': '#7986cb', 'emoji': '☕'},  # 娱乐社交 (Leisure & Social)
    '2':  {'label': 'Sage',      'hex': '#33b679', 'emoji': '😴💤'},  # 睡觉 (Sleep - Primary)
    '3':  {'label': 'Grape',     'hex': '#8e24aa', 'emoji': '☕'},  # 娱乐社交 (Social)
    '4':  {'label': 'Flamingo',  'hex': '#e67c73', 'emoji': '🧠'},  # 学习提升 (Learning & Growth)
    '5':  {'label': 'Banana',    'hex': '#f6bf26', 'emoji': '📞'},  # 家庭事务 (Domestic Affairs)
    '6':  {'label': 'Tangerine', 'hex': '#f4511e', 'emoji': '👨‍💻'},  # 工作 (System/Engineering)
    '7':  {'label': 'Peacock',   'hex': '#039be5', 'emoji': '☕'},  # 日常 (Daily Routine)
    '8':  {'label': 'Graphite',  'hex': '#616161', 'emoji': '📓'},  # 工作 (Documentation/Review)
    '9':  {'label': 'Blueberry', 'hex': '#3f51b5', 'emoji': '🍹'},  # 娱乐社交 (Leisure and Relaxation)
    '10': {'label': 'Basil',     'hex': '#0b8043', 'emoji': '💤'},  # 睡觉 (Recovery/Nap)
    '11': {'label': 'Tomato',    'hex': '#d50000', 'emoji': '👨‍💻'},  # 工作 (Development/Deep Work)
    'Default': {'label': 'Default', 'hex': '#039be5', 'emoji': '🗓️'} # 默认日常
}
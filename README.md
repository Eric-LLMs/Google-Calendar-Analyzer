# 📅 Daily Schedule Analyzer Dashboard

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31%2B-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A professional productivity telemetry dashboard that interfaces with the **Google Calendar API**. This tool ingests calendar events, normalizes temporal data, and visualizes daily schedules using a custom **Gantt-style Swimlane Engine** and aggregated distribution metrics.

Designed for engineers and professionals who need granular insights into their time allocation, context switching, and deep work distribution.

![Dashboard Demo](screenshots/dashboard_demo.png)

## ✨ Key Features

* **ETL Pipeline**:
    * **Wide-Fetch Strategy**: Automatically broadens the API query window to handle UTC timezone offsets, ensuring no data loss for evening events.
    * **Timezone Synchronization**: Auto-detects and converts calendar events to the user's local system time.
    * **Normalization**: Cleanses event titles and color metadata for accurate categorical aggregation.

* **Visualization Engine**:
    * **Smart Swimlanes**: Implements a greedy algorithm (`solve_overlaps`) to detect temporal collisions and render overlapping events in stacked sub-lanes.
    * **Precision Timeline**: 24-hour linear visualization with slim bars and external annotation for high information density.
    * **Color Binding**: Strict Hex-code synchronization between Google Calendar source, Timeline, and Distribution charts.

* **CJK Support**: Built-in font configuration to support Chinese/Japanese/Korean characters in Matplotlib charts.

## 🛠️ Tech Stack

* **Frontend**: Streamlit
* **Data Processing**: Pandas
* **Visualization**: Matplotlib (Custom patches & broken_barh)
* **Backend**: Google Client Library for Python

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/daily-schedule-analyzer.git](https://github.com/your-username/daily-schedule-analyzer.git)
cd daily-schedule-analyzer

```

### 2. Install Dependencies

It is recommended to use a virtual environment to avoid conflicts.

```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate

# Install libraries
pip install -r requirements.txt

```

*Create a `requirements.txt` file with the following content if it doesn't exist:*

```text
streamlit
pandas
matplotlib
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client

```

### 3. Google Calendar API Setup (Crucial)

To run this app, you need your own credentials from the Google Cloud Console.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the **Google Calendar API**.
3. Configure the **OAuth consent screen** (set to "External" and add your email as a test user).
4. Go to **Credentials** -> **Create Credentials** -> **OAuth client ID** (Desktop App).
5. Download the JSON file, rename it to `credentials.json`, and place it in the **project root directory**.

### 4. Run the Dashboard

```bash
streamlit run app.py

```

*On the first run, a browser window will open asking you to log in to your Google account to authorize read-only access to your calendar. A `token.json` file will be generated automatically for future logins.*

## 📊 Usage Guide

* **Select Mode**: Choose between "Specific Day", "Last N Days", or "Custom Range" from the top dropdown.
* **Timeline View**: For single-day analysis, the Swimlane Timeline shows exact start/end times. Overlapping events are automatically stacked to avoid visual clutter.
* **Aggregated Stats**: The Pie Chart shows the percentage breakdown of your time based on Event Color categories (e.g., Deep Work vs. Meetings).
* **Detailed Log**: A tabular view at the bottom provides raw data export capabilities with precise timestamps.

## 🔒 Privacy Note

This application runs **locally** on your machine.

* Your calendar data is processed in-memory using Pandas.
* No data is sent to any third-party server (other than Google's API for fetching).
* Your `credentials.json` and `token.json` contain sensitive access keys—**never commit them to GitHub**.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

```

```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📋 Project Overview

This is a multi-purpose project with three main components:

1. **Daily Report Auto-Generation** (`daily_report.py`): Fetches Gmail messages and generates daily reports in Google Docs using Claude AI
2. **Semiconductor News Distribution** (`semiconductor_news_sender.py`): Sends Japanese semiconductor market analysis and news via Gmail and Google Sheets
3. **Feedback Management System** (Google Apps Script): Manages orientation feedback with Good/More labeling and automated statistics dashboard

**Development Branch:** `claude/daily-semiconductor-news-FAWWp`

---

## 🏗️ Architecture & File Structure

### Core Scripts
- **`daily_report.py`**: Main script that:
  - Fetches emails from Gmail API (sent/received)
  - Summarizes content using Claude AI API
  - Creates formatted Google Docs document with: Date, Daily Summary, Actions Taken, Next Day Plans

- **`semiconductor_news_sender.py`**: Generates and distributes Japanese semiconductor market analysis including:
  - Stock movement analysis (Micron/MU)
  - Market trends and catalysts
  - Risk factors and economic indicators
  - Can be sent via Gmail or Google Sheets

- **`create_template_excel_v2.py` & `create_template_excel.py`**: Generate Excel templates with sample data and formatting (8-column structure with day-of-week support)

- **`create_excel_feedback.py`**: Creates feedback analysis Excel with Good/More categorization and statistics

### Google Apps Script (Feedback Management)
- **`google_apps_script_v3.gs`** (Current version - Use this):
  - 8-column structure: Date | Day-of-Week | Item | Good/More | Details | Next Action① | Next Action② | Feedback Count
  - Auto-calculates day-of-week from date input
  - Dropdown menus: Good/More, Items (5 categories), Next Actions (47 options)
  - Automatic color coding (green for Good, orange for More)
  - Auto-generates statistics dashboard with Next Action rankings
  
- **`google_apps_script_v2.gs`** & **`google_apps_script.gs`**: Previous versions (legacy)

### Cloud Functions
- **`cloud_function/main.py`**: Scheduled Cloud Function (basic)
- **`cloud_function/main_gmail.py`**: Gmail integration for Cloud Functions

### Documentation
- **`README.md`**: User-facing setup and execution guide
- **`GOOGLE_SHEET_SETUP.md`**: Feedback management system setup instructions
- **`CLOUD_FUNCTION_SETUP.md`**: Cloud Function deployment guide
- **`DEPLOY_GMAIL_FUNCTION.md`**: Gmail-specific Cloud Function setup

---

## 🔧 Common Commands

### Daily Report Generation
```bash
python daily_report.py
```
Creates a new Google Docs file named `日報_YYYYMMDD` with automated content from Gmail analysis.

### Semiconductor News Distribution
```bash
python semiconductor_news_sender.py
```
Generates and sends Japanese semiconductor market analysis.

### Excel Template Generation
```bash
# Standard template (7 columns)
python create_template_excel.py

# Updated template (8 columns with day-of-week)
python create_template_excel_v2.py
```

### Feedback Analysis Excel
```bash
python create_excel_feedback.py
```

### Deploy to Google Cloud Function
```bash
gcloud functions deploy daily-report --runtime python312 --trigger-http
```

---

## ⚙️ Critical Setup Requirements

### Environment Variables
```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxx"
export GOOGLE_CLOUD_PROJECT_ID="your-project-id"
```

### Google Cloud Configuration
1. **Required APIs**: Gmail API, Google Docs API, Google Drive API, Google Sheets API
2. **OAuth Credentials**: Download `credentials.json` from Google Cloud Console (Desktop App type)
   - Place in project root directory
   - MUST be added to `.gitignore`
3. **First Run**: Execute `daily_report.py` to generate `token.json` (also in `.gitignore`)

### Google Apps Script Deployment
1. Open target Google Sheet → Extensions → Apps Script
2. Delete default code
3. Copy entire `google_apps_script_v3.gs` and paste
4. Save (Ctrl+S)
5. Select `initializeSheet` function
6. Click Run and grant permissions
7. Sheets created: "フィードバック入力" and "統計ダッシュボード"

### Dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client anthropic openpyxl
```

---

## 📊 Data Flow

### Daily Report
```
Gmail API → Extract emails → Claude AI summarization → Google Docs API → Create document
```

### Feedback Management
```
Google Sheet (user input) → Apps Script onEdit() → Color coding + Day calc
→ updateStatistics() → Auto-generated dashboard
```

### News Distribution
```
Semiconductor data (hardcoded/API) → Format → Gmail/Sheets → Distribution
```

---

## 🚀 Important Notes

- **API Keys are sensitive**: Always keep in environment variables, never commit
- **Token Management**: `token.json` is auto-generated after first OAuth authentication
- **Google Apps Script Versioning**: v3.gs is the current version with full 8-column support
- **Excel Templates**: v2 is updated for day-of-week column support; use v2 for new projects
- **Autorun with Cron**: Example in README.md (daily at 18:00)

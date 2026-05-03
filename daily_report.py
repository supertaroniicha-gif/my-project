#!/usr/bin/env python3
"""
日報自動生成スクリプト
Gmail APIで今日のメールを取得し、Claude AIで要約してGoogle Docsに日報を作成する。
"""

import os
import base64
import datetime
from email.utils import parsedate_to_datetime

import anthropic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail・Google Docs・Google Calendar の読み書き権限
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/calendar.readonly",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_google_service(api_name: str, api_version: str):
    """Google API クライアントを認証して返す。"""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build(api_name, api_version, credentials=creds)


def get_today_emails(gmail_service) -> list[dict]:
    """今日受信・送信したメールの件名・差出人・本文（先頭500文字）を返す。"""
    today = datetime.date.today()
    query = f"after:{today.strftime('%Y/%m/%d')}"

    emails = []
    for label in ("INBOX", "SENT"):
        result = gmail_service.users().messages().list(
            userId="me", q=query, labelIds=[label], maxResults=50
        ).execute()

        messages = result.get("messages", [])
        for msg_ref in messages:
            msg = gmail_service.users().messages().get(
                userId="me", messageId=msg_ref["id"], format="full"
            ).execute()

            headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
            subject = headers.get("Subject", "(件名なし)")
            sender = headers.get("From", "")
            recipient = headers.get("To", "")
            body = _extract_body(msg["payload"])

            emails.append({
                "direction": "受信" if label == "INBOX" else "送信",
                "subject": subject,
                "from": sender,
                "to": recipient,
                "body": body[:500],
            })

    return emails


def _extract_body(payload: dict) -> str:
    """メールペイロードからプレーンテキストを再帰的に取り出す。"""
    mime_type = payload.get("mimeType", "")
    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    for part in payload.get("parts", []):
        text = _extract_body(part)
        if text:
            return text
    return ""


def get_week_events(calendar_service) -> list[dict]:
    """今日を含む1週間のGoogle Calendarイベントを取得する。"""
    today = datetime.date.today()
    week_start = today
    week_end = today + datetime.timedelta(days=7)

    events_result = calendar_service.events().list(
        calendarId="primary",
        timeMin=datetime.datetime.combine(week_start, datetime.time.min).isoformat() + "Z",
        timeMax=datetime.datetime.combine(week_end, datetime.time.min).isoformat() + "Z",
        maxResults=100,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    formatted_events = []

    for event in events:
        start = event.get("start", {})
        end = event.get("end", {})
        summary = event.get("summary", "(タイトルなし)")

        start_time = start.get("dateTime") or start.get("date")
        end_time = end.get("dateTime") or end.get("date")

        formatted_events.append({
            "title": summary,
            "start": start_time,
            "end": end_time,
            "description": event.get("description", ""),
        })

    return formatted_events


def summarize_with_claude(emails: list[dict], events: list[dict], today: datetime.date) -> dict:
    """Claude AIにメール・カレンダーイベント一覧を渡して日報の各セクションを生成させる。"""
    client = anthropic.Anthropic()

    if not emails:
        email_text = "（本日のメールはありません）"
    else:
        lines = []
        for i, e in enumerate(emails, 1):
            lines.append(
                f"[{i}] [{e['direction']}] 件名: {e['subject']}\n"
                f"    From: {e['from']} / To: {e['to']}\n"
                f"    本文: {e['body']}\n"
            )
        email_text = "\n".join(lines)

    if not events:
        event_text = "（1週間のカレンダーイベントはありません）"
    else:
        lines = []
        for i, ev in enumerate(events, 1):
            lines.append(
                f"[{i}] {ev['title']}\n"
                f"    開始: {ev['start']} / 終了: {ev['end']}"
            )
            if ev.get("description"):
                lines.append(f"    説明: {ev['description'][:200]}")
        event_text = "\n".join(lines)

    prompt = f"""以下は {today.strftime('%Y年%m月%d日')} に受信・送信したメールと、今後1週間のカレンダーイベントの一覧です。

【メール】
{email_text}

【1週間のカレンダーイベント】
{event_text}

これらをもとに、日報の各セクションを日本語で作成してください。
出力は必ず以下のJSON形式で返してください（コードブロック不要）：

{{
  "summary": "今日の業務まとめ（2〜3文）",
  "actions": "対応したことの箇条書き（・で始まる行を複数）",
  "tomorrow": "明日の予定の箇条書き（・で始まる行を複数）"
}}
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    text = message.content[0].text.strip()
    # JSONブロックが含まれている場合は取り出す
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


def build_report_text(today: datetime.date, sections: dict) -> str:
    """日報本文の文字列を組み立てる。"""
    date_str = today.strftime("%Y年%m月%d日")
    return f"""【日付】
{date_str}

【今日の業務まとめ】
{sections['summary']}

【対応したこと】
{sections['actions']}

【明日の予定】
{sections['tomorrow']}
"""


def create_google_doc(docs_service, drive_service, title: str, body_text: str) -> str:
    """Google Docsに新規ドキュメントを作成して本文を書き込み、URLを返す。"""
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": body_text,
            }
        }
    ]
    docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"


def main():
    today = datetime.date.today()
    print(f"日報生成開始: {today.strftime('%Y年%m月%d日')}")

    print("Google APIに接続中...")
    gmail_service = get_google_service("gmail", "v1")
    docs_service = get_google_service("docs", "v1")
    drive_service = get_google_service("drive", "v3")
    calendar_service = get_google_service("calendar", "v3")

    print("今日のメールを取得中...")
    emails = get_today_emails(gmail_service)
    print(f"  取得件数: {len(emails)}件")

    print("1週間のカレンダーイベントを取得中...")
    events = get_week_events(calendar_service)
    print(f"  取得件数: {len(events)}件")

    print("Claude AIで日報を生成中...")
    sections = summarize_with_claude(emails, events, today)

    report_text = build_report_text(today, sections)
    print("\n--- 生成された日報 ---")
    print(report_text)
    print("----------------------\n")

    title = f"日報_{today.strftime('%Y%m%d')}"
    print(f"Google Docsにドキュメント「{title}」を作成中...")
    url = create_google_doc(docs_service, drive_service, title, report_text)

    print(f"完了！ドキュメントURL: {url}")


if __name__ == "__main__":
    main()

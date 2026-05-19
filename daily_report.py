#!/usr/bin/env python3
"""
日報自動生成スクリプト
Gmail APIで今日のメールを取得し、Outlook カレンダーから予定を取得、
Claude AIで要約してGoogle Docsに日報を作成する。
"""

import os
import base64
import json
import datetime
from email.utils import parsedate_to_datetime

import anthropic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from azure.identity import InteractiveBrowserCredential
from msgraph.core import GraphClient

# Gmail・Google Docs の読み書き権限
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
OUTLOOK_CREDENTIALS_FILE = ".outlook_credentials"


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


def get_outlook_graph_client() -> GraphClient:
    """Outlook (Microsoft Graph) API クライアントを認証して返す。"""
    credential = InteractiveBrowserCredential()
    scopes = ["https://graph.microsoft.com/.default"]
    return GraphClient(credential=credential, scopes=scopes)


def get_today_calendar_events(graph_client: GraphClient) -> list[dict]:
    """Outlook カレンダーから今日のイベントを取得する。"""
    today = datetime.date.today()
    start = datetime.datetime.combine(today, datetime.time.min).isoformat()
    end = datetime.datetime.combine(today, datetime.time.max).isoformat()

    query_params = {
        "startDateTime": start,
        "endDateTime": end,
    }

    events = []
    try:
        response = graph_client.get(
            "/me/calendarview",
            params=query_params,
        )
        data = response.json()
        for event in data.get("value", []):
            events.append({
                "subject": event.get("subject", "(題目なし)"),
                "start": event.get("start", {}).get("dateTime", ""),
                "end": event.get("end", {}).get("dateTime", ""),
                "organizer": event.get("organizer", {}).get("emailAddress", {}).get("name", ""),
            })
    except Exception as e:
        print(f"Outlook カレンダー取得エラー: {e}")

    return events


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


def summarize_with_claude(emails: list[dict], events: list[dict], today: datetime.date) -> dict:
    """Claude AIにメールとカレンダー情報を渡して日報の各セクションを生成させる。"""
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
        event_text = "（本日のカレンダーイベントはありません）"
    else:
        lines = []
        for i, ev in enumerate(events, 1):
            lines.append(
                f"[{i}] {ev['subject']}\n"
                f"    開始: {ev['start']} / 終了: {ev['end']}\n"
                f"    主催者: {ev['organizer']}\n"
            )
        event_text = "\n".join(lines)

    prompt = f"""以下は {today.strftime('%Y年%m月%d日')} に受信・送信したメールと、カレンダーに登録されているイベントの一覧です。

【メール一覧】
{email_text}

【カレンダーイベント】
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

    print("Outlook カレンダーに接続中...")
    graph_client = get_outlook_graph_client()

    print("今日のメールを取得中...")
    emails = get_today_emails(gmail_service)
    print(f"  取得件数: {len(emails)}件")

    print("今日のカレンダーイベントを取得中...")
    events = get_today_calendar_events(graph_client)
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

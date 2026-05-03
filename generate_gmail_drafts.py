#!/usr/bin/env python3
"""
Excelから名刺データを読み込み、
Claude AIでAI研修営業メールを生成し、
Gmailの下書きに保存する。
"""

import os
import base64
import openpyxl
import anthropic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_gmail_service():
    """Gmail APIクライアントを認証して返す。"""
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

    return build("gmail", "v1", credentials=creds)


def load_excel_data(excel_file: str = "business_cards.xlsx") -> list[dict]:
    """Excelファイルから名刺データを読み込む。"""
    wb = openpyxl.load_workbook(excel_file)
    ws = wb.active

    cards_data = []
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
        if row[0] is None:
            break
        cards_data.append({
            "no": row[0],
            "name": row[1] or "様",
            "title": row[2] or "",
            "company": row[3] or "貴社",
            "email": row[4] or "",
            "phone": row[5] or "",
            "industry": row[6] or "一般企業",
        })

    return cards_data


def generate_sales_email(card_data: dict) -> str:
    """Claude AIを使ってAI研修営業メールを生成する。"""
    client = anthropic.Anthropic()

    company = card_data.get("company", "貴社")
    title = card_data.get("title", "")
    name = card_data.get("name", "様")
    industry = card_data.get("industry", "一般企業")

    prompt = f"""
あなたはAI研修サービスを販売するプロフェッショナルです。
以下の情報を持つ人物に対して、AI研修の営業メール本文を日本語で作成してください。

【相手情報】
- 名前: {name}
- 役職: {title if title != '不明' else '（役職不明）'}
- 会社: {company}
- 業種: {industry}

【要件】
1. 相手の業種や役職から推測される課題にフォーカス
2. AI研修が具体的にどのような価値をもたらすかを示す
3. 親切で専門的なトーン
4. 長さ：200～300文字
5. 署名は不要（本文のみ）

【出力形式】
メール本文のみを返してください。"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text.strip()


def create_gmail_draft(gmail_service, to_email: str, subject: str, body: str) -> bool:
    """Gmailに下書きメールを作成する。"""
    try:
        message = MIMEText(body, _charset="utf-8")
        message["to"] = to_email
        message["subject"] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        draft_body = {
            "message": {
                "raw": raw_message,
            }
        }

        gmail_service.users().drafts().create(userId="me", body=draft_body).execute()
        return True
    except Exception as e:
        print(f"    エラー: {e}")
        return False


def main():
    print("=" * 60)
    print("Excel → AI営業メール生成 → Gmail下書き保存")
    print("=" * 60)

    # 1. Excelから名刺データを読み込む
    print("\nExcelからデータを読み込み中...")
    try:
        cards_data = load_excel_data()
        print(f"✓ {len(cards_data)}件のデータを読み込み")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return

    # 2. Gmail APIに接続
    print("\nGoogle APIに接続中...")
    try:
        gmail_service = get_gmail_service()
        print("✓ Gmail サービス初期化完了")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return

    # 3. 各人物向けにメールを生成・保存
    print("\nAI営業メール生成・Gmail下書き保存中...")
    success_count = 0
    skip_count = 0

    for i, card_data in enumerate(cards_data, 1):
        name = card_data.get("name", "様")
        email = card_data.get("email", "")
        company = card_data.get("company", "")

        # メールアドレスの確認
        if not email or email == "不明" or "@" not in email:
            print(f"  [{i:2d}/20] {name} ({company}) - メールアドレスなしスキップ")
            skip_count += 1
            continue

        # メール生成
        subject = f"AI人材育成プログラムのご提案 - {company}"
        print(f"  [{i:2d}/20] {name} ({company})...", end=" ", flush=True)

        try:
            body = generate_sales_email(card_data)
            if create_gmail_draft(gmail_service, email, subject, body):
                print("✓")
                success_count += 1
            else:
                print("✗")
        except Exception as e:
            print(f"✗ ({e})")

    print("\n" + "=" * 60)
    print("✓ 完了！")
    print(f"  - Gmail下書き保存: {success_count}件")
    if skip_count > 0:
        print(f"  - スキップ（メール不明）: {skip_count}件")
    print("=" * 60)


if __name__ == "__main__":
    main()

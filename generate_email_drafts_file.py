#!/usr/bin/env python3
"""
Excelから名刺データを読み込み、
Claude AIでAI研修営業メールを生成し、
JSON形式で保存する。
"""

import json
import openpyxl
import anthropic

def load_excel_data(excel_file: str = "business_cards.xlsx"):
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


def main():
    print("=" * 70)
    print("Excel → AI営業メール生成 → JSON保存")
    print("=" * 70)

    # 1. Excelから名刺データを読み込む
    print("\n📄 Excelからデータを読み込み中...")
    try:
        cards_data = load_excel_data()
        print(f"✓ {len(cards_data)}件のデータを読み込み完了")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return

    # 2. 各人物向けにメールを生成
    print("\n🤖 AI営業メール生成中（Claude APIを使用）...\n")
    email_drafts = []

    for i, card_data in enumerate(cards_data, 1):
        name = card_data.get("name", "様")
        email = card_data.get("email", "")
        company = card_data.get("company", "")
        title = card_data.get("title", "")
        industry = card_data.get("industry", "")

        print(f"  [{i:2d}/20] {name} ({company})", end=" ", flush=True)

        try:
            # メール本文を生成
            body = generate_sales_email(card_data)

            # 下書きメール情報を作成
            draft = {
                "no": i,
                "to_name": name,
                "to_email": email,
                "to_company": company,
                "to_title": title,
                "to_industry": industry,
                "subject": f"AI人材育成プログラムのご提案 - {company}",
                "body": body,
            }
            email_drafts.append(draft)
            print("✓")

        except Exception as e:
            print(f"✗ エラー: {e}")

    # 3. JSONファイルに保存
    print(f"\n💾 JSONファイルに保存中...")
    output_file = "email_drafts.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(email_drafts, f, ensure_ascii=False, indent=2)

    print(f"✓ {output_file} に保存完了\n")

    # 4. 結果サマリーを表示
    print("=" * 70)
    print(f"✅ 完了！")
    print(f"   - 生成されたメール: {len(email_drafts)}件")
    print(f"   - 保存ファイル: {output_file}")
    print("=" * 70)

    # 5. 先頭3件をプレビュー表示
    print("\n📋 【メール下書きプレビュー】\n")
    for i, draft in enumerate(email_drafts[:3], 1):
        print(f"━━━━━ メール {i}/20 ━━━━━")
        print(f"宛先: {draft['to_name']} ({draft['to_company']})")
        print(f"メール: {draft['to_email']}")
        print(f"件名: {draft['subject']}\n")
        print(f"本文:")
        print(f"{draft['body']}\n")

    print("\n📝 その他18件も email_drafts.json に保存されています。")
    print("\n💡 このJSONファイルから、以下の方法でGmailに取り込めます:")
    print("   1. JSONファイルの内容をコピー")
    print("   2. Gmailで「下書き作成」→ テンプレート機能で利用")
    print("   3. または、Google Apps Scriptで自動化\n")


if __name__ == "__main__":
    main()

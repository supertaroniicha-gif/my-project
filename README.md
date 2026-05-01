# 日報自動生成スクリプト

GmailとGoogle Docsを使って、今日のメールをもとにClaude AIが日報を自動生成するPythonスクリプトです。

## 動作概要

1. Gmail APIで当日の受信・送信メールを取得
2. Claude AIがメール内容から業務内容を要約・整理
3. Google Docs APIで以下フォーマットの日報ドキュメントを新規作成

```
【日付】
【今日の業務まとめ】
【対応したこと】
【明日の予定】
```

---

## セットアップ手順

### 1. リポジトリのクローンと依存パッケージのインストール

```bash
git clone <このリポジトリのURL>
cd <リポジトリ名>
pip install -r requirements.txt
```

Python 3.10以上を推奨します。

---

### 2. Anthropic APIキーの取得

1. [Anthropic Console](https://console.anthropic.com/) にアクセスしてアカウントを作成
2. **API Keys** ページで新しいキーを発行
3. 環境変数に設定する

```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxx"
```

永続化する場合は `~/.bashrc` または `~/.zshrc` に追記してください。

---

### 3. Google Cloud プロジェクトの設定

#### 3-1. プロジェクト作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 上部のプロジェクト選択メニューから **新しいプロジェクト** を作成

#### 3-2. APIの有効化

以下の2つのAPIを有効化します。

| API | 用途 |
|-----|------|
| Gmail API | メールの読み取り |
| Google Docs API | 日報ドキュメントの作成 |
| Google Drive API | ドキュメントの権限設定 |

**手順：**
1. Cloud Console の左メニューから **APIとサービス > ライブラリ** を開く
2. 各APIを検索して **有効にする** をクリック

#### 3-3. OAuth 2.0 認証情報の作成

1. **APIとサービス > 認証情報** を開く
2. **認証情報を作成 > OAuthクライアントID** を選択
3. アプリケーションの種類: **デスクトップアプリ** を選択
4. 作成後、**JSONをダウンロード** してファイル名を `credentials.json` に変更
5. `credentials.json` をスクリプトと同じディレクトリに配置

#### 3-4. OAuth 同意画面の設定

1. **APIとサービス > OAuth同意画面** を開く
2. User Type: **外部** を選択して作成
3. アプリ名・メールアドレスなど必須項目を入力
4. **テストユーザー** にご自身のGmailアドレスを追加

---

### 4. 初回認証

スクリプトを初めて実行すると、ブラウザが起動してGoogleアカウントの認証画面が表示されます。

```bash
python daily_report.py
```

- Googleアカウントでログインし、アクセスを許可してください
- 認証が完了すると `token.json` が生成され、次回以降は自動ログインになります

---

## 実行方法

```bash
python daily_report.py
```

実行が完了すると、Google Drive に `日報_YYYYMMDD` という名前のドキュメントが作成され、URLがターミナルに表示されます。

### 毎日自動実行（cron）

毎日18時に自動実行する場合：

```bash
crontab -e
```

以下を追記（パスは環境に合わせて変更）：

```
0 18 * * 1-5 cd /path/to/project && ANTHROPIC_API_KEY=sk-ant-xxx /usr/bin/python3 daily_report.py >> daily_report.log 2>&1
```

---

## ファイル構成

```
.
├── daily_report.py     # メインスクリプト
├── requirements.txt    # 依存パッケージ
├── credentials.json    # Google OAuth認証情報（自分で配置）
├── token.json          # 認証トークン（初回実行後に自動生成）
└── README.md
```

> **注意：** `credentials.json` と `token.json` は機密情報です。`.gitignore` に追加してGitにコミットしないようにしてください。

---

## .gitignore への追加

```bash
echo "credentials.json" >> .gitignore
echo "token.json" >> .gitignore
```

---

## トラブルシューティング

| エラー | 対処法 |
|--------|--------|
| `credentials.json not found` | Google CloudからOAuth JSONをダウンロードして配置 |
| `ANTHROPIC_API_KEY not set` | 環境変数 `ANTHROPIC_API_KEY` を設定 |
| `Access Not Configured` | Cloud ConsoleでGmail/Docs/Drive APIを有効化 |
| `Token has been expired` | `token.json` を削除して再認証 |
| ブラウザが開かない | `flow.run_local_server` のポートが塞がれている場合は別ポートを指定 |

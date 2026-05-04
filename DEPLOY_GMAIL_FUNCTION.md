# Cloud Function デプロイガイド - Gmail自動送信

このガイドに従って、毎朝8時に日本語の半導体ニュースをGmailで自動送信するCloud Functionをデプロイします。

## 必要な情報

JSON認証情報から以下の値をコピーしておいてください:
```
private_key_id: 5507fcc17aca522b451f858bb16fdd53c7053fe1
private_key: -----BEGIN PRIVATE KEY-----\n... (全体をコピー)
client_email: semiconductor-news@appspot.gserviceaccount.com
client_id: 100787031187262074094
```

---

## デプロイ手順

### **Step 1: Cloud Functionsページに移動**

1. Google Cloud Console に移動
2. 左メニュー → **「Cloud Functions」**
3. **「関数を作成」** をクリック

### **Step 2: 関数の設定**

**基本設定:**
- **環境**: Python 3.11
- **関数名**: `send-semiconductor-news`
- **トリガータイプ**: `HTTPS`
- **認証**: チェックを外す (公開)
- **メモリ**: 256 MB
- **タイムアウト**: 60秒

### **Step 3: コードをコピー**

1. **メインコード** (`main.py`) に以下をコピー:
   - `/cloud_function/main_gmail.py` の内容

2. **requirements.txt** に以下をコピー:
```
functions-framework==3.*
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.100.0
```

3. **エントリポイント**: `send_semiconductor_news`

### **Step 4: 環境変数を設定**

1. 下の **「実行時設定の表示」** をクリック
2. **「環境変数」** タブ
3. 以下の環境変数を追加:

| 変数名 | 値 |
|--------|-----|
| `GCP_PROJECT_ID` | `semiconductor-news` |
| `PRIVATE_KEY_ID` | JSON から `private_key_id` |
| `PRIVATE_KEY` | JSON から `private_key` (改行をそのままコピー) |
| `CLIENT_EMAIL` | `semiconductor-news@appspot.gserviceaccount.com` |
| `CLIENT_ID` | `100787031187262074094` |

**⚠️ 注意**: `PRIVATE_KEY` は改行を含めてそのままコピーしてください

### **Step 5: デプロイ**

1. **「デプロイ」** ボタンをクリック
2. デプロイ完了まで待機 (1-2分)

---

## Cloud Scheduler で毎朝8時に実行

### **Step 1: Cloud Schedulerに移動**

1. Google Cloud Console
2. 左メニュー → **「Cloud Scheduler」**
3. **「ジョブを作成」** をクリック

### **Step 2: ジョブを設定**

**基本設定:**
- **名前**: `semiconductor-news-daily`
- **周期**: `0 8 * * *` (毎日8時)
- **タイムゾーン**: `Asia/Tokyo` (または任意)
- **実行する設定**: **Pub/Sub を使用** に変更

**Pub/Sub設定:**
1. トピック: **新規作成** → `semiconductor-news-trigger`
2. メッセージ本体: `{"trigger": "daily"}`

### **Step 3: HTTP トリガーに変更**

実は Pub/Sub ではなく、Cloud Function への **HTTP トリガー** を直接使用します:

1. **実行する設定**: **HTTP** に変更
2. **URL**: Cloud Function のURLをコピペ
   - Cloud Functions ページで関数をクリック
   - 「トリガー」タブ
   - **URL** をコピー
3. **HTTP メソッド**: `POST`

### **Step 4: 作成**

**「作成」** をクリック

---

## テスト方法

### Cloud Function をテスト:

1. Cloud Functions で関数をクリック
2. **「トリガー」** タブ
3. URLをコピーして **ブラウザで開く**
4. または、以下のコマンド実行:
```bash
curl -X POST https://YOUR-FUNCTION-URL
```

**期待される結果:**
- Gmailの受信トレイに「日次半導体ニュース」が到着
- supertaroniicha@gmail.com に送信

### Cloud Scheduler をテスト:

1. Cloud Scheduler ページ
2. ジョブをクリック
3. **「今すぐ実行」** ボタン
4. メールが送信されるか確認

---

## トラブルシューティング

### メールが送信されない:

1. **ログを確認:**
   - Cloud Functions → 関数 → ログ
   - エラーメッセージを確認

2. **よくあるエラー:**
   - `PRIVATE_KEY の改行がおかしい`: JSONをそのままコピー
   - `Gmail API が有効化されていない`: APIを有効化
   - `権限がない`: Service Account に権限があるか確認

### Cloud Scheduler が実行されない:

1. ジョブの詳細ページで「実行ステータス」を確認
2. URL が正しいか確認
3. 時間設定が正しいか確認 (JST で 8:00 = UTC で 23:00 前日)

---

## 料金

**完全に無料:**
- Cloud Functions: 月200万秒無料 ✅
- Cloud Scheduler: 月3ジョブまで無料 ✅
- Gmail API: 無料 ✅

毎日1回のメール送信 = 無料枠内

---

## デプロイ完了後

✅ 毎朝8時に自動実行
✅ supertaroniicha@gmail.com に日本語ニュース送信
✅ 完全無料
✅ 24時間自動運用

問題があれば、ログを確認してください！

# 📌 Meta広告 自動出稿システム

Meta広告の自動出稿を支援するPythonシステムです。Business Manager配下の複数クライアント広告アカウントに対して、CLI経由でMeta広告を自動作成・出稿できます。

## 🚀 機能

- **広告アカウント管理**: Business Manager配下の広告アカウント一覧取得・選択
- **テンプレートシステム**: 再利用可能な広告テンプレートの作成・管理・適用
- **クイック出稿**: テンプレートベースの高速広告作成
- **Google Sheets連携**: スプレッドシートでの入力・一括処理・進捗管理
- **Google Drive動画管理**: 動画検索・名前検索・フォルダ検索・データベース化
- **キャンペーン作成**: 目的・名称・ステータス指定でのキャンペーン作成
- **広告セット作成**: 予算・スケジュール・配信地域設定
- **クリエイティブ作成**: 動画・文言・リンクURL設定
- **広告作成・公開**: 完全な広告作成から出稿まで
- **ログ管理**: 出稿履歴とエラーログの記録
- **自動設定**: 日時・ターゲティング・最適化の自動設定

## 📋 要件

- Python 3.8+
- Meta Business Manager アカウント
- Meta Business API アクセストークン
- Google Cloud Platform アカウント（Google Sheets/Drive連携用）
- Google API 認証情報（サービスアカウントキー）
- facebook-business SDK
- Google API クライアントライブラリ

## 🛠️ セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/nagae-haruki/auto-meta.git
cd auto-meta
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`env.example`を参考に`.env`ファイルを作成し、以下の情報を設定してください：

```bash
# Meta Business API設定
META_ACCESS_TOKEN=your_long_lived_access_token_here
BUSINESS_MANAGER_ID=your_business_manager_id_here

# アプリ設定
APP_ID=your_facebook_app_id_here？
APP_SECRET=your_facebook_app_secret_here

# Google API設定
GOOGLE_CREDENTIALS_FILE=path/to/your/google-credentials.json
```

### 4. Meta Business API アクセストークンの取得

1. [Meta for Developers](https://developers.facebook.com/) でアプリを作成
2. Business Manager API の権限を取得
3. 長期アクセストークンを生成
4. Business Manager ID を取得

### 5. Google API 認証情報の取得

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. Google Sheets API と Google Drive API を有効化
3. サービスアカウントを作成
4. サービスアカウントキー（JSON）をダウンロード
5. ダウンロードしたJSONファイルのパスを環境変数に設定

## 🎯 使用方法

### WebUI での実行（推奨）

```bash
python run_web.py
```

ブラウザで http://localhost:8501 にアクセスしてWebUIを使用できます。

### CLI での実行

```bash
python main.py
```

### 操作フロー

#### WebUI（推奨）
1. **サービス初期化**: サイドバーでサービスを初期化
2. **キャンペーン作成**: 個別作成・一括作成・テンプレート使用から選択
3. **フォーム入力**: 直感的なWebフォームで情報を入力
4. **動画選択**: Google Driveから動画を検索・選択
5. **作成実行**: ワンクリックでキャンペーンを作成

#### Google Sheets連携
1. **シート作成**: キャンペーン入力シートを作成
2. **データ入力**: Google Sheetsでキャンペーン情報を入力
3. **動画検索**: Google Driveから動画を検索・選択
4. **一括処理**: シートからデータを読み込み・一括作成
5. **進捗管理**: シート上でステータスを自動更新

#### クイック出稿（テンプレート使用）
1. **テンプレート選択**: 事前作成したテンプレートから選択
2. **アカウント選択**: 利用可能な広告アカウントから選択
3. **基本情報入力**: キャンペーン名・商品名のみ入力
4. **設定確認**: テンプレート設定を確認・必要に応じてカスタマイズ
5. **確認・作成**: 入力内容を確認して広告を作成

#### 手動設定
1. **アカウント選択**: 利用可能な広告アカウントから選択
2. **キャンペーン設定**: 名前・目的を入力
3. **広告セット設定**: 予算・配信期間を設定
4. **クリエイティブ設定**: 見出し・説明文・URL・動画を設定
5. **確認・作成**: 入力内容を確認して広告を作成

## 📁 プロジェクト構造

```
auto-meta/
├── src/
│   ├── __init__.py
│   ├── config.py              # 設定管理
│   ├── meta_client.py         # Meta API クライアント
│   ├── cli.py                # CLI インターフェース
│   ├── logger.py             # ログ管理
│   ├── template_manager.py   # テンプレート管理
│   ├── google_sheets_manager.py # Google Sheets連携
│   └── google_drive_manager.py  # Google Drive動画管理
├── logs/                     # ログファイル
├── data/
│   ├── templates/            # テンプレートファイル
│   └── video_database.json   # 動画データベース
├── main.py                   # CLI メインエントリーポイント
├── web_app.py               # Streamlit WebUI
├── run_web.py               # WebUI起動スクリプト
├── requirements.txt          # 依存関係
└── README.md                # このファイル
```

## 🔧 開発ロードマップ

### MVP① (完了)
- ✅ CLI でクライアント選択＋キャンペーン作成
- ✅ 広告アカウント一覧取得
- ✅ キャンペーン作成（テスト）
- ✅ テンプレート管理システム
- ✅ クイック出稿機能
- ✅ 自動設定項目のテンプレート化
- ✅ Google Sheets連携機能
- ✅ Google Drive動画管理機能
- ✅ スプレッドシートベースの入力システム
- ✅ 動画検索・名前検索・フォルダ検索
- ✅ Streamlit WebUI
- ✅ 直感的なWebフォーム
- ✅ 一括処理機能
- ✅ リアルタイム進捗表示

### MVP② (予定)
- 広告セット＋クリエイティブ作成
- 予算・日程・URL・動画を反映

### MVP③ (予定)
- 広告完成 & 出稿
- 実際に出稿できる状態まで

### MVP④ (予定)
- WebフォームUI (Streamlit/Flask)
- 広告運用者がノーコード的に使える形に

### MVP⑤ (予定)
- 運用改善
- 出稿ログを一覧管理
- 配信停止・削除などの操作も可能に

## ⚠️ 注意事項

- 広告は最初に**一時停止状態**で作成されます
- 配信開始には、Meta広告マネージャーで手動で有効化が必要です
- アクセストークンは適切に管理し、定期的に更新してください
- 本番環境での使用前に、テストアカウントで十分にテストしてください

## 📝 ライセンス

このプロジェクトのライセンスについては、今後決定予定です。

## 🤝 貢献

プルリクエストやイシューの報告を歓迎します。

## 📞 サポート

問題が発生した場合は、GitHubのIssuesで報告してください。

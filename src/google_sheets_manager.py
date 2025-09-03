"""
Google Sheets連携管理システム
"""
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from typing import Dict, List, Optional, Any
import os
from datetime import datetime

class GoogleSheetsManager:
    """Google Sheets連携管理クラス"""
    
    def __init__(self, credentials_file=None):
        """初期化"""
        self.credentials_file = credentials_file or os.getenv('GOOGLE_CREDENTIALS_FILE')
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Google Sheets クライアントを初期化"""
        try:
            if not self.credentials_file or not os.path.exists(self.credentials_file):
                print("⚠️ Google認証ファイルが見つかりません。")
                print("   GOOGLE_CREDENTIALS_FILE 環境変数を設定してください。")
                return False
            
            # スコープを設定
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # 認証情報を読み込み
            creds = Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=scope
            )
            
            # クライアントを初期化
            self.client = gspread.authorize(creds)
            print("✅ Google Sheets クライアントが初期化されました")
            return True
            
        except Exception as e:
            print(f"❌ Google Sheets 初期化エラー: {e}")
            return False
    
    def create_campaign_sheet(self, sheet_name: str = None) -> Optional[str]:
        """キャンペーン入力用のスプレッドシートを作成"""
        try:
            if not self.client:
                print("❌ Google Sheets クライアントが初期化されていません")
                return None
            
            # シート名を生成
            if not sheet_name:
                sheet_name = f"Meta広告キャンペーン_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # スプレッドシートを作成
            spreadsheet = self.client.create(sheet_name)
            
            # ワークシートを設定
            worksheet = spreadsheet.sheet1
            worksheet.title = "キャンペーン入力"
            
            # ヘッダー行を設定
            headers = [
                "キャンペーン名", "商品名", "目的", "予算(円/日)", 
                "開始日", "終了日", "見出し", "説明文", "URL", 
                "動画名", "動画ID", "ステータス", "作成日時"
            ]
            
            worksheet.append_row(headers)
            
            # フォーマット設定
            worksheet.format('A1:M1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })
            
            # 列幅を調整
            worksheet.columns_auto_resize(0, len(headers) - 1)
            
            print(f"✅ スプレッドシートを作成しました: {spreadsheet.url}")
            return spreadsheet.url
            
        except Exception as e:
            print(f"❌ スプレッドシート作成エラー: {e}")
            return None
    
    def read_campaign_data(self, spreadsheet_url: str) -> List[Dict[str, Any]]:
        """スプレッドシートからキャンペーンデータを読み込み"""
        try:
            if not self.client:
                print("❌ Google Sheets クライアントが初期化されていません")
                return []
            
            # スプレッドシートを開く
            spreadsheet = self.client.open_by_url(spreadsheet_url)
            worksheet = spreadsheet.sheet1
            
            # データを取得
            records = worksheet.get_all_records()
            
            # 有効なデータのみフィルタリング
            valid_records = []
            for record in records:
                if record.get('キャンペーン名') and record.get('ステータス') != '完了':
                    valid_records.append(record)
            
            return valid_records
            
        except Exception as e:
            print(f"❌ データ読み込みエラー: {e}")
            return []
    
    def update_campaign_status(self, spreadsheet_url: str, campaign_name: str, status: str, campaign_id: str = None):
        """キャンペーンのステータスを更新"""
        try:
            if not self.client:
                return False
            
            # スプレッドシートを開く
            spreadsheet = self.client.open_by_url(spreadsheet_url)
            worksheet = spreadsheet.sheet1
            
            # データを取得
            records = worksheet.get_all_records()
            
            # 該当するキャンペーンを検索
            for i, record in enumerate(records, start=2):  # ヘッダー行をスキップ
                if record.get('キャンペーン名') == campaign_name:
                    # ステータスを更新
                    worksheet.update_cell(i, 12, status)  # ステータス列
                    worksheet.update_cell(i, 13, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))  # 作成日時列
                    
                    if campaign_id:
                        # キャンペーンIDを追加（新しい列が必要な場合は拡張）
                        pass
                    
                    print(f"✅ キャンペーン '{campaign_name}' のステータスを '{status}' に更新しました")
                    return True
            
            print(f"❌ キャンペーン '{campaign_name}' が見つかりません")
            return False
            
        except Exception as e:
            print(f"❌ ステータス更新エラー: {e}")
            return False
    
    def create_template_sheet(self, template_name: str) -> Optional[str]:
        """テンプレート設定用のスプレッドシートを作成"""
        try:
            if not self.client:
                return None
            
            sheet_name = f"テンプレート_{template_name}_{datetime.now().strftime('%Y%m%d')}"
            spreadsheet = self.client.create(sheet_name)
            worksheet = spreadsheet.sheet1
            worksheet.title = "テンプレート設定"
            
            # テンプレート設定用のヘッダー
            headers = [
                "設定項目", "値", "説明", "必須", "デフォルト値"
            ]
            
            # テンプレート設定データ
            template_data = [
                ["テンプレート名", template_name, "テンプレートの名前", "必須", ""],
                ["説明", "", "テンプレートの説明", "任意", ""],
                ["キャンペーン目的", "LINK_CLICKS", "キャンペーンの目的", "必須", "LINK_CLICKS"],
                ["デフォルト予算", "1000", "デフォルトの1日予算（円）", "必須", "1000"],
                ["配信期間", "7日間", "デフォルトの配信期間", "必須", "7日間"],
                ["見出しテンプレート", "【{product_name}】今だけ特別価格！", "見出しのテンプレート", "必須", "【{product_name}】今だけ特別価格！"],
                ["説明文テンプレート", "お得な情報をお見逃しなく！詳細はこちらから。", "説明文のテンプレート", "必須", "お得な情報をお見逃しなく！詳細はこちらから。"],
                ["URLテンプレート", "https://example.com/{campaign_name}", "URLのテンプレート", "必須", "https://example.com/{campaign_name}"],
                ["ターゲット年齢最小", "18", "ターゲット年齢の最小値", "必須", "18"],
                ["ターゲット年齢最大", "65", "ターゲット年齢の最大値", "必須", "65"],
                ["ターゲット性別", "男女両方", "ターゲット性別（男性/女性/両方）", "必須", "両方"],
                ["配信地域", "日本", "配信地域", "必須", "日本"]
            ]
            
            worksheet.append_row(headers)
            for row in template_data:
                worksheet.append_row(row)
            
            # フォーマット設定
            worksheet.format('A1:E1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })
            
            worksheet.columns_auto_resize(0, 4)
            
            print(f"✅ テンプレート設定シートを作成しました: {spreadsheet.url}")
            return spreadsheet.url
            
        except Exception as e:
            print(f"❌ テンプレートシート作成エラー: {e}")
            return None
    
    def read_template_data(self, spreadsheet_url: str) -> Dict[str, Any]:
        """テンプレート設定シートからデータを読み込み"""
        try:
            if not self.client:
                return {}
            
            spreadsheet = self.client.open_by_url(spreadsheet_url)
            worksheet = spreadsheet.sheet1
            records = worksheet.get_all_records()
            
            template_data = {}
            for record in records:
                setting_name = record.get('設定項目', '')
                value = record.get('値', '')
                if setting_name and value:
                    template_data[setting_name] = value
            
            return template_data
            
        except Exception as e:
            print(f"❌ テンプレートデータ読み込みエラー: {e}")
            return {}
    
    def create_batch_sheet(self, campaigns: List[Dict[str, Any]]) -> Optional[str]:
        """一括キャンペーン作成用のスプレッドシートを作成"""
        try:
            if not self.client:
                return None
            
            sheet_name = f"一括キャンペーン_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            spreadsheet = self.client.create(sheet_name)
            worksheet = spreadsheet.sheet1
            worksheet.title = "一括キャンペーン"
            
            # ヘッダー
            headers = [
                "キャンペーン名", "商品名", "テンプレート名", "予算(円/日)", 
                "開始日", "終了日", "見出し", "説明文", "URL", 
                "動画名", "ステータス", "作成日時", "キャンペーンID"
            ]
            
            worksheet.append_row(headers)
            
            # データを追加
            for campaign in campaigns:
                row = [
                    campaign.get('campaign_name', ''),
                    campaign.get('product_name', ''),
                    campaign.get('template_name', ''),
                    campaign.get('budget', ''),
                    campaign.get('start_date', ''),
                    campaign.get('end_date', ''),
                    campaign.get('headline', ''),
                    campaign.get('description', ''),
                    campaign.get('url', ''),
                    campaign.get('video_name', ''),
                    '待機中',
                    '',
                    ''
                ]
                worksheet.append_row(row)
            
            # フォーマット設定
            worksheet.format('A1:M1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })
            
            worksheet.columns_auto_resize(0, len(headers) - 1)
            
            print(f"✅ 一括キャンペーンシートを作成しました: {spreadsheet.url}")
            return spreadsheet.url
            
        except Exception as e:
            print(f"❌ 一括シート作成エラー: {e}")
            return None

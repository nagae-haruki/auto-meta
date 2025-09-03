"""
CLI インターフェース
"""
import sys
from datetime import datetime, timedelta
from .meta_client import MetaAdsClient
from .logger import AdLogger

class MetaAdsCLI:
    """Meta広告自動出稿システム CLI"""
    
    def __init__(self):
        """初期化"""
        self.client = MetaAdsClient()
        self.logger = AdLogger()
    
    def display_welcome(self):
        """ウェルカムメッセージ表示"""
        print("=" * 60)
        print("📌 Meta広告 自動出稿システム")
        print("=" * 60)
        print("このシステムを使用してMeta広告を自動で作成・出稿できます。")
        print()
    
    def select_ad_account(self):
        """広告アカウント選択"""
        print("📋 広告アカウント一覧を取得中...")
        
        try:
            accounts = self.client.get_ad_accounts()
            
            if not accounts:
                print("❌ 利用可能な広告アカウントが見つかりません。")
                return None
            
            print("\n📋 利用可能な広告アカウント:")
            print("-" * 50)
            
            for i, account in enumerate(accounts, 1):
                status_emoji = "✅" if account['status'] == 1 else "⚠️"
                print(f"{i}. {status_emoji} {account['name']} (ID: {account['id']})")
            
            while True:
                try:
                    choice = int(input(f"\nアカウントを選択してください (1-{len(accounts)}): "))
                    if 1 <= choice <= len(accounts):
                        selected_account = accounts[choice - 1]
                        print(f"✅ 選択されたアカウント: {selected_account['name']}")
                        return selected_account
                    else:
                        print("❌ 無効な選択です。")
                except ValueError:
                    print("❌ 数値を入力してください。")
                    
        except Exception as e:
            print(f"❌ アカウント取得エラー: {e}")
            self.logger.log_account_access({}, False, str(e))
            return None
    
    def get_campaign_input(self):
        """キャンペーン情報入力"""
        print("\n📝 キャンペーン情報を入力してください:")
        print("-" * 40)
        
        campaign_name = input("キャンペーン名: ").strip()
        if not campaign_name:
            print("❌ キャンペーン名は必須です。")
            return None
        
        print("\n📊 キャンペーン目的を選択してください:")
        objectives = {
            '1': 'LINK_CLICKS',
            '2': 'CONVERSIONS',
            '3': 'REACH',
            '4': 'BRAND_AWARENESS'
        }
        
        for key, value in objectives.items():
            print(f"{key}. {value}")
        
        objective_choice = input("目的を選択 (1-4, デフォルト: 1): ").strip() or '1'
        objective = objectives.get(objective_choice, 'LINK_CLICKS')
        
        return {
            'name': campaign_name,
            'objective': objective
        }
    
    def get_ad_set_input(self):
        """広告セット情報入力"""
        print("\n💰 広告セット情報を入力してください:")
        print("-" * 40)
        
        ad_set_name = input("広告セット名: ").strip()
        if not ad_set_name:
            print("❌ 広告セット名は必須です。")
            return None
        
        try:
            budget = float(input("1日予算 (円): "))
            if budget <= 0:
                print("❌ 予算は0より大きい値である必要があります。")
                return None
        except ValueError:
            print("❌ 有効な数値を入力してください。")
            return None
        
        # 配信期間設定
        print("\n📅 配信期間を設定してください:")
        start_date = input("開始日 (YYYY-MM-DD, デフォルト: 今日): ").strip()
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        end_date = input("終了日 (YYYY-MM-DD, デフォルト: 1週間後): ").strip()
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        return {
            'name': ad_set_name,
            'budget': budget,
            'start_date': start_date,
            'end_date': end_date
        }
    
    def get_creative_input(self):
        """クリエイティブ情報入力"""
        print("\n🎨 広告クリエイティブ情報を入力してください:")
        print("-" * 40)
        
        creative_name = input("クリエイティブ名: ").strip()
        if not creative_name:
            print("❌ クリエイティブ名は必須です。")
            return None
        
        headline = input("見出し: ").strip()
        if not headline:
            print("❌ 見出しは必須です。")
            return None
        
        description = input("説明文: ").strip()
        if not description:
            print("❌ 説明文は必須です。")
            return None
        
        url = input("リンク先URL: ").strip()
        if not url:
            print("❌ リンク先URLは必須です。")
            return None
        
        video_id = input("動画ID (オプション): ").strip()
        
        return {
            'name': creative_name,
            'headline': headline,
            'description': description,
            'url': url,
            'video_id': video_id if video_id else None
        }
    
    def create_campaign_flow(self):
        """キャンペーン作成フロー"""
        print("\n🚀 キャンペーン作成を開始します...")
        
        # 1. アカウント選択
        account = self.select_ad_account()
        if not account:
            return False
        
        # 2. キャンペーン情報入力
        campaign_info = self.get_campaign_input()
        if not campaign_info:
            return False
        
        # 3. 広告セット情報入力
        ad_set_info = self.get_ad_set_input()
        if not ad_set_info:
            return False
        
        # 4. クリエイティブ情報入力
        creative_info = self.get_creative_input()
        if not creative_info:
            return False
        
        # 5. 確認
        print("\n📋 入力内容を確認してください:")
        print("-" * 50)
        print(f"アカウント: {account['name']}")
        print(f"キャンペーン名: {campaign_info['name']}")
        print(f"目的: {campaign_info['objective']}")
        print(f"広告セット名: {ad_set_info['name']}")
        print(f"予算: {ad_set_info['budget']}円/日")
        print(f"期間: {ad_set_info['start_date']} ～ {ad_set_info['end_date']}")
        print(f"見出し: {creative_info['headline']}")
        print(f"説明文: {creative_info['description']}")
        print(f"URL: {creative_info['url']}")
        
        confirm = input("\nこの内容で作成しますか？ (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 作成をキャンセルしました。")
            return False
        
        # 6. 作成実行
        try:
            print("\n🔄 広告を作成中...")
            
            # キャンペーン作成
            campaign = self.client.create_campaign(
                account['id'],
                campaign_info['name'],
                campaign_info['objective']
            )
            print(f"✅ キャンペーン作成完了: {campaign['id']}")
            
            # 広告セット作成
            ad_set = self.client.create_ad_set(
                account['id'],
                campaign['id'],
                ad_set_info['name'],
                ad_set_info['budget'],
                ad_set_info['start_date'],
                ad_set_info['end_date']
            )
            print(f"✅ 広告セット作成完了: {ad_set['id']}")
            
            # クリエイティブ作成
            creative = self.client.create_ad_creative(
                account['id'],
                creative_info['name'],
                creative_info['headline'],
                creative_info['description'],
                creative_info['url'],
                creative_info['video_id']
            )
            print(f"✅ クリエイティブ作成完了: {creative['id']}")
            
            # 広告作成
            ad = self.client.create_ad(
                account['id'],
                ad_set['id'],
                creative['id'],
                f"{campaign_info['name']}_Ad"
            )
            print(f"✅ 広告作成完了: {ad['id']}")
            
            # ログ記録
            self.logger.log_campaign_creation({
                'account_id': account['id'],
                'campaign_id': campaign['id'],
                'ad_set_id': ad_set['id'],
                'creative_id': creative['id'],
                'ad_id': ad['id']
            }, True)
            
            print("\n🎉 広告作成が完了しました！")
            print(f"📊 キャンペーンID: {campaign['id']}")
            print(f"📊 広告ID: {ad['id']}")
            print("⚠️  広告は一時停止状態で作成されました。")
            print("   配信を開始するには、Meta広告マネージャーで手動で有効化してください。")
            
            return True
            
        except Exception as e:
            print(f"❌ 広告作成エラー: {e}")
            self.logger.log_campaign_creation({}, False, str(e))
            return False
    
    def show_recent_logs(self):
        """最近のログ表示"""
        print("\n📋 最近の操作ログ:")
        print("-" * 50)
        
        logs = self.logger.get_recent_logs(10)
        if not logs:
            print("ログが見つかりません。")
            return
        
        for log in logs:
            status = "✅" if log['success'] else "❌"
            timestamp = log['timestamp'][:19]  # 日時部分のみ
            action = log['action']
            print(f"{status} {timestamp} - {action}")
            if not log['success'] and log.get('error'):
                print(f"   エラー: {log['error']}")
    
    def run(self):
        """メイン実行ループ"""
        self.display_welcome()
        
        while True:
            print("\n📌 メニュー:")
            print("1. 広告キャンペーン作成")
            print("2. 最近のログ表示")
            print("3. 終了")
            
            choice = input("\n選択してください (1-3): ").strip()
            
            if choice == '1':
                self.create_campaign_flow()
            elif choice == '2':
                self.show_recent_logs()
            elif choice == '3':
                print("👋 システムを終了します。")
                break
            else:
                print("❌ 無効な選択です。")

def main():
    """メイン関数"""
    try:
        cli = MetaAdsCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n👋 システムを終了します。")
    except Exception as e:
        print(f"❌ システムエラー: {e}")

if __name__ == "__main__":
    main()

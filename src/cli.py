"""
CLI インターフェース
"""
import sys
from datetime import datetime, timedelta
from .meta_client import MetaAdsClient
from .logger import AdLogger
from .template_manager import TemplateManager

class MetaAdsCLI:
    """Meta広告自動出稿システム CLI"""
    
    def __init__(self):
        """初期化"""
        self.client = MetaAdsClient()
        self.logger = AdLogger()
        self.template_manager = TemplateManager()
    
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
        
        # 作成方法を選択
        print("\n📋 作成方法を選択してください:")
        print("1. テンプレートを使用（クイック出稿）")
        print("2. 手動で詳細設定")
        
        method_choice = input("選択 (1-2, デフォルト: 1): ").strip() or '1'
        
        if method_choice == '1':
            return self.quick_campaign_creation()
        else:
            return self.manual_campaign_creation()
    
    def quick_campaign_creation(self):
        """テンプレートベースのクイック出稿"""
        print("\n⚡ クイック出稿モード")
        
        # 1. テンプレート選択
        template_name = self.select_template()
        
        # 2. アカウント選択
        account = self.select_ad_account()
        if not account:
            return False
        
        # 3. 基本情報入力（最小限）
        print("\n📝 基本情報を入力してください:")
        print("-" * 40)
        
        campaign_name = input("キャンペーン名: ").strip()
        if not campaign_name:
            print("❌ キャンペーン名は必須です。")
            return False
        
        # 変数設定
        variables = {
            'campaign_name': campaign_name,
            'product_name': input("商品名 (オプション): ").strip() or "商品",
            'current_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # テンプレートを適用
        try:
            template_data = self.template_manager.apply_template(template_name, variables)
        except Exception as e:
            print(f"❌ テンプレート適用エラー: {e}")
            return False
        
        # 4. 設定確認とカスタマイズ
        print("\n📋 テンプレート設定:")
        print("-" * 50)
        print(f"テンプレート: {template_name}")
        print(f"キャンペーン名: {template_data['campaign']['name_template']}")
        print(f"目的: {template_data['campaign']['objective']}")
        print(f"予算: {template_data['ad_set']['budget']}円/日")
        print(f"期間: {template_data['ad_set']['start_time']} ～ {template_data['ad_set']['end_time']}")
        print(f"見出し: {template_data['creative']['headline_template']}")
        print(f"説明文: {template_data['creative']['description_template']}")
        print(f"URL: {template_data['creative']['url_template']}")
        
        # カスタマイズオプション
        print("\n🔧 設定をカスタマイズしますか？ (y/N): ", end="")
        if input().strip().lower() == 'y':
            template_data = self.customize_template_settings(template_data)
        
        # 5. 最終確認
        print("\n📋 最終確認:")
        print("-" * 50)
        print(f"アカウント: {account['name']}")
        print(f"キャンペーン名: {template_data['campaign']['name_template']}")
        print(f"目的: {template_data['campaign']['objective']}")
        print(f"予算: {template_data['ad_set']['budget']}円/日")
        print(f"期間: {template_data['ad_set']['start_time']} ～ {template_data['ad_set']['end_time']}")
        print(f"見出し: {template_data['creative']['headline_template']}")
        print(f"説明文: {template_data['creative']['description_template']}")
        print(f"URL: {template_data['creative']['url_template']}")
        
        confirm = input("\nこの内容で作成しますか？ (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 作成をキャンセルしました。")
            return False
        
        # 6. 作成実行
        return self.execute_campaign_creation(account, template_data)
    
    def customize_template_settings(self, template_data):
        """テンプレート設定のカスタマイズ"""
        print("\n🔧 カスタマイズ項目:")
        print("1. 予算を変更")
        print("2. 配信期間を変更")
        print("3. 見出しを変更")
        print("4. 説明文を変更")
        print("5. URLを変更")
        print("6. 完了")
        
        while True:
            choice = input("カスタマイズ項目を選択 (1-6): ").strip()
            
            if choice == '1':
                try:
                    budget = float(input(f"新しい予算 (現在: {template_data['ad_set']['budget']}円/日): "))
                    template_data['ad_set']['budget'] = budget
                    print(f"✅ 予算を {budget}円/日 に変更しました。")
                except ValueError:
                    print("❌ 無効な予算値です。")
            
            elif choice == '2':
                start_date = input(f"開始日 (現在: {template_data['ad_set']['start_time']}): ").strip()
                if start_date:
                    template_data['ad_set']['start_time'] = start_date
                
                end_date = input(f"終了日 (現在: {template_data['ad_set']['end_time']}): ").strip()
                if end_date:
                    template_data['ad_set']['end_time'] = end_date
                
                print("✅ 配信期間を変更しました。")
            
            elif choice == '3':
                headline = input(f"新しい見出し (現在: {template_data['creative']['headline_template']}): ").strip()
                if headline:
                    template_data['creative']['headline_template'] = headline
                    print("✅ 見出しを変更しました。")
            
            elif choice == '4':
                description = input(f"新しい説明文 (現在: {template_data['creative']['description_template']}): ").strip()
                if description:
                    template_data['creative']['description_template'] = description
                    print("✅ 説明文を変更しました。")
            
            elif choice == '5':
                url = input(f"新しいURL (現在: {template_data['creative']['url_template']}): ").strip()
                if url:
                    template_data['creative']['url_template'] = url
                    print("✅ URLを変更しました。")
            
            elif choice == '6':
                break
            
            else:
                print("❌ 無効な選択です。")
        
        return template_data
    
    def manual_campaign_creation(self):
        """手動での詳細設定によるキャンペーン作成"""
        print("\n🔧 手動設定モード")
        
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
        
        # 6. テンプレートデータ形式に変換
        template_data = {
            'campaign': {
                'name_template': campaign_info['name'],
                'objective': campaign_info['objective'],
                'status': 'PAUSED'
            },
            'ad_set': {
                'name_template': ad_set_info['name'],
                'budget': ad_set_info['budget'],
                'start_time': ad_set_info['start_date'],
                'end_time': ad_set_info['end_date'],
                'targeting': {
                    'geo_locations': {'countries': ['JP']},
                    'age_min': 18,
                    'age_max': 65
                }
            },
            'creative': {
                'name_template': creative_info['name'],
                'headline_template': creative_info['headline'],
                'description_template': creative_info['description'],
                'url_template': creative_info['url'],
                'video_id': creative_info['video_id']
            },
            'ad': {
                'name_template': f"{campaign_info['name']}_Ad",
                'status': 'PAUSED'
            }
        }
        
        # 7. 作成実行
        return self.execute_campaign_creation(account, template_data)
    
    def execute_campaign_creation(self, account, template_data):
        """キャンペーン作成の実行"""
        try:
            print("\n🔄 広告を作成中...")
            
            # キャンペーン作成
            campaign = self.client.create_campaign(
                account['id'],
                template_data['campaign']['name_template'],
                template_data['campaign']['objective']
            )
            print(f"✅ キャンペーン作成完了: {campaign['id']}")
            
            # 広告セット作成
            ad_set = self.client.create_ad_set(
                account['id'],
                campaign['id'],
                template_data['ad_set']['name_template'],
                template_data['ad_set']['budget'],
                template_data['ad_set']['start_time'],
                template_data['ad_set']['end_time']
            )
            print(f"✅ 広告セット作成完了: {ad_set['id']}")
            
            # クリエイティブ作成
            creative = self.client.create_ad_creative(
                account['id'],
                template_data['creative']['name_template'],
                template_data['creative']['headline_template'],
                template_data['creative']['description_template'],
                template_data['creative']['url_template'],
                template_data['creative'].get('video_id')
            )
            print(f"✅ クリエイティブ作成完了: {creative['id']}")
            
            # 広告作成
            ad = self.client.create_ad(
                account['id'],
                ad_set['id'],
                creative['id'],
                template_data['ad']['name_template']
            )
            print(f"✅ 広告作成完了: {ad['id']}")
            
            # ログ記録
            self.logger.log_campaign_creation({
                'account_id': account['id'],
                'campaign_id': campaign['id'],
                'ad_set_id': ad_set['id'],
                'creative_id': creative['id'],
                'ad_id': ad['id'],
                'template_used': template_data.get('template_name', 'Manual')
            }, True)
            
            print("\n🎉 広告作成が完了しました！")
            print(f"📊 キャンペーンID: {campaign['id']}")
            print(f"📊 広告ID: {ad['id']}")
            print("⚠️  広告は一時停止状態で作成されました。")
            print("   配信を開始するには、Meta広告マネージャーで手動で有効化してください。")
            
            # テンプレート保存オプション
            print("\n💾 この設定をテンプレートとして保存しますか？ (y/N): ", end="")
            if input().strip().lower() == 'y':
                template_name = input("テンプレート名: ").strip()
                if template_name:
                    template_data['template_name'] = template_name
                    template_data['description'] = f"キャンペーン '{campaign['id']}' から作成"
                    if self.template_manager.save_template(template_data):
                        print(f"✅ テンプレート '{template_name}' を保存しました。")
            
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
    
    def manage_templates(self):
        """テンプレート管理"""
        while True:
            print("\n📋 テンプレート管理:")
            print("1. テンプレート一覧表示")
            print("2. テンプレート作成")
            print("3. テンプレート編集")
            print("4. テンプレート削除")
            print("5. 戻る")
            
            choice = input("\n選択してください (1-5): ").strip()
            
            if choice == '1':
                self.list_templates()
            elif choice == '2':
                self.create_template()
            elif choice == '3':
                self.edit_template()
            elif choice == '4':
                self.delete_template()
            elif choice == '5':
                break
            else:
                print("❌ 無効な選択です。")
    
    def list_templates(self):
        """テンプレート一覧表示"""
        print("\n📋 利用可能なテンプレート:")
        print("-" * 60)
        
        templates = self.template_manager.list_templates()
        if not templates:
            print("テンプレートが見つかりません。")
            return
        
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template['name']}")
            print(f"   説明: {template['description']}")
            print(f"   更新日: {template['updated_at'][:10]}")
            print()
    
    def create_template(self):
        """テンプレート作成"""
        print("\n📝 新しいテンプレートを作成します:")
        print("-" * 40)
        
        template_name = input("テンプレート名: ").strip()
        if not template_name:
            print("❌ テンプレート名は必須です。")
            return
        
        description = input("説明 (オプション): ").strip()
        
        # デフォルトテンプレートをベースに作成
        template = self.template_manager.create_default_template()
        template['template_name'] = template_name
        template['description'] = description
        
        # 基本設定をカスタマイズ
        print("\n🔧 基本設定をカスタマイズしますか？ (y/N): ", end="")
        if input().strip().lower() == 'y':
            template = self.customize_template(template)
        
        if self.template_manager.save_template(template):
            print(f"✅ テンプレート '{template_name}' を作成しました。")
        else:
            print("❌ テンプレートの作成に失敗しました。")
    
    def customize_template(self, template):
        """テンプレートのカスタマイズ"""
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
        template['campaign']['objective'] = objectives.get(objective_choice, 'LINK_CLICKS')
        
        # 予算設定
        try:
            budget = input("デフォルト予算 (円/日, デフォルト: 1000): ").strip()
            if budget:
                template['ad_set']['budget'] = float(budget)
        except ValueError:
            print("❌ 無効な予算値です。デフォルト値を使用します。")
        
        # ターゲティング設定
        print("\n🎯 ターゲティング設定をカスタマイズしますか？ (y/N): ", end="")
        if input().strip().lower() == 'y':
            self.customize_targeting(template['ad_set']['targeting'])
        
        # クリエイティブ設定
        print("\n🎨 クリエイティブ設定をカスタマイズしますか？ (y/N): ", end="")
        if input().strip().lower() == 'y':
            self.customize_creative(template['creative'])
        
        return template
    
    def customize_targeting(self, targeting):
        """ターゲティング設定のカスタマイズ"""
        # 年齢設定
        try:
            age_min = input("最小年齢 (デフォルト: 18): ").strip()
            if age_min:
                targeting['age_min'] = int(age_min)
            
            age_max = input("最大年齢 (デフォルト: 65): ").strip()
            if age_max:
                targeting['age_max'] = int(age_max)
        except ValueError:
            print("❌ 無効な年齢値です。デフォルト値を使用します。")
        
        # 性別設定
        print("性別設定:")
        print("1. 男性のみ")
        print("2. 女性のみ")
        print("3. 両方 (デフォルト)")
        
        gender_choice = input("選択 (1-3, デフォルト: 3): ").strip() or '3'
        if gender_choice == '1':
            targeting['genders'] = [1]
        elif gender_choice == '2':
            targeting['genders'] = [2]
        else:
            targeting['genders'] = [1, 2]
    
    def customize_creative(self, creative):
        """クリエイティブ設定のカスタマイズ"""
        headline = input("デフォルト見出しテンプレート: ").strip()
        if headline:
            creative['headline_template'] = headline
        
        description = input("デフォルト説明文テンプレート: ").strip()
        if description:
            creative['description_template'] = description
        
        url = input("デフォルトURLテンプレート: ").strip()
        if url:
            creative['url_template'] = url
    
    def edit_template(self):
        """テンプレート編集"""
        templates = self.template_manager.list_templates()
        if not templates:
            print("編集可能なテンプレートがありません。")
            return
        
        print("\n📝 編集するテンプレートを選択してください:")
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template['name']}")
        
        try:
            choice = int(input(f"選択 (1-{len(templates)}): "))
            if 1 <= choice <= len(templates):
                template_name = templates[choice - 1]['name']
                template = self.template_manager.load_template(template_name)
                
                if template:
                    print(f"\n📝 テンプレート '{template_name}' を編集します:")
                    edited_template = self.customize_template(template)
                    
                    if self.template_manager.save_template(edited_template):
                        print(f"✅ テンプレート '{template_name}' を更新しました。")
                    else:
                        print("❌ テンプレートの更新に失敗しました。")
            else:
                print("❌ 無効な選択です。")
        except ValueError:
            print("❌ 数値を入力してください。")
    
    def delete_template(self):
        """テンプレート削除"""
        templates = self.template_manager.list_templates()
        if not templates:
            print("削除可能なテンプレートがありません。")
            return
        
        print("\n🗑️ 削除するテンプレートを選択してください:")
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template['name']}")
        
        try:
            choice = int(input(f"選択 (1-{len(templates)}): "))
            if 1 <= choice <= len(templates):
                template_name = templates[choice - 1]['name']
                
                confirm = input(f"テンプレート '{template_name}' を削除しますか？ (y/N): ").strip().lower()
                if confirm == 'y':
                    if self.template_manager.delete_template(template_name):
                        print(f"✅ テンプレート '{template_name}' を削除しました。")
                    else:
                        print("❌ テンプレートの削除に失敗しました。")
            else:
                print("❌ 無効な選択です。")
        except ValueError:
            print("❌ 数値を入力してください。")
    
    def select_template(self):
        """テンプレート選択"""
        templates = self.template_manager.list_templates()
        if not templates:
            print("利用可能なテンプレートがありません。デフォルトテンプレートを使用します。")
            return "デフォルトテンプレート"
        
        print("\n📋 使用するテンプレートを選択してください:")
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template['name']}")
            print(f"   説明: {template['description']}")
        
        try:
            choice = int(input(f"選択 (1-{len(templates)}): "))
            if 1 <= choice <= len(templates):
                return templates[choice - 1]['name']
            else:
                print("❌ 無効な選択です。デフォルトテンプレートを使用します。")
                return "デフォルトテンプレート"
        except ValueError:
            print("❌ 数値を入力してください。デフォルトテンプレートを使用します。")
            return "デフォルトテンプレート"
    
    def run(self):
        """メイン実行ループ"""
        self.display_welcome()
        
        while True:
            print("\n📌 メニュー:")
            print("1. 広告キャンペーン作成")
            print("2. テンプレート管理")
            print("3. 最近のログ表示")
            print("4. 終了")
            
            choice = input("\n選択してください (1-4): ").strip()
            
            if choice == '1':
                self.create_campaign_flow()
            elif choice == '2':
                self.manage_templates()
            elif choice == '3':
                self.show_recent_logs()
            elif choice == '4':
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

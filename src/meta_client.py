"""
Meta Business API クライアント
"""
import logging
from facebook_business import FacebookAdsApi
from facebook_business.adobjects.business import Business
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad
from facebook_business.exceptions import FacebookRequestError

from .config import Config

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetaAdsClient:
    """Meta広告APIクライアント"""
    
    def __init__(self):
        """初期化"""
        Config.validate_config()
        
        # Facebook Ads API初期化
        FacebookAdsApi.init(
            app_id=Config.APP_ID,
            app_secret=Config.APP_SECRET,
            access_token=Config.META_ACCESS_TOKEN
        )
        
        self.business = Business(Config.BUSINESS_MANAGER_ID)
        logger.info("Meta Ads API クライアントが初期化されました")
    
    def get_ad_accounts(self):
        """Business Manager配下の広告アカウント一覧を取得（ページネーション対応）"""
        try:
            # 正しいAPIエンドポイントを使用
            import requests
            
            # ユーザーの広告アカウントを取得する正しいエンドポイント
            url = "https://graph.facebook.com/v19.0/me/adaccounts"
            params = {
                'access_token': Config.META_ACCESS_TOKEN,
                'fields': 'id,name,account_status',
                'limit': 25  # 1ページあたりの最大数
            }
            
            account_list = []
            next_url = None
            page_count = 0
            
            while True:
                page_count += 1
                logger.info(f"ページ {page_count} を取得中...")
                
                if next_url:
                    response = requests.get(next_url)
                else:
                    response = requests.get(url, params=params)
                
                response.raise_for_status()
                data = response.json()
                
                # アカウント情報を追加
                for account in data.get('data', []):
                    account_info = {
                        'id': account['id'],
                        'name': account.get('name', 'Unknown'),
                        'status': account.get('account_status', 'Unknown')
                    }
                    account_list.append(account_info)
                
                # 次のページがあるかチェック
                paging = data.get('paging', {})
                next_url = paging.get('next')
                
                if not next_url:
                    logger.info("すべてのページを取得完了")
                    break
            
            logger.info(f"{len(account_list)}個の広告アカウントを取得しました")
            return account_list
            
        except Exception as e:
            logger.error(f"広告アカウント取得エラー: {e}")
            # フォールバック: 手動でアカウントIDを指定
            logger.warning("手動でアカウントIDを設定してください")
            return []
    
    def get_conversion_datasets(self, account_id):
        """コンバージョンデータセット一覧を取得"""
        try:
            import requests
            
            # 複数のエンドポイントを試行
            endpoints = [
                f"https://graph.facebook.com/v19.0/{account_id}/conversion_sources",
                f"https://graph.facebook.com/v19.0/{account_id}/conversion_datasets",
                f"https://graph.facebook.com/v19.0/{account_id}/pixels"
            ]
            
            for url in endpoints:
                try:
                    params = {
                        'access_token': Config.META_ACCESS_TOKEN,
                        'fields': 'id,name,description'
                    }
                    
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    datasets = []
                    for dataset in data.get('data', []):
                        dataset_info = {
                            'id': dataset['id'],
                            'name': dataset.get('name', 'Unknown'),
                            'description': dataset.get('description', '')
                        }
                        datasets.append(dataset_info)
                    
                    if datasets:
                        logger.info(f"{len(datasets)}個のデータセットを取得しました")
                        return datasets
                        
                except Exception as e:
                    logger.warning(f"エンドポイント {url} でエラー: {e}")
                    continue
            
            # すべてのエンドポイントが失敗した場合
            logger.warning("すべてのデータセット取得エンドポイントが失敗しました")
            return []
            
        except Exception as e:
            logger.error(f"データセット取得エラー: {e}")
            return []
    
    def get_facebook_pages(self):
        """Facebookページ一覧を取得"""
        try:
            import requests
            
            # 複数のエンドポイントを試行
            endpoints = [
                "https://graph.facebook.com/v19.0/me/accounts",
                "https://graph.facebook.com/v19.0/me/pages",
                f"https://graph.facebook.com/v19.0/{Config.BUSINESS_MANAGER_ID}/owned_pages"
            ]
            
            for url in endpoints:
                try:
                    params = {
                        'access_token': Config.META_ACCESS_TOKEN,
                        'fields': 'id,name,category'
                    }
                    
                    # 特定のエンドポイント用のパラメータ
                    if 'me/accounts' in url:
                        params['type'] = 'page'
                    elif 'owned_pages' in url:
                        params['access_token'] = Config.META_ACCESS_TOKEN
                    
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    pages = []
                    for page in data.get('data', []):
                        page_info = {
                            'id': page['id'],
                            'name': page.get('name', 'Unknown'),
                            'category': page.get('category', '')
                        }
                        pages.append(page_info)
                    
                    if pages:
                        logger.info(f"{len(pages)}個のFacebookページを取得しました")
                        return pages
                        
                except Exception as e:
                    logger.warning(f"エンドポイント {url} でエラー: {e}")
                    continue
            
            # すべてのエンドポイントが失敗した場合
            logger.warning("すべてのFacebookページ取得エンドポイントが失敗しました")
            return []
            
        except Exception as e:
            logger.error(f"Facebookページ取得エラー: {e}")
            return []
    
    def create_campaign(self, account_id, campaign_name, budget_amount, budget_type='daily'):
        """キャンペーンを作成（売上目的固定）"""
        try:
            account = AdAccount(account_id)
            
            # 固定設定
            campaign_data = {
                Campaign.Field.name: campaign_name,
                Campaign.Field.objective: 'OUTCOME_SALES',  # 売上固定
                Campaign.Field.status: Config.DEFAULT_AD_STATUS,
                Campaign.Field.special_ad_categories: [],  # 特別な広告カテゴリなし
                Campaign.Field.buying_type: 'AUCTION',  # オークション固定
                Campaign.Field.bid_strategy: 'LOWEST_COST_WITHOUT_CAP'  # 最大数量または最高金額固定
            }
            
            # 予算設定
            if budget_type == 'daily':
                campaign_data[Campaign.Field.daily_budget] = budget_amount * 100  # セント単位
            else:
                campaign_data[Campaign.Field.lifetime_budget] = budget_amount * 100  # セント単位
            
            campaign = account.create_campaign(params=campaign_data)
            logger.info(f"キャンペーン作成成功: {campaign['id']} - {campaign_name} (予算: {budget_amount}円)")
            
            return {
                'id': campaign['id'],
                'name': campaign_name,
                'objective': 'OUTCOME_SALES',
                'status': Config.DEFAULT_AD_STATUS,
                'budget': budget_amount,
                'budget_type': budget_type
            }
            
        except FacebookRequestError as e:
            logger.error(f"キャンペーン作成エラー: {e}")
            raise
    
    def create_ad_set(self, account_id, campaign_id, ad_set_name, budget, start_time, end_time=None, dataset_id=None):
        """広告セットを作成（固定設定多数）"""
        try:
            account = AdAccount(account_id)
            
            # 固定設定（キャンペーンで予算を設定しているため、広告セットでは予算を設定しない）
            ad_set_data = {
                AdSet.Field.name: ad_set_name,
                AdSet.Field.campaign_id: campaign_id,
                # AdSet.Field.daily_budget: budget * 100,  # キャンペーンで予算を設定しているため削除
                AdSet.Field.start_time: start_time,
                AdSet.Field.status: Config.DEFAULT_AD_STATUS,
                AdSet.Field.billing_event: 'IMPRESSIONS',  # 固定
                AdSet.Field.optimization_goal: 'OFFSITE_CONVERSIONS',  # オフサイトコンバージョン固定
                AdSet.Field.attribution_spec: [{'event_type': 'CLICK_THROUGH', 'window_days': 7}],  # クリックスルー固定
                AdSet.Field.targeting: {
                    'geo_locations': {
                        'countries': ['JP']  # 日本固定
                    }
                },
                # AdSet.Field.placement: ['facebook', 'instagram', 'messenger', 'audience_network'],  # Advantage+配置オン固定（フィールドが存在しないためコメントアウト）
                # AdSet.Field.dynamic_creative: False,  # ダイナミッククリエイティブオフ固定（フィールドが存在しないためコメントアウト）
                AdSet.Field.bid_strategy: 'LOWEST_COST_WITHOUT_CAP'  # 最大数量または最高金額固定
            }
            
            # 終了日時が設定されている場合のみ追加
            if end_time:
                ad_set_data[AdSet.Field.end_time] = end_time
            
            # データセットが指定されている場合のみ追加
            if dataset_id:
                # conversion_specsフィールドが存在しないためコメントアウト
                # ad_set_data[AdSet.Field.conversion_specs] = [{
                #     'conversion_type': 'WEBSITE',
                #     'conversion_dataset_id': dataset_id
                # }]
                pass
            else:
                # デフォルトのウェブサイトコンバージョン
                # conversion_specsフィールドが存在しないためコメントアウト
                # ad_set_data[AdSet.Field.conversion_specs] = [{
                #     'conversion_type': 'WEBSITE'
                # }]
                pass
            
            ad_set = account.create_ad_set(params=ad_set_data)
            logger.info(f"広告セット作成成功: {ad_set['id']} - {ad_set_name}")
            
            return {
                'id': ad_set['id'],
                'name': ad_set_name,
                'campaign_id': campaign_id,
                'budget': budget
            }
            
        except FacebookRequestError as e:
            logger.error(f"広告セット作成エラー: {e}")
            raise
    
    def create_ad_creative(self, account_id, ad_creative_name, headline, description, url, video_id=None, page_id=None):
        """広告クリエイティブを作成（固定設定多数）"""
        try:
            account = AdAccount(account_id)
            
            # 固定設定
            creative_data = {
                AdCreative.Field.name: ad_creative_name,
                AdCreative.Field.title: headline,
                AdCreative.Field.body: description,
                AdCreative.Field.object_url: url,
                AdCreative.Field.call_to_action_type: 'LEARN_MORE',  # コールトゥアクション固定（詳しくはこちら）
                AdCreative.Field.link_type: 'WEBSITE',  # ウェブサイト固定
                AdCreative.Field.display_url: url,  # ディスプレイリンク（ウェブサイトのURLと同じ）
                AdCreative.Field.multi_share_optimized: True,  # 複数広告主の広告オン固定
                AdCreative.Field.creative_type: 'VIDEO' if video_id else 'IMAGE',  # 動画または画像固定
                AdCreative.Field.source_type: 'MANUAL_UPLOAD'  # 手動アップロード固定
            }
            
            # Facebookページが指定されている場合
            if page_id:
                creative_data[AdCreative.Field.page_id] = page_id
            
            # 動画がある場合は追加
            if video_id:
                creative_data[AdCreative.Field.object_story_spec] = {
                    'page_id': page_id or account_id,
                    'video_data': {
                        'video_id': video_id,
                        'title': headline,
                        'description': description,
                        'call_to_action': {
                            'type': 'LEARN_MORE',
                            'value': {
                                'link': url
                            }
                        }
                    }
                }
            
            creative = account.create_ad_creative(params=creative_data)
            logger.info(f"広告クリエイティブ作成成功: {creative['id']} - {ad_creative_name}")
            
            return {
                'id': creative['id'],
                'name': ad_creative_name,
                'headline': headline,
                'description': description,
                'url': url
            }
            
        except FacebookRequestError as e:
            logger.error(f"広告クリエイティブ作成エラー: {e}")
            raise
    
    def create_ad(self, account_id, ad_set_id, creative_id, ad_name):
        """広告を作成"""
        try:
            account = AdAccount(account_id)
            
            ad_data = {
                Ad.Field.name: ad_name,
                Ad.Field.adset_id: ad_set_id,
                Ad.Field.creative: {'creative_id': creative_id},
                Ad.Field.status: Config.DEFAULT_AD_STATUS
            }
            
            ad = account.create_ad(params=ad_data)
            logger.info(f"広告作成成功: {ad['id']} - {ad_name}")
            
            return {
                'id': ad['id'],
                'name': ad_name,
                'ad_set_id': ad_set_id,
                'creative_id': creative_id,
                'status': Config.DEFAULT_AD_STATUS
            }
            
        except FacebookRequestError as e:
            logger.error(f"広告作成エラー: {e}")
            raise

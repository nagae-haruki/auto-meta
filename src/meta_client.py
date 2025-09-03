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
        """Business Manager配下の広告アカウント一覧を取得"""
        try:
            accounts = self.business.get_ad_accounts(fields=['id', 'name', 'account_status'])
            account_list = []
            
            for account in accounts:
                account_info = {
                    'id': account['id'],
                    'name': account.get('name', 'Unknown'),
                    'status': account.get('account_status', 'Unknown')
                }
                account_list.append(account_info)
            
            logger.info(f"{len(account_list)}個の広告アカウントを取得しました")
            return account_list
            
        except FacebookRequestError as e:
            logger.error(f"広告アカウント取得エラー: {e}")
            raise
    
    def create_campaign(self, account_id, campaign_name, objective='LINK_CLICKS'):
        """キャンペーンを作成"""
        try:
            account = AdAccount(account_id)
            
            campaign_data = {
                Campaign.Field.name: campaign_name,
                Campaign.Field.objective: objective,
                Campaign.Field.status: Config.DEFAULT_AD_STATUS
            }
            
            campaign = account.create_campaign(params=campaign_data)
            logger.info(f"キャンペーン作成成功: {campaign['id']} - {campaign_name}")
            
            return {
                'id': campaign['id'],
                'name': campaign_name,
                'objective': objective,
                'status': Config.DEFAULT_AD_STATUS
            }
            
        except FacebookRequestError as e:
            logger.error(f"キャンペーン作成エラー: {e}")
            raise
    
    def create_ad_set(self, account_id, campaign_id, ad_set_name, budget, start_time, end_time):
        """広告セットを作成"""
        try:
            account = AdAccount(account_id)
            
            ad_set_data = {
                AdSet.Field.name: ad_set_name,
                AdSet.Field.campaign_id: campaign_id,
                AdSet.Field.daily_budget: budget * 100,  # セント単位
                AdSet.Field.start_time: start_time,
                AdSet.Field.end_time: end_time,
                AdSet.Field.status: Config.DEFAULT_AD_STATUS,
                AdSet.Field.targeting: {
                    'geo_locations': {
                        'countries': ['JP']  # デフォルトで日本
                    }
                }
            }
            
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
    
    def create_ad_creative(self, account_id, ad_creative_name, headline, description, url, video_id=None):
        """広告クリエイティブを作成"""
        try:
            account = AdAccount(account_id)
            
            creative_data = {
                AdCreative.Field.name: ad_creative_name,
                AdCreative.Field.title: headline,
                AdCreative.Field.body: description,
                AdCreative.Field.object_url: url,
                AdCreative.Field.call_to_action_type: 'LEARN_MORE'
            }
            
            # 動画がある場合は追加
            if video_id:
                creative_data[AdCreative.Field.object_story_spec] = {
                    'page_id': account.get_ad_accounts()[0]['id'],  # ページIDが必要
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

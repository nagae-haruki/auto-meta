"""
Meta広告自動出稿システム - 設定管理
"""
import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

class Config:
    """アプリケーション設定クラス"""
    
    # Meta Business API設定
    META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
    BUSINESS_MANAGER_ID = os.getenv('BUSINESS_MANAGER_ID')
    APP_ID = os.getenv('APP_ID')
    APP_SECRET = os.getenv('APP_SECRET')
    
    # アプリケーション設定
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/meta_ads.log')
    
    # デフォルト広告設定
    DEFAULT_CAMPAIGN_OBJECTIVE = 'LINK_CLICKS'
    DEFAULT_AD_STATUS = 'PAUSED'  # 安全のため最初は停止状態
    
    @classmethod
    def validate_config(cls):
        """設定値の検証"""
        required_vars = [
            'META_ACCESS_TOKEN',
            'BUSINESS_MANAGER_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"以下の環境変数が設定されていません: {', '.join(missing_vars)}")
        
        return True

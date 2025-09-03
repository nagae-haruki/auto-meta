"""
ログ管理機能
"""
import logging
import os
from datetime import datetime
import json

class AdLogger:
    """広告出稿ログ管理クラス"""
    
    def __init__(self, log_file='logs/ad_campaigns.log'):
        """初期化"""
        self.log_file = log_file
        self.ensure_log_directory()
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def ensure_log_directory(self):
        """ログディレクトリの存在確認と作成"""
        log_dir = os.path.dirname(self.log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def log_campaign_creation(self, campaign_data, success=True, error_message=None):
        """キャンペーン作成ログ"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'campaign_creation',
            'success': success,
            'data': campaign_data,
            'error': error_message
        }
        
        if success:
            self.logger.info(f"キャンペーン作成成功: {campaign_data}")
        else:
            self.logger.error(f"キャンペーン作成失敗: {error_message}")
        
        self._write_to_file(log_entry)
    
    def log_ad_creation(self, ad_data, success=True, error_message=None):
        """広告作成ログ"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'ad_creation',
            'success': success,
            'data': ad_data,
            'error': error_message
        }
        
        if success:
            self.logger.info(f"広告作成成功: {ad_data}")
        else:
            self.logger.error(f"広告作成失敗: {error_message}")
        
        self._write_to_file(log_entry)
    
    def log_account_access(self, account_data, success=True, error_message=None):
        """アカウントアクセスログ"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'account_access',
            'success': success,
            'data': account_data,
            'error': error_message
        }
        
        if success:
            self.logger.info(f"アカウントアクセス成功: {account_data}")
        else:
            self.logger.error(f"アカウントアクセス失敗: {error_message}")
        
        self._write_to_file(log_entry)
    
    def _write_to_file(self, log_entry):
        """ログファイルに書き込み"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"ログファイル書き込みエラー: {e}")
    
    def get_recent_logs(self, limit=10):
        """最近のログを取得"""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-limit:] if len(lines) > limit else lines
                return [json.loads(line.strip()) for line in recent_lines if line.strip()]
        except FileNotFoundError:
            return []
        except Exception as e:
            self.logger.error(f"ログ読み込みエラー: {e}")
            return []

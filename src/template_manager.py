"""
テンプレート管理システム
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class TemplateManager:
    """広告テンプレート管理クラス"""
    
    def __init__(self, template_dir='data/templates'):
        """初期化"""
        self.template_dir = template_dir
        self.ensure_template_directory()
        self.template_file = os.path.join(template_dir, 'ad_templates.json')
    
    def ensure_template_directory(self):
        """テンプレートディレクトリの存在確認と作成"""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
    
    def create_default_template(self) -> Dict[str, Any]:
        """デフォルトテンプレートを作成"""
        return {
            "template_name": "デフォルトテンプレート",
            "description": "基本的な広告テンプレート",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "campaign": {
                "name_template": "{campaign_name}",
                "objective": "LINK_CLICKS",
                "status": "PAUSED"
            },
            "ad_set": {
                "name_template": "{campaign_name}_AdSet",
                "budget": 1000,  # デフォルト予算（円）
                "budget_type": "daily",  # daily or lifetime
                "start_time": "today",
                "end_time": "7_days_later",
                "targeting": {
                    "geo_locations": {
                        "countries": ["JP"]
                    },
                    "age_min": 18,
                    "age_max": 65,
                    "genders": [1, 2],  # 1: male, 2: female
                    "interests": []
                },
                "optimization_goal": "LINK_CLICKS",
                "billing_event": "IMPRESSIONS"
            },
            "creative": {
                "name_template": "{campaign_name}_Creative",
                "headline_template": "【{product_name}】今だけ特別価格！",
                "description_template": "お得な情報をお見逃しなく！詳細はこちらから。",
                "url_template": "https://example.com/{campaign_name}",
                "call_to_action": "LEARN_MORE",
                "video_id": None,
                "image_url": None
            },
            "ad": {
                "name_template": "{campaign_name}_Ad",
                "status": "PAUSED"
            },
            "auto_settings": {
                "auto_optimize": True,
                "auto_bid": True,
                "auto_schedule": True,
                "auto_audience": True
            }
        }
    
    def save_template(self, template: Dict[str, Any]) -> bool:
        """テンプレートを保存"""
        try:
            # 既存のテンプレートを読み込み
            templates = self.load_all_templates()
            
            # テンプレート名で既存のものを更新または新規追加
            template_name = template['template_name']
            template['updated_at'] = datetime.now().isoformat()
            
            if template_name not in templates:
                template['created_at'] = datetime.now().isoformat()
            
            templates[template_name] = template
            
            # ファイルに保存
            with open(self.template_file, 'w', encoding='utf-8') as f:
                json.dump(templates, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ テンプレート保存エラー: {e}")
            return False
    
    def load_all_templates(self) -> Dict[str, Any]:
        """すべてのテンプレートを読み込み"""
        try:
            if os.path.exists(self.template_file):
                with open(self.template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 初回実行時はデフォルトテンプレートを作成
                default_template = self.create_default_template()
                self.save_template(default_template)
                return {default_template['template_name']: default_template}
                
        except Exception as e:
            print(f"❌ テンプレート読み込みエラー: {e}")
            return {}
    
    def load_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """指定されたテンプレートを読み込み"""
        templates = self.load_all_templates()
        return templates.get(template_name)
    
    def delete_template(self, template_name: str) -> bool:
        """テンプレートを削除"""
        try:
            templates = self.load_all_templates()
            if template_name in templates:
                del templates[template_name]
                
                with open(self.template_file, 'w', encoding='utf-8') as f:
                    json.dump(templates, f, ensure_ascii=False, indent=2)
                
                return True
            return False
            
        except Exception as e:
            print(f"❌ テンプレート削除エラー: {e}")
            return False
    
    def list_templates(self) -> List[Dict[str, str]]:
        """テンプレート一覧を取得"""
        templates = self.load_all_templates()
        template_list = []
        
        for name, template in templates.items():
            template_list.append({
                'name': name,
                'description': template.get('description', ''),
                'created_at': template.get('created_at', ''),
                'updated_at': template.get('updated_at', '')
            })
        
        return template_list
    
    def apply_template(self, template_name: str, variables: Dict[str, str] = None) -> Dict[str, Any]:
        """テンプレートを適用して変数を置換"""
        template = self.load_template(template_name)
        if not template:
            raise ValueError(f"テンプレート '{template_name}' が見つかりません")
        
        if variables is None:
            variables = {}
        
        # デフォルト変数を設定
        default_variables = {
            'campaign_name': 'Test Campaign',
            'product_name': '商品名',
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            'current_time': datetime.now().strftime('%H:%M:%S')
        }
        default_variables.update(variables)
        
        # テンプレートをコピーして変数を置換
        applied_template = json.loads(json.dumps(template))  # ディープコピー
        
        # 文字列テンプレートの置換
        self._replace_variables(applied_template, default_variables)
        
        # 日時の自動設定
        self._apply_auto_settings(applied_template)
        
        return applied_template
    
    def _replace_variables(self, obj: Any, variables: Dict[str, str]):
        """オブジェクト内の変数を置換"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and '{' in value:
                    try:
                        obj[key] = value.format(**variables)
                    except KeyError:
                        # 変数が見つからない場合はそのまま
                        pass
                else:
                    self._replace_variables(value, variables)
        elif isinstance(obj, list):
            for item in obj:
                self._replace_variables(item, variables)
    
    def _apply_auto_settings(self, template: Dict[str, Any]):
        """自動設定を適用"""
        ad_set = template.get('ad_set', {})
        
        # 開始日の自動設定
        if ad_set.get('start_time') == 'today':
            ad_set['start_time'] = datetime.now().strftime('%Y-%m-%d')
        elif ad_set.get('start_time') == 'tomorrow':
            ad_set['start_time'] = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # 終了日の自動設定
        if ad_set.get('end_time') == '7_days_later':
            ad_set['end_time'] = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        elif ad_set.get('end_time') == '30_days_later':
            ad_set['end_time'] = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        # 自動最適化設定
        auto_settings = template.get('auto_settings', {})
        if auto_settings.get('auto_optimize'):
            ad_set['optimization_goal'] = ad_set.get('optimization_goal', 'LINK_CLICKS')
        
        if auto_settings.get('auto_bid'):
            ad_set['bidding_strategy'] = 'LOWEST_COST_WITHOUT_CAP'
        
        if auto_settings.get('auto_audience'):
            # デフォルトオーディエンス設定
            if not ad_set['targeting'].get('interests'):
                ad_set['targeting']['interests'] = [
                    {'name': 'Marketing', 'id': '6003107902433'},
                    {'name': 'Advertising', 'id': '6003348634581'}
                ]
    
    def create_template_from_campaign(self, campaign_data: Dict[str, Any], template_name: str) -> bool:
        """既存のキャンペーンデータからテンプレートを作成"""
        try:
            template = {
                "template_name": template_name,
                "description": f"キャンペーン '{campaign_data.get('campaign_name', '')}' から作成",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "campaign": {
                    "name_template": "{campaign_name}",
                    "objective": campaign_data.get('objective', 'LINK_CLICKS'),
                    "status": "PAUSED"
                },
                "ad_set": {
                    "name_template": "{campaign_name}_AdSet",
                    "budget": campaign_data.get('budget', 1000),
                    "budget_type": "daily",
                    "start_time": "today",
                    "end_time": "7_days_later",
                    "targeting": campaign_data.get('targeting', {
                        "geo_locations": {"countries": ["JP"]},
                        "age_min": 18,
                        "age_max": 65
                    }),
                    "optimization_goal": "LINK_CLICKS",
                    "billing_event": "IMPRESSIONS"
                },
                "creative": {
                    "name_template": "{campaign_name}_Creative",
                    "headline_template": campaign_data.get('headline', "【{product_name}】今だけ特別価格！"),
                    "description_template": campaign_data.get('description', "お得な情報をお見逃しなく！詳細はこちらから。"),
                    "url_template": campaign_data.get('url', "https://example.com/{campaign_name}"),
                    "call_to_action": "LEARN_MORE",
                    "video_id": campaign_data.get('video_id'),
                    "image_url": campaign_data.get('image_url')
                },
                "ad": {
                    "name_template": "{campaign_name}_Ad",
                    "status": "PAUSED"
                },
                "auto_settings": {
                    "auto_optimize": True,
                    "auto_bid": True,
                    "auto_schedule": True,
                    "auto_audience": True
                }
            }
            
            return self.save_template(template)
            
        except Exception as e:
            print(f"❌ テンプレート作成エラー: {e}")
            return False

"""
Google Drive動画管理システム
"""
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from typing import Dict, List, Optional, Any
import re

class GoogleDriveManager:
    """Google Drive動画管理クラス"""
    
    def __init__(self, credentials_file=None):
        """初期化"""
        self.credentials_file = credentials_file or os.getenv('GOOGLE_CREDENTIALS_FILE')
        self.service = None
        self.initialize_service()
    
    def initialize_service(self):
        """Google Drive API サービスを初期化"""
        try:
            if not self.credentials_file or not os.path.exists(self.credentials_file):
                print("⚠️ Google認証ファイルが見つかりません。")
                print("   GOOGLE_CREDENTIALS_FILE 環境変数を設定してください。")
                return False
            
            # スコープを設定
            scope = ['https://www.googleapis.com/auth/drive.readonly']
            
            # 認証情報を読み込み
            creds = Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=scope
            )
            
            # サービスを初期化
            self.service = build('drive', 'v3', credentials=creds)
            print("✅ Google Drive サービスが初期化されました")
            return True
            
        except Exception as e:
            print(f"❌ Google Drive 初期化エラー: {e}")
            return False
    
    def search_videos(self, query: str = "", folder_id: str = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """動画ファイルを検索"""
        try:
            if not self.service:
                print("❌ Google Drive サービスが初期化されていません")
                return []
            
            # 検索クエリを構築
            search_query = "mimeType contains 'video/'"
            
            if query:
                # ファイル名での検索を追加
                search_query += f" and name contains '{query}'"
            
            if folder_id:
                # 特定のフォルダ内で検索
                search_query += f" and '{folder_id}' in parents"
            
            # 検索実行
            results = self.service.files().list(
                q=search_query,
                pageSize=max_results,
                fields="nextPageToken, files(id, name, size, createdTime, modifiedTime, webViewLink, webContentLink, parents)"
            ).execute()
            
            items = results.get('files', [])
            
            # 動画情報を整理
            videos = []
            for item in items:
                video_info = {
                    'id': item['id'],
                    'name': item['name'],
                    'size': self._format_file_size(int(item.get('size', 0))),
                    'created_time': item.get('createdTime', ''),
                    'modified_time': item.get('modifiedTime', ''),
                    'web_view_link': item.get('webViewLink', ''),
                    'web_content_link': item.get('webContentLink', ''),
                    'parents': item.get('parents', [])
                }
                videos.append(video_info)
            
            print(f"✅ {len(videos)}個の動画ファイルが見つかりました")
            return videos
            
        except HttpError as error:
            print(f"❌ Google Drive 検索エラー: {error}")
            return []
        except Exception as e:
            print(f"❌ 動画検索エラー: {e}")
            return []
    
    def search_videos_by_name(self, name_query: str, folder_id: str = None) -> List[Dict[str, Any]]:
        """ファイル名で動画を検索"""
        return self.search_videos(query=name_query, folder_id=folder_id)
    
    def get_video_by_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """動画IDで動画情報を取得"""
        try:
            if not self.service:
                return None
            
            file_info = self.service.files().get(
                fileId=video_id,
                fields="id, name, size, createdTime, modifiedTime, webViewLink, webContentLink, parents"
            ).execute()
            
            return {
                'id': file_info['id'],
                'name': file_info['name'],
                'size': self._format_file_size(int(file_info.get('size', 0))),
                'created_time': file_info.get('createdTime', ''),
                'modified_time': file_info.get('modifiedTime', ''),
                'web_view_link': file_info.get('webViewLink', ''),
                'web_content_link': file_info.get('webContentLink', ''),
                'parents': file_info.get('parents', [])
            }
            
        except HttpError as error:
            print(f"❌ 動画取得エラー: {error}")
            return None
        except Exception as e:
            print(f"❌ 動画取得エラー: {e}")
            return None
    
    def list_folders(self, parent_folder_id: str = None) -> List[Dict[str, Any]]:
        """フォルダ一覧を取得"""
        try:
            if not self.service:
                return []
            
            # 検索クエリを構築
            search_query = "mimeType = 'application/vnd.google-apps.folder'"
            
            if parent_folder_id:
                search_query += f" and '{parent_folder_id}' in parents"
            
            results = self.service.files().list(
                q=search_query,
                pageSize=100,
                fields="nextPageToken, files(id, name, createdTime, modifiedTime, parents)"
            ).execute()
            
            items = results.get('files', [])
            
            folders = []
            for item in items:
                folder_info = {
                    'id': item['id'],
                    'name': item['name'],
                    'created_time': item.get('createdTime', ''),
                    'modified_time': item.get('modifiedTime', ''),
                    'parents': item.get('parents', [])
                }
                folders.append(folder_info)
            
            return folders
            
        except HttpError as error:
            print(f"❌ フォルダ一覧取得エラー: {error}")
            return []
        except Exception as e:
            print(f"❌ フォルダ一覧取得エラー: {e}")
            return []
    
    def get_video_download_url(self, video_id: str) -> Optional[str]:
        """動画のダウンロードURLを取得"""
        try:
            if not self.service:
                return None
            
            file_info = self.service.files().get(
                fileId=video_id,
                fields="webContentLink"
            ).execute()
            
            return file_info.get('webContentLink')
            
        except HttpError as error:
            print(f"❌ ダウンロードURL取得エラー: {error}")
            return None
        except Exception as e:
            print(f"❌ ダウンロードURL取得エラー: {e}")
            return None
    
    def search_videos_in_folder(self, folder_name: str) -> List[Dict[str, Any]]:
        """指定されたフォルダ名内の動画を検索"""
        try:
            # フォルダを検索
            folders = self.list_folders()
            target_folder = None
            
            for folder in folders:
                if folder_name.lower() in folder['name'].lower():
                    target_folder = folder
                    break
            
            if not target_folder:
                print(f"❌ フォルダ '{folder_name}' が見つかりません")
                return []
            
            # フォルダ内の動画を検索
            return self.search_videos(folder_id=target_folder['id'])
            
        except Exception as e:
            print(f"❌ フォルダ内動画検索エラー: {e}")
            return []
    
    def get_recent_videos(self, days: int = 30, max_results: int = 20) -> List[Dict[str, Any]]:
        """最近追加された動画を取得"""
        try:
            if not self.service:
                return []
            
            from datetime import datetime, timedelta
            
            # 日付範囲を計算
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 検索クエリを構築
            search_query = f"mimeType contains 'video/' and createdTime > '{start_date.isoformat()}Z'"
            
            results = self.service.files().list(
                q=search_query,
                pageSize=max_results,
                orderBy='createdTime desc',
                fields="nextPageToken, files(id, name, size, createdTime, modifiedTime, webViewLink, webContentLink, parents)"
            ).execute()
            
            items = results.get('files', [])
            
            videos = []
            for item in items:
                video_info = {
                    'id': item['id'],
                    'name': item['name'],
                    'size': self._format_file_size(int(item.get('size', 0))),
                    'created_time': item.get('createdTime', ''),
                    'modified_time': item.get('modifiedTime', ''),
                    'web_view_link': item.get('webViewLink', ''),
                    'web_content_link': item.get('webContentLink', ''),
                    'parents': item.get('parents', [])
                }
                videos.append(video_info)
            
            return videos
            
        except Exception as e:
            print(f"❌ 最近の動画取得エラー: {e}")
            return []
    
    def _format_file_size(self, size_bytes: int) -> str:
        """ファイルサイズをフォーマット"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def create_video_database(self, output_file: str = "data/video_database.json") -> bool:
        """動画データベースを作成"""
        try:
            import json
            
            # すべての動画を取得
            all_videos = self.search_videos(max_results=1000)
            
            # データベース形式で整理
            video_database = {
                'created_at': datetime.now().isoformat(),
                'total_videos': len(all_videos),
                'videos': all_videos
            }
            
            # ファイルに保存
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(video_database, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 動画データベースを作成しました: {output_file}")
            print(f"   総動画数: {len(all_videos)}")
            return True
            
        except Exception as e:
            print(f"❌ 動画データベース作成エラー: {e}")
            return False

#!/usr/bin/env python3
"""
Meta広告自動出稿システム - Streamlit WebUI
"""
import streamlit as st
import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.meta_client import MetaAdsClient
from src.template_manager import TemplateManager
from src.google_drive_manager import GoogleDriveManager
from src.logger import AdLogger

# ページ設定
st.set_page_config(
    page_title="Meta広告自動出稿システム",
    page_icon="📌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション状態の初期化
if 'meta_client' not in st.session_state:
    st.session_state.meta_client = None
if 'template_manager' not in st.session_state:
    st.session_state.template_manager = None
if 'drive_manager' not in st.session_state:
    st.session_state.drive_manager = None
if 'logger' not in st.session_state:
    st.session_state.logger = None

def initialize_services():
    """サービスを初期化"""
    try:
        if st.session_state.meta_client is None:
            st.session_state.meta_client = MetaAdsClient()
        if st.session_state.template_manager is None:
            st.session_state.template_manager = TemplateManager()
        if st.session_state.drive_manager is None:
            st.session_state.drive_manager = GoogleDriveManager()
        if st.session_state.logger is None:
            st.session_state.logger = AdLogger()
        return True
    except Exception as e:
        st.error(f"サービス初期化エラー: {e}")
        return False

def main():
    """メイン関数"""
    st.title("📌 Meta広告自動出稿システム")
    st.markdown("---")
    
    # サイドバーでサービス初期化
    with st.sidebar:
        st.header("🔧 システム設定")
        if st.button("サービス初期化"):
            with st.spinner("サービスを初期化中..."):
                if initialize_services():
                    st.success("✅ サービスが初期化されました")
                else:
                    st.error("❌ サービス初期化に失敗しました")
        
        # サービス状態表示
        st.subheader("📊 サービス状態")
        services_status = {
            "Meta API": st.session_state.meta_client is not None,
            "テンプレート管理": st.session_state.template_manager is not None,
            "Google Drive": st.session_state.drive_manager is not None,
            "ログ管理": st.session_state.logger is not None
        }
        
        for service, status in services_status.items():
            if status:
                st.success(f"✅ {service}")
            else:
                st.error(f"❌ {service}")
    
    # メインコンテンツ
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 キャンペーン作成", "📋 テンプレート管理", "🎬 動画管理", "📊 ログ・履歴"])
    
    with tab1:
        campaign_creation_tab()
    
    with tab2:
        template_management_tab()
    
    with tab3:
        video_management_tab()
    
    with tab4:
        logs_tab()

def campaign_creation_tab():
    """キャンペーン作成タブ"""
    st.header("🚀 キャンペーン作成")
    
    if st.session_state.meta_client is None:
        st.warning("⚠️ まずサイドバーでサービスを初期化してください")
        return
    
    # 作成方法選択
    creation_method = st.radio(
        "作成方法を選択してください:",
        ["📝 個別作成", "📊 一括作成", "⚡ テンプレート使用"]
    )
    
    if creation_method == "📝 個別作成":
        single_campaign_form()
    elif creation_method == "📊 一括作成":
        batch_campaign_form()
    elif creation_method == "⚡ テンプレート使用":
        template_campaign_form()

def single_campaign_form():
    """個別キャンペーン作成フォーム"""
    st.subheader("📝 個別キャンペーン作成")
    
    with st.form("single_campaign_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # 広告アカウント選択
            st.subheader("📋 基本設定")
            
            # アカウント一覧取得
            try:
                accounts = st.session_state.meta_client.get_ad_accounts()
                account_options = {f"{acc['name']} (ID: {acc['id']})": acc['id'] for acc in accounts}
                selected_account = st.selectbox(
                    "広告アカウント",
                    options=list(account_options.keys()),
                    help="Business Manager配下の広告アカウントから選択"
                )
                account_id = account_options[selected_account]
            except Exception as e:
                st.error(f"アカウント取得エラー: {e}")
                return
            
            # キャンペーン基本情報
            campaign_name = st.text_input(
                "キャンペーン名",
                placeholder="例: 2024年新春セール",
                help="キャンペーンの名前を入力"
            )
            
            objective_options = {
                "リンククリック": "LINK_CLICKS",
                "コンバージョン": "CONVERSIONS", 
                "リーチ": "REACH",
                "ブランド認知": "BRAND_AWARENESS"
            }
            objective = st.selectbox(
                "キャンペーン目的",
                options=list(objective_options.keys()),
                help="キャンペーンの目的を選択"
            )
            objective_value = objective_options[objective]
        
        with col2:
            # 予算・配信設定
            st.subheader("💰 予算・配信設定")
            
            budget_type = st.radio(
                "予算タイプ",
                ["日単位", "総額"],
                help="予算の設定方法を選択"
            )
            
            if budget_type == "日単位":
                budget = st.number_input(
                    "1日予算 (円)",
                    min_value=100,
                    value=1000,
                    step=100,
                    help="1日あたりの予算を設定"
                )
            else:
                total_budget = st.number_input(
                    "総予算 (円)",
                    min_value=1000,
                    value=10000,
                    step=1000,
                    help="キャンペーン全体の予算を設定"
                )
                campaign_days = st.number_input(
                    "配信日数",
                    min_value=1,
                    value=7,
                    help="配信する日数を設定"
                )
                budget = total_budget / campaign_days
            
            # 配信期間
            col_start, col_end = st.columns(2)
            with col_start:
                start_date = st.date_input(
                    "配信開始日",
                    value=datetime.now().date(),
                    help="配信開始日を選択"
                )
            with col_end:
                end_date = st.date_input(
                    "配信終了日",
                    value=(datetime.now() + timedelta(days=7)).date(),
                    help="配信終了日を選択"
                )
        
        # 広告クリエイティブ
        st.subheader("🎨 広告クリエイティブ")
        
        col3, col4 = st.columns(2)
        
        with col3:
            headline = st.text_area(
                "見出し",
                placeholder="例: 【限定セール】今だけ50%OFF！",
                height=100,
                help="広告の見出しを入力"
            )
            
            description = st.text_area(
                "説明文",
                placeholder="例: お得な情報をお見逃しなく！詳細はこちらから。",
                height=100,
                help="広告の説明文を入力"
            )
        
        with col4:
            url = st.text_input(
                "リンク先URL",
                placeholder="https://example.com/landing-page",
                help="広告のリンク先URLを入力"
            )
            
            # 動画選択
            st.subheader("🎬 動画選択")
            
            video_option = st.radio(
                "動画選択方法",
                ["Google Driveから検索", "ファイルアップロード", "動画なし"]
            )
            
            video_id = None
            if video_option == "Google Driveから検索":
                video_search_term = st.text_input(
                    "動画名で検索",
                    placeholder="動画名の一部を入力",
                    help="Google Driveから動画を検索"
                )
                if video_search_term and st.button("🔍 動画検索"):
                    with st.spinner("動画を検索中..."):
                        try:
                            videos = st.session_state.drive_manager.search_videos_by_name(video_search_term)
                            if videos:
                                video_options = {f"{v['name']} ({v['size']})": v['id'] for v in videos}
                                selected_video = st.selectbox(
                                    "検索結果から選択",
                                    options=list(video_options.keys())
                                )
                                video_id = video_options[selected_video]
                                st.success(f"✅ 動画を選択しました: {selected_video}")
                            else:
                                st.warning("動画が見つかりませんでした")
                        except Exception as e:
                            st.error(f"動画検索エラー: {e}")
            
            elif video_option == "ファイルアップロード":
                uploaded_file = st.file_uploader(
                    "動画ファイルをアップロード",
                    type=['mp4', 'mov', 'avi', 'mkv'],
                    help="動画ファイルをアップロード（最大100MB）"
                )
                if uploaded_file:
                    st.info("📁 ファイルアップロード機能は開発中です")
        
        # 送信ボタン
        submitted = st.form_submit_button("🚀 キャンペーンを作成", type="primary")
        
        if submitted:
            # 入力検証
            if not campaign_name:
                st.error("❌ キャンペーン名は必須です")
                return
            if not headline:
                st.error("❌ 見出しは必須です")
                return
            if not description:
                st.error("❌ 説明文は必須です")
                return
            if not url:
                st.error("❌ リンク先URLは必須です")
                return
            
            # キャンペーン作成実行
            create_campaign(
                account_id=account_id,
                campaign_name=campaign_name,
                objective=objective_value,
                budget=budget,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                headline=headline,
                description=description,
                url=url,
                video_id=video_id
            )

def batch_campaign_form():
    """一括キャンペーン作成フォーム"""
    st.subheader("📊 一括キャンペーン作成")
    
    # CSV アップロード
    st.info("💡 CSVファイルで一括作成できます")
    
    # サンプルCSVダウンロード
    sample_data = {
        'キャンペーン名': ['サンプルキャンペーン1', 'サンプルキャンペーン2'],
        '商品名': ['商品A', '商品B'],
        '目的': ['LINK_CLICKS', 'CONVERSIONS'],
        '予算(円/日)': [1000, 2000],
        '開始日': ['2024-01-01', '2024-01-01'],
        '終了日': ['2024-01-07', '2024-01-14'],
        '見出し': ['【商品A】特別価格！', '【商品B】限定セール！'],
        '説明文': ['お得な情報をお見逃しなく！', '数量限定！今すぐチェック！'],
        'URL': ['https://example.com/product-a', 'https://example.com/product-b'],
        '動画名': ['', '']
    }
    
    sample_df = pd.DataFrame(sample_data)
    csv = sample_df.to_csv(index=False, encoding='utf-8-sig')
    
    st.download_button(
        label="📥 サンプルCSVをダウンロード",
        data=csv,
        file_name="campaign_template.csv",
        mime="text/csv"
    )
    
    # CSV アップロード
    uploaded_file = st.file_uploader(
        "CSVファイルをアップロード",
        type=['csv'],
        help="上記のサンプル形式でCSVファイルを作成してアップロード"
    )
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            st.success(f"✅ {len(df)}件のキャンペーンデータを読み込みました")
            
            # データプレビュー
            st.subheader("📋 データプレビュー")
            st.dataframe(df, use_container_width=True)
            
            # アカウント選択
            try:
                accounts = st.session_state.meta_client.get_ad_accounts()
                account_options = {f"{acc['name']} (ID: {acc['id']})": acc['id'] for acc in accounts}
                selected_account = st.selectbox(
                    "広告アカウント",
                    options=list(account_options.keys()),
                    help="一括作成する広告アカウントを選択"
                )
                account_id = account_options[selected_account]
            except Exception as e:
                st.error(f"アカウント取得エラー: {e}")
                return
            
            # 一括作成実行
            if st.button("🚀 一括作成を実行", type="primary"):
                with st.spinner("一括作成中..."):
                    success_count = 0
                    error_count = 0
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, row in df.iterrows():
                        status_text.text(f"処理中: {row['キャンペーン名']} ({i+1}/{len(df)})")
                        
                        try:
                            # 動画検索
                            video_id = None
                            if row.get('動画名') and pd.notna(row['動画名']):
                                videos = st.session_state.drive_manager.search_videos_by_name(str(row['動画名']))
                                if videos:
                                    video_id = videos[0]['id']
                            
                            # キャンペーン作成
                            success = create_campaign(
                                account_id=account_id,
                                campaign_name=row['キャンペーン名'],
                                objective=row['目的'],
                                budget=float(row['予算(円/日)']),
                                start_date=row['開始日'],
                                end_date=row['終了日'],
                                headline=row['見出し'],
                                description=row['説明文'],
                                url=row['URL'],
                                video_id=video_id,
                                show_success=False
                            )
                            
                            if success:
                                success_count += 1
                            else:
                                error_count += 1
                                
                        except Exception as e:
                            st.error(f"エラー: {row['キャンペーン名']} - {e}")
                            error_count += 1
                        
                        progress_bar.progress((i + 1) / len(df))
                    
                    status_text.text("完了")
                    st.success(f"✅ 一括作成完了: 成功 {success_count}件, エラー {error_count}件")
                    
        except Exception as e:
            st.error(f"CSV読み込みエラー: {e}")

def template_campaign_form():
    """テンプレート使用キャンペーン作成フォーム"""
    st.subheader("⚡ テンプレート使用キャンペーン作成")
    
    if st.session_state.template_manager is None:
        st.warning("⚠️ テンプレート管理サービスが初期化されていません")
        return
    
    # テンプレート選択
    try:
        templates = st.session_state.template_manager.list_templates()
        if not templates:
            st.warning("利用可能なテンプレートがありません")
            return
        
        template_options = {t['name']: t['name'] for t in templates}
        selected_template = st.selectbox(
            "使用するテンプレート",
            options=list(template_options.keys()),
            help="事前作成したテンプレートから選択"
        )
        
        # テンプレート情報表示
        template_info = st.session_state.template_manager.load_template(selected_template)
        if template_info:
            with st.expander("📋 テンプレート設定を確認"):
                st.json(template_info)
        
        # 基本情報入力
        with st.form("template_campaign_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                campaign_name = st.text_input(
                    "キャンペーン名",
                    placeholder="例: 2024年新春セール",
                    help="キャンペーンの名前を入力"
                )
                
                product_name = st.text_input(
                    "商品名",
                    placeholder="例: 特別商品",
                    help="商品名を入力（テンプレート変数で使用）"
                )
            
            with col2:
                # アカウント選択
                try:
                    accounts = st.session_state.meta_client.get_ad_accounts()
                    account_options = {f"{acc['name']} (ID: {acc['id']})": acc['id'] for acc in accounts}
                    selected_account = st.selectbox(
                        "広告アカウント",
                        options=list(account_options.keys()),
                        help="Business Manager配下の広告アカウントから選択"
                    )
                    account_id = account_options[selected_account]
                except Exception as e:
                    st.error(f"アカウント取得エラー: {e}")
                    return
            
            # カスタマイズオプション
            st.subheader("🔧 カスタマイズ設定")
            
            col3, col4 = st.columns(2)
            
            with col3:
                custom_budget = st.number_input(
                    "予算 (円/日)",
                    min_value=100,
                    value=int(template_info.get('ad_set', {}).get('budget', 1000)),
                    step=100,
                    help="テンプレートの予算を上書き"
                )
                
                custom_start_date = st.date_input(
                    "配信開始日",
                    value=datetime.now().date(),
                    help="配信開始日を選択"
                )
            
            with col4:
                custom_end_date = st.date_input(
                    "配信終了日",
                    value=(datetime.now() + timedelta(days=7)).date(),
                    help="配信終了日を選択"
                )
            
            # 送信ボタン
            submitted = st.form_submit_button("🚀 テンプレートでキャンペーンを作成", type="primary")
            
            if submitted:
                if not campaign_name:
                    st.error("❌ キャンペーン名は必須です")
                    return
                
                # テンプレート適用
                try:
                    variables = {
                        'campaign_name': campaign_name,
                        'product_name': product_name or "商品",
                        'current_date': datetime.now().strftime('%Y-%m-%d')
                    }
                    
                    applied_template = st.session_state.template_manager.apply_template(selected_template, variables)
                    
                    # カスタマイズ値を適用
                    applied_template['ad_set']['budget'] = custom_budget
                    applied_template['ad_set']['start_time'] = custom_start_date.strftime('%Y-%m-%d')
                    applied_template['ad_set']['end_time'] = custom_end_date.strftime('%Y-%m-%d')
                    
                    # キャンペーン作成実行
                    create_campaign_from_template(account_id, applied_template)
                    
                except Exception as e:
                    st.error(f"テンプレート適用エラー: {e}")
    
    except Exception as e:
        st.error(f"テンプレート取得エラー: {e}")

def create_campaign(account_id, campaign_name, objective, budget, start_date, end_date, 
                   headline, description, url, video_id=None, show_success=True):
    """キャンペーン作成"""
    try:
        with st.spinner("キャンペーンを作成中..."):
            # キャンペーン作成
            campaign = st.session_state.meta_client.create_campaign(
                account_id, campaign_name, objective
            )
            
            # 広告セット作成
            ad_set = st.session_state.meta_client.create_ad_set(
                account_id, campaign['id'], f"{campaign_name}_AdSet",
                budget, start_date, end_date
            )
            
            # クリエイティブ作成
            creative = st.session_state.meta_client.create_ad_creative(
                account_id, f"{campaign_name}_Creative",
                headline, description, url, video_id
            )
            
            # 広告作成
            ad = st.session_state.meta_client.create_ad(
                account_id, ad_set['id'], creative['id'], f"{campaign_name}_Ad"
            )
            
            # ログ記録
            st.session_state.logger.log_campaign_creation({
                'account_id': account_id,
                'campaign_id': campaign['id'],
                'ad_set_id': ad_set['id'],
                'creative_id': creative['id'],
                'ad_id': ad['id']
            }, True)
            
            if show_success:
                st.success("🎉 キャンペーン作成が完了しました！")
                st.info(f"📊 キャンペーンID: {campaign['id']}")
                st.info(f"📊 広告ID: {ad['id']}")
                st.warning("⚠️ 広告は一時停止状態で作成されました。配信開始には手動で有効化が必要です。")
            
            return True
            
    except Exception as e:
        st.error(f"❌ キャンペーン作成エラー: {e}")
        st.session_state.logger.log_campaign_creation({}, False, str(e))
        return False

def create_campaign_from_template(account_id, template_data):
    """テンプレートからキャンペーン作成"""
    try:
        with st.spinner("テンプレートからキャンペーンを作成中..."):
            # キャンペーン作成
            campaign = st.session_state.meta_client.create_campaign(
                account_id,
                template_data['campaign']['name_template'],
                template_data['campaign']['objective']
            )
            
            # 広告セット作成
            ad_set = st.session_state.meta_client.create_ad_set(
                account_id,
                campaign['id'],
                template_data['ad_set']['name_template'],
                template_data['ad_set']['budget'],
                template_data['ad_set']['start_time'],
                template_data['ad_set']['end_time']
            )
            
            # クリエイティブ作成
            creative = st.session_state.meta_client.create_ad_creative(
                account_id,
                template_data['creative']['name_template'],
                template_data['creative']['headline_template'],
                template_data['creative']['description_template'],
                template_data['creative']['url_template'],
                template_data['creative'].get('video_id')
            )
            
            # 広告作成
            ad = st.session_state.meta_client.create_ad(
                account_id,
                ad_set['id'],
                creative['id'],
                template_data['ad']['name_template']
            )
            
            # ログ記録
            st.session_state.logger.log_campaign_creation({
                'account_id': account_id,
                'campaign_id': campaign['id'],
                'ad_set_id': ad_set['id'],
                'creative_id': creative['id'],
                'ad_id': ad['id'],
                'template_used': template_data.get('template_name', 'Unknown')
            }, True)
            
            st.success("🎉 テンプレートからキャンペーン作成が完了しました！")
            st.info(f"📊 キャンペーンID: {campaign['id']}")
            st.info(f"📊 広告ID: {ad['id']}")
            st.warning("⚠️ 広告は一時停止状態で作成されました。配信開始には手動で有効化が必要です。")
            
    except Exception as e:
        st.error(f"❌ テンプレートキャンペーン作成エラー: {e}")

def template_management_tab():
    """テンプレート管理タブ"""
    st.header("📋 テンプレート管理")
    
    if st.session_state.template_manager is None:
        st.warning("⚠️ まずサイドバーでサービスを初期化してください")
        return
    
    tab_create, tab_list, tab_edit = st.tabs(["➕ 作成", "📋 一覧", "✏️ 編集"])
    
    with tab_create:
        st.subheader("➕ 新しいテンプレートを作成")
        
        with st.form("create_template_form"):
            template_name = st.text_input("テンプレート名", placeholder="例: 新春セール用テンプレート")
            description = st.text_area("説明", placeholder="テンプレートの説明を入力")
            
            col1, col2 = st.columns(2)
            
            with col1:
                objective = st.selectbox(
                    "キャンペーン目的",
                    ["LINK_CLICKS", "CONVERSIONS", "REACH", "BRAND_AWARENESS"]
                )
                
                default_budget = st.number_input(
                    "デフォルト予算 (円/日)",
                    min_value=100,
                    value=1000,
                    step=100
                )
            
            with col2:
                headline_template = st.text_input(
                    "見出しテンプレート",
                    value="【{product_name}】今だけ特別価格！"
                )
                
                description_template = st.text_area(
                    "説明文テンプレート",
                    value="お得な情報をお見逃しなく！詳細はこちらから。"
                )
            
            url_template = st.text_input(
                "URLテンプレート",
                value="https://example.com/{campaign_name}"
            )
            
            if st.form_submit_button("📝 テンプレートを作成"):
                if template_name:
                    # テンプレート作成
                    template = st.session_state.template_manager.create_default_template()
                    template['template_name'] = template_name
                    template['description'] = description
                    template['campaign']['objective'] = objective
                    template['ad_set']['budget'] = default_budget
                    template['creative']['headline_template'] = headline_template
                    template['creative']['description_template'] = description_template
                    template['creative']['url_template'] = url_template
                    
                    if st.session_state.template_manager.save_template(template):
                        st.success(f"✅ テンプレート '{template_name}' を作成しました")
                    else:
                        st.error("❌ テンプレート作成に失敗しました")
                else:
                    st.error("❌ テンプレート名は必須です")
    
    with tab_list:
        st.subheader("📋 テンプレート一覧")
        
        try:
            templates = st.session_state.template_manager.list_templates()
            if templates:
                for template in templates:
                    with st.expander(f"📋 {template['name']}"):
                        st.write(f"**説明:** {template['description']}")
                        st.write(f"**作成日:** {template['created_at'][:10]}")
                        st.write(f"**更新日:** {template['updated_at'][:10]}")
                        
                        if st.button(f"🗑️ 削除", key=f"delete_{template['name']}"):
                            if st.session_state.template_manager.delete_template(template['name']):
                                st.success(f"✅ テンプレート '{template['name']}' を削除しました")
                                st.rerun()
                            else:
                                st.error("❌ テンプレート削除に失敗しました")
            else:
                st.info("テンプレートがありません")
        except Exception as e:
            st.error(f"テンプレート一覧取得エラー: {e}")
    
    with tab_edit:
        st.subheader("✏️ テンプレート編集")
        st.info("テンプレート編集機能は開発中です")

def video_management_tab():
    """動画管理タブ"""
    st.header("🎬 動画管理")
    
    if st.session_state.drive_manager is None:
        st.warning("⚠️ まずサイドバーでサービスを初期化してください")
        return
    
    tab_search, tab_upload, tab_database = st.tabs(["🔍 検索", "📤 アップロード", "💾 データベース"])
    
    with tab_search:
        st.subheader("🔍 動画検索")
        
        search_type = st.radio(
            "検索方法",
            ["キーワード検索", "名前検索", "最近の動画", "フォルダ検索"]
        )
        
        if search_type == "キーワード検索":
            query = st.text_input("検索キーワード", placeholder="動画の内容や名前の一部を入力")
            max_results = st.slider("最大結果数", 10, 100, 20)
            
            if st.button("🔍 検索"):
                if query:
                    with st.spinner("動画を検索中..."):
                        try:
                            videos = st.session_state.drive_manager.search_videos(query=query, max_results=max_results)
                            display_videos(videos)
                        except Exception as e:
                            st.error(f"検索エラー: {e}")
                else:
                    st.warning("検索キーワードを入力してください")
        
        elif search_type == "名前検索":
            name_query = st.text_input("動画名", placeholder="動画名の一部を入力")
            
            if st.button("🔍 名前で検索"):
                if name_query:
                    with st.spinner("動画を検索中..."):
                        try:
                            videos = st.session_state.drive_manager.search_videos_by_name(name_query)
                            display_videos(videos)
                        except Exception as e:
                            st.error(f"検索エラー: {e}")
                else:
                    st.warning("動画名を入力してください")
        
        elif search_type == "最近の動画":
            days = st.slider("何日前から", 1, 90, 30)
            max_results = st.slider("最大結果数", 5, 50, 20)
            
            if st.button("📅 最近の動画を表示"):
                with st.spinner("最近の動画を取得中..."):
                    try:
                        videos = st.session_state.drive_manager.get_recent_videos(days=days, max_results=max_results)
                        display_videos(videos)
                    except Exception as e:
                        st.error(f"取得エラー: {e}")
        
        elif search_type == "フォルダ検索":
            folder_name = st.text_input("フォルダ名", placeholder="フォルダ名の一部を入力")
            
            if st.button("📁 フォルダ内を検索"):
                if folder_name:
                    with st.spinner("フォルダ内の動画を検索中..."):
                        try:
                            videos = st.session_state.drive_manager.search_videos_in_folder(folder_name)
                            display_videos(videos)
                        except Exception as e:
                            st.error(f"検索エラー: {e}")
                else:
                    st.warning("フォルダ名を入力してください")
    
    with tab_upload:
        st.subheader("📤 動画アップロード")
        st.info("📁 動画アップロード機能は開発中です")
        st.info("現在はGoogle Driveに直接アップロードしてから検索機能をご利用ください")
    
    with tab_database:
        st.subheader("💾 動画データベース")
        
        if st.button("🔄 データベースを更新"):
            with st.spinner("動画データベースを作成中..."):
                try:
                    success = st.session_state.drive_manager.create_video_database()
                    if success:
                        st.success("✅ 動画データベースが更新されました")
                    else:
                        st.error("❌ データベース更新に失敗しました")
                except Exception as e:
                    st.error(f"データベース更新エラー: {e}")

def display_videos(videos):
    """動画一覧を表示"""
    if not videos:
        st.warning("動画が見つかりませんでした")
        return
    
    st.success(f"✅ {len(videos)}個の動画が見つかりました")
    
    for i, video in enumerate(videos):
        with st.expander(f"🎬 {video['name']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**ID:** {video['id']}")
                st.write(f"**サイズ:** {video['size']}")
                st.write(f"**作成日:** {video['created_time'][:10]}")
                st.write(f"**URL:** {video['web_view_link']}")
            
            with col2:
                if st.button(f"📋 IDをコピー", key=f"copy_{i}"):
                    st.code(video['id'])
                    st.success("IDをクリップボードにコピーしました")

def logs_tab():
    """ログ・履歴タブ"""
    st.header("📊 ログ・履歴")
    
    if st.session_state.logger is None:
        st.warning("⚠️ まずサイドバーでサービスを初期化してください")
        return
    
    # ログ表示
    st.subheader("📋 最近の操作ログ")
    
    limit = st.slider("表示件数", 5, 50, 10)
    
    if st.button("🔄 ログを更新"):
        try:
            logs = st.session_state.logger.get_recent_logs(limit)
            if logs:
                for log in logs:
                    status = "✅" if log['success'] else "❌"
                    timestamp = log['timestamp'][:19]
                    action = log['action']
                    
                    with st.expander(f"{status} {timestamp} - {action}"):
                        st.json(log)
                        
                        if not log['success'] and log.get('error'):
                            st.error(f"エラー: {log['error']}")
            else:
                st.info("ログが見つかりません")
        except Exception as e:
            st.error(f"ログ取得エラー: {e}")

if __name__ == "__main__":
    main()

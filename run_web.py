#!/usr/bin/env python3
"""
Meta広告自動出稿システム - WebUI起動スクリプト
"""
import subprocess
import sys
import os

def main():
    """WebUIを起動"""
    print("🚀 Meta広告自動出稿システム WebUI を起動します...")
    print("📌 ブラウザで http://localhost:8501 にアクセスしてください")
    print("⚠️  Ctrl+C で終了できます")
    print("-" * 60)
    
    try:
        # Streamlitアプリを起動
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "web_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 WebUIを終了します")
    except Exception as e:
        print(f"❌ 起動エラー: {e}")

if __name__ == "__main__":
    main()

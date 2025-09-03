#!/usr/bin/env python3
"""
Meta広告自動出稿システム - メインエントリーポイント
"""
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli import main

if __name__ == "__main__":
    main()

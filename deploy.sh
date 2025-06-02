#!/bin/bash

# スクリプト内でエラーが発生したらすぐに終了
set -e

echo "--- Custom deployment script started ---"

# Azure App Serviceのアプリケーションルートディレクトリ
# アプリのファイルは最終的にここに配置されます
DEPLOYMENT_TARGET_DIR="/home/site/wwwroot"
echo "Moving to deployment target directory: $DEPLOYMENT_TARGET_DIR"
mkdir -p "$DEPLOYMENT_TARGET_DIR" # 念のためディレクトリを作成
cd "$DEPLOYMENT_TARGET_DIR"

# Oryxがソースコードを展開する一時ディレクトリ
# GitHubからのデプロイでは通常ここに入ります
SOURCE_DIR="/tmp/zipdeploy/extracted"
echo "Source directory for initial files: $SOURCE_DIR"

# 既存のデプロイファイルを削除してクリーンな状態にする
# ただし、App Serviceが最初に生成する hostingstart.html は残しておく
echo "Cleaning existing files in $DEPLOYMENT_TARGET_DIR (excluding hostingstart.html)..."
# 現在のディレクトリのファイルとディレクトリを再帰的に削除。ただし、hostingstart.htmlは除外。
find . -mindepth 1 ! -name "hostingstart.html" -exec rm -rf {} +

# ソースコードをデプロイ先にコピー
# これにより、testproject/ディレクトリ、manage.py、requirements.txt などが
# /home/site/wwwroot の直下に配置されます
echo "Copying source files from $SOURCE_DIR to $DEPLOYMENT_TARGET_DIR..."
cp -R "$SOURCE_DIR"/* .

# Python仮想環境を作成し、依存関係をインストール
# virtualenv_name=antenv に合わせて /home/site/wwwroot/antenv に仮想環境を作成します
VENV_DIR="$DEPLOYMENT_TARGET_DIR/antenv"
echo "Creating/activating virtual environment at: $VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

# collectstatic の実行
# settings.py で STATIC_ROOT = BASE_DIR / 'staticfiles' としているので、
# これにより /home/site/wwwroot/staticfiles に静的ファイルが収集されます
echo "Running Django collectstatic..."
python manage.py collectstatic --noinput

# 仮想環境を非アクティブ化
deactivate

echo "--- Custom deployment script finished successfully ---"
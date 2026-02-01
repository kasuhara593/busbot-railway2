FROM python:3.10-slim

WORKDIR /app

# 依存関係を先にコピーしてインストール（ビルド高速化）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体をコピー
COPY busbot.py .

# 実行
CMD ["python", "busbot.py"]

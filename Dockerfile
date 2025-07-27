FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    gettext \
    libmariadb-dev-compat \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt を先にコピーして依存をインストール
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# プロジェクト全体をコピー
COPY . .

WORKDIR /app/todo_app

EXPOSE 8000

# 開発環境用 - runserverを使用
CMD ["sh", "-c", "python manage.py migrate && python manage.py create_demo_user && python manage.py runserver 0.0.0.0:8000"]
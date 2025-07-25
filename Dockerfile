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

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

FROM python:3.11-slim

# Отключаем генерацию .pyc файлов и включаем моментальный вывод логов Django
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка системных зависимостей для сборки C-пакетов (cffi, psycopg2 и т.д.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Копируем весь проект
COPY . .

# Открываем порт (для Gunicorn)
EXPOSE 8000

# Запуск Gunicorn
CMD ["gunicorn", "newprod.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "30"]
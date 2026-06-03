# Dockerfile
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Собираем статику (выполняется при сборке образа)
RUN python manage.py collectstatic --noinput

# Открываем порт (для Gunicorn)
EXPOSE 8000

# Запуск Gunicorn
CMD ["gunicorn", "newprod.wsgi:application", "--bind", "0.0.0.0:8000"]
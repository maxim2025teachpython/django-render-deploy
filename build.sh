#!/usr/bin/env bash
set -o errexit  # Остановить выполнение при ошибке

echo "📦 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🛠 Применение миграций..."
python manage.py makemigrations
python manage.py migrate

echo "🎨 Сбор статических файлов..."
python manage.py collectstatic --no-input

echo "👤 Проверка суперпользователя..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '123456')
    print('✅ Суперпользователь создан: admin / 123456')
else:
    print('ℹ️ Суперпользователь уже существует')
END

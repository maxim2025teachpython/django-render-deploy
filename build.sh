#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Создание суперпользователя ПОСЛЕ миграций
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'yourpassword123')
    print('Superuser created')
else:
    print('Superuser already exists')
"

# Отладка - покажет созданных пользователей
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
users = User.objects.all()
print(f'Total users: {users.count()}')
for user in users:
    print(f'Username: {user.username}, Email: {user.email}, is_superuser: {user.is_superuser}')
"
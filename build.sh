#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt


python manage.py createsuperuser --noinput
python manage.py create_superuser
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'yourpassword123')
    print('Superuser created')



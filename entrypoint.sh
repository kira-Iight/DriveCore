#!/bin/bash
# entrypoint.sh

set -e

# Применение миграций
echo "Применение миграций..."
python manage.py migrate

# Сбор статики
echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

# Создание суперпользователя (если не существует)
echo "Создание суперпользователя..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Суперпользователь создан')
"

# Запуск команды
exec "$@"

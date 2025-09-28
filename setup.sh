#!/bin/bash

# Exit on error
set -e

echo "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Creating superuser if not exists..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); \
username='$DJANGO_SUPERUSER_USERNAME'; email='$DJANGO_SUPERUSER_EMAIL'; password='$DJANGO_SUPERUSER_PASSWORD'; \
User.objects.filter(username=username).exists() or User.objects.create_superuser(username=username, email=email, password=password)"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Uploading existing media to Cloudinary..."
python manage.py upload_to_cloudinary  # only if you have that command set up

echo "Setup complete!"

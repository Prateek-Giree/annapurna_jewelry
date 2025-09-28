#!/bin/bash

# Exit immediately if a command fails
set -e
set -o pipefail

echo "=== Installing Python dependencies ==="
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "=== Running migrations ==="
python manage.py makemigrations
python manage.py migrate

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput
echo "Static files collected successfully."

# Optional: Upload existing media to Cloudinary
if python manage.py help | grep -q upload_to_cloudinary; then
    echo "=== Uploading existing media to Cloudinary ==="
    python manage.py upload_to_cloudinary
    echo "Media uploaded to Cloudinary successfully."
else
    echo "No upload_to_cloudinary command found, skipping."
fi

echo "=== Setup complete! ==="

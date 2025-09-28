from django.core.management.base import BaseCommand
from a_app.models import Product

class Command(BaseCommand):
    help = 'Upload existing local images to Cloudinary'

    def handle(self, *args, **kwargs):
        for p in Product.objects.all():
            if p.image and not p.image.url.startswith('http'):
                p.image = p.image  # triggers Cloudinary save
                p.save()
        self.stdout.write(self.style.SUCCESS('All images uploaded to Cloudinary.'))

from django.core.management.base import BaseCommand
from ocr_app.models import ClothingImage
import os

class Command(BaseCommand):
    help = 'Check clothing image records'

    def handle(self, *args, **options):
        records = ClothingImage.objects.all()
        self.stdout.write(f"Found {records.count()} records")

        for record in records:
            self.stdout.write(f"\nRecord ID: {record.id}")
            self.stdout.write(f"Image path: {record.image.path}")
            self.stdout.write(f"Image exists: {os.path.exists(record.image.path)}")
            self.stdout.write(f"Label image path: {record.label_image.path}")
            self.stdout.write(f"Label image exists: {os.path.exists(record.label_image.path)}")
            self.stdout.write(f"Materials: {record.materials}")
            self.stdout.write(f"Recognized text: {record.recognized_text}") 
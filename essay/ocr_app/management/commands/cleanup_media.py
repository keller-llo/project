from django.core.management.base import BaseCommand
from django.conf import settings
from ocr_app.models import ClothingImage
import os

class Command(BaseCommand):
    help = '清理没有对应数据库记录的媒体文件'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        clothing_dir = os.path.join(media_root, 'clothing_images')
        label_dir = os.path.join(media_root, 'label_images')

        # 获取数据库中的所有文件名
        db_clothing_files = set(ClothingImage.objects.values_list('image', flat=True))
        db_label_files = set(ClothingImage.objects.values_list('label_image', flat=True))

        files_removed = 0

        # 清理衣物图片
        if os.path.exists(clothing_dir):
            for file in os.listdir(clothing_dir):
                file_path = os.path.join('clothing_images', file)
                if file_path not in db_clothing_files:
                    os.remove(os.path.join(clothing_dir, file))
                    files_removed += 1
                    self.stdout.write(f"Removed: {file}")

        # 清理标签图片
        if os.path.exists(label_dir):
            for file in os.listdir(label_dir):
                file_path = os.path.join('label_images', file)
                if file_path not in db_label_files:
                    os.remove(os.path.join(label_dir, file))
                    files_removed += 1
                    self.stdout.write(f"Removed: {file}")

        self.stdout.write(self.style.SUCCESS(f'Successfully removed {files_removed} orphaned files')) 
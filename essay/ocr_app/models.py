# ocr_app/models.py
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import pillow_heif  # 需要安装这个包来处理 HEIC
from io import BytesIO
from django.core.files.base import ContentFile
import os
import logging
import time

logger = logging.getLogger(__name__)





class ClothingImage(models.Model):
    """Model to store clothing images and their analysis results"""
    CATEGORY_CHOICES = [
        ('pant', '长裤'),
        ('shortpant', '短裤'),
        ('longsleeve', '长袖'),
        ('tshirt', 'T恤'),
    ]

    image = models.ImageField(upload_to='clothing_images/')
    label_image = models.ImageField(upload_to='label_images/', null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    classification_confidence = models.FloatField(null=True, blank=True)
    recognized_text = models.TextField(null=True, blank=True)
    materials = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        """删除记录和关联的图片文件"""
        
        def try_delete_file(file_path, max_retries=3):
            """尝试删除文件，如果失败则重试"""
            for i in range(max_retries):
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    return True
                except PermissionError:
                    if i < max_retries - 1:
                        print(f"Attempt {i+1}: File is in use, waiting before retry...")
                        time.sleep(1)  # 等待1秒后重试
                    continue
                except Exception as e:
                    print(f"Error deleting file {file_path}: {str(e)}")
                    return False
            return False

        # 尝试删除图片文件
        if self.image:
            try_delete_file(self.image.path)
        
        # 尝试删除标签图片文件
        if self.label_image:
            try_delete_file(self.label_image.path)
        
        # 删除数据库记录
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Clothing {self.id}"

    def save(self, *args, **kwargs):
        print("\n=== Save Debug Info ===")
        print(f"Saving image: {self.image.name if self.image else 'No image'}")
        print(f"Saving label: {self.label_image.name if self.label_image else 'No label'}")
        
        if not self.image:
            raise ValueError("No image provided")
            
        super().save(*args, **kwargs)
        
        # 验证保存后的文件
        if not os.path.exists(self.image.path):
            raise ValueError(f"Image file not saved: {self.image.path}")
        
        print(f"Save successful. ID: {self.id}")
        print(f"Image path: {self.image.path}")
        print(f"Image exists: {os.path.exists(self.image.path)}")

    def convert_heic_to_jpg(self, field_name):
        """将 HEIC 格式转换为 JPG"""
        try:
            # 获取原始文件
            field = getattr(self, field_name)
            heif_file = pillow_heif.read_heif(field.read())
            
            # 转换为 PIL Image
            image = Image.frombytes(
                heif_file.mode, 
                heif_file.size, 
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
            
            # 转换为 RGB（如果需要）
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 保存为 JPG
            output = BytesIO()
            image.save(output, format='JPEG', quality=95)
            output.seek(0)
            
            # 更新文件名和内容
            new_name = os.path.splitext(field.name)[0] + '.jpg'
            setattr(self, field_name, ContentFile(output.read(), name=new_name))
            
        except Exception as e:
            print(f"Error converting HEIC to JPG: {str(e)}")

    class Meta:
        ordering = ['-created_at']  # 按创建时间倒序排列


class WeatherData(models.Model):
    """Model to store weather information"""
    city = models.CharField(max_length=100)
    temperature = models.FloatField()
    humidity = models.FloatField()
    condition = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Weather Data {self.temperature}°C at {self.timestamp}"


class Recommendation(models.Model):
    """Model to store clothing recommendations"""
    clothing = models.ForeignKey(ClothingImage, on_delete=models.CASCADE)
    weather = models.ForeignKey(WeatherData, on_delete=models.CASCADE)
    recommendation_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.clothing}"



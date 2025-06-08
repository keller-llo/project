from django import forms
from .models import ClothingImage

class ClothingItemForm(forms.ModelForm):
    class Meta:
        model = ClothingImage
        fields = ['clothing_image', 'label_image']  # 上传衣服图片和标签图片

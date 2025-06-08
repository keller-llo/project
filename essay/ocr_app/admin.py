from django.contrib import admin
from .models import ClothingImage, WeatherData, Recommendation

@admin.register(ClothingImage)
class ClothingImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'image', 'label_image', 'created_at']
    list_filter = ['created_at']
    search_fields = ['id']

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['city', 'temperature', 'humidity', 'condition', 'timestamp']
    list_filter = ['city', 'timestamp']
    search_fields = ['city']

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['clothing', 'weather', 'created_at']
    list_filter = ['created_at']
    search_fields = ['recommendation_text']

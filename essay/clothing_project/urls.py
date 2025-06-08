from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ocr_app.urls')),  # 包含 ocr_app 的 URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

print("\n=== URL Configuration Debug ===")
print(f"MEDIA_URL: {settings.MEDIA_URL}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
# ocr_app/urls.py
from django.urls import path
from .views import (
    HomeView, BatchUploadView, ClothingListView,
    QueryView, ViewUploadData,
    ManualInputView, ImageCheckView, ImportExistingImagesView,
    SaveLabelTextView, delete_clothing, delete_all_clothing,
    save_materials, update_category
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('upload/', BatchUploadView.as_view(), name='batch_upload'),
    path('clothing_list/', ClothingListView.as_view(), name='clothing_list'),
    path('query/', QueryView.as_view(), name='query'),
    path('view_data/', ViewUploadData.as_view(), name='view_data'),
    path('manual_input/<int:clothing_id>/', ManualInputView.as_view(), name='manual_input'),
    path('image_check/', ImageCheckView.as_view(), name='image_check'),
    path('import_existing/', ImportExistingImagesView.as_view(), name='import_existing'),
    path('save_label_text/', SaveLabelTextView.as_view(), name='save_label_text'),
    path('delete_clothing/<int:clothing_id>/', delete_clothing, name='delete_clothing'),
    path('delete-all/', delete_all_clothing, name='delete_all_clothing'),
    path('save-materials/', save_materials, name='save_materials'),
    path('update_category/<int:clothing_id>/', update_category, name='update_category'),
]

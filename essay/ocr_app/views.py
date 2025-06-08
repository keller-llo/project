from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from PIL import Image
import io
import os
import json
import logging
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import tempfile

from .services.ocr_processor import OCRProcessor
from .services.image_classifier import ImageClassifier
from .services.weather_service import WeatherService
from .services.recommender import ClothingRecommender
from .models import ClothingImage

import os
import logging

logger = logging.getLogger(__name__)

class HomeView(View):
    """处理主页显示"""
    def get(self, request):
        return render(request, 'ocr_app/home.html')

class BatchUploadView(View):
    def get(self, request):
        return render(request, 'ocr_app/upload.html')

    def post(self, request):
        print("\n=== Upload Processing Debug ===")
        clothing_images = request.FILES.getlist('clothing_images[]')
        label_images = request.FILES.getlist('label_images[]')
        
        print(f"Number of clothing images: {len(clothing_images)}")
        print(f"Number of label images: {len(label_images)}")
        
        if not clothing_images or not label_images:
            messages.error(request, 'Please upload both clothing and label images.')
            return redirect('batch_upload')
        
        if len(clothing_images) != len(label_images):
            messages.error(request, 'Number of clothing images and label images must match.')
            return redirect('batch_upload')
        
        success_count = 0
        failed_items = []
        
        # Initialize classifiers
        classifier = ImageClassifier()
        
        for i, (clothing_image, label_image) in enumerate(zip(clothing_images, label_images)):
            try:
                print(f"\nProcessing item {i+1}:")
                print(f"Clothing image: {clothing_image.name}")
                print(f"Label image: {label_image.name}")
                
                clothing = ClothingImage()
                clothing.image = clothing_image
                clothing.label_image = label_image
                
                # Classify the clothing image
                print("Starting image classification...")
                category_result = classifier.classify_image(clothing_image)
                category_name = category_result['category'] if isinstance(category_result, dict) else category_result
                clothing.category = category_name
                print(f"Classification result: {category_name}")
                
                # Process the label image with OCR
                print("Starting OCR processing...")
                ocr_result = process_label_image(label_image)
                
                if not ocr_result:
                    print(f"OCR processing failed for {label_image.name}")
                    # Still save the item even if OCR fails, so user can input text manually
                    clothing.recognized_text = ""
                    clothing.materials = []
                else:
                    # Store OCR recognized text
                    recognized_text = " ".join(ocr_result.get('recognized_texts', []))
                    print(f"Recognized text: {recognized_text}")
                    clothing.recognized_text = recognized_text
                    
                    # Store materials - 使用完整的材料信息
                    materials = ocr_result.get('materials', [])
                    print(f"Raw materials from OCR: {materials}")
                    
                    # 直接保存完整的材料信息（包括百分比）
                    clothing.materials = materials
                    print(f"Final materials to save: {clothing.materials}")
                
                print("Saving clothing record...")
                clothing.save()
                print(f"Successfully saved clothing record {clothing.id}")
                success_count += 1
                
            except Exception as e:
                print(f"Error processing item {i+1}: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                failed_items.append(label_image.name)
                continue
        
        print(f"\nProcessing complete. Success: {success_count}, Failed: {len(failed_items)}")
        
        # Show summary message
        if success_count > 0:
            messages.success(request, 'Upload successful.')
        else:
            messages.error(request, 'No items were successfully processed.')
        
        return redirect('clothing_list')

    def convert_to_jpg(self, image_file):
        """将图片转换为JPG格式"""
        try:
            # 打开图片
            img = Image.open(image_file)
            
            # 如果图片不是RGB模式，转换为RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 创建一个BytesIO对象来保存转换后的图片
            output = io.BytesIO()
            
            # 保存为JPEG格式
            img.save(output, format='JPEG', quality=95)
            output.seek(0)
            
            # 创建新的InMemoryUploadedFile
            converted = InMemoryUploadedFile(
                output,
                'ImageField',
                f"{os.path.splitext(image_file.name)[0]}.jpg",
                'image/jpeg',
                output.getbuffer().nbytes,
                None
            )
            
            return converted
        except Exception as e:
            logger.error(f"Error converting image: {str(e)}")
            raise e

from django.views.generic import DetailView
import logging


logger = logging.getLogger(__name__)

from ocr_app.models import ClothingImage

from django.shortcuts import render
from django.views import View
from ocr_app.models import ClothingImage
from ocr_app.services.weather_service import WeatherService
from ocr_app.services.recommender import ClothingRecommender

class QueryView(View):
    def get(self, request):
        return render(request, 'ocr_app/query.html')

    def post(self, request):
        city = request.POST.get('city', '').strip()
        if not city:
            return render(request, 'ocr_app/query.html', {'error': 'Please enter a city name'})

        weather_service = WeatherService(api_key=settings.WEATHER_API_KEY)
        weather_data = weather_service.get_weather_by_city(city)
        
        if not weather_data or 'error' in weather_data:
            return render(request, 'ocr_app/query.html', {'error': 'Unable to get weather information'})

        # Prepare weather data
        weather_info = {
            'temperature': weather_data['weather'].get('temperature'),
            'humidity': weather_data['weather'].get('humidity'),
            'condition': weather_data['weather'].get('condition')
        }

        # Get all clothing items
        clothing_items = ClothingImage.objects.all()
        
        # Initialize recommender
        recommender = ClothingRecommender()
        
        # Get recommendations
        recommendation_result = recommender.get_recommendation(clothing_items, weather_info)
        
        # Update the items to include image URLs
        for item in recommendation_result['items']:
            clothing = ClothingImage.objects.get(id=item['id'])
            item['image_url'] = clothing.image.url if clothing.image else None
            # 添加调试信息
            print(f"\nProcessing item {item['id']}:")
            print(f"Label image exists: {bool(clothing.label_image)}")
            if clothing.label_image:
                print(f"Label image URL: {clothing.label_image.url}")
            item['label_image'] = clothing.label_image.url if clothing.label_image else None
        
        # Prepare template context
        context = {
            'city': city,
            'weather': weather_info,
            'recommendations': recommendation_result['items'],
            'recommendation_text': recommendation_result['text']
        }
        
        # 添加调试信息
        print("\nRecommendation items:")
        for item in recommendation_result['items']:
            print(f"Item {item['id']}:")
            print(f"Image URL: {item.get('image_url')}")
            print(f"Label Image: {item.get('label_image')}")
        
        return render(request, 'ocr_app/query.html', context)

from django.views.generic import ListView
from ocr_app.models import ClothingImage

class ClothingListView(ListView):
    model = ClothingImage
    template_name = 'ocr_app/clothing_list.html'
    context_object_name = 'clothing_images'
    
    def get_queryset(self):
        queryset = ClothingImage.objects.all()
        print("\n=== ClothingListView Debug ===")
        print(f"Total records: {queryset.count()}")
        
        for item in queryset:
            print(f"\nRecord {item.id}:")
            print(f"Category: {item.category}")
            print(f"Materials: {item.materials}")
            print(f"OCR Text: {item.recognized_text}")
            print(f"Label Image: {'Yes' if item.label_image else 'No'}")
            print(f"Clothing Image: {'Yes' if item.image else 'No'}")
            print(f"OCR Text Type: {type(item.recognized_text)}")
            print(f"Materials Type: {type(item.materials)}")
            if item.materials:
                print(f"Materials Content: {item.materials}")
            if item.recognized_text:
                print(f"OCR Text Content: {item.recognized_text}")
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'MEDIA_URL': settings.MEDIA_URL,
            'MEDIA_ROOT': settings.MEDIA_ROOT,
            'debug_mode': settings.DEBUG,
        })
        print("\n=== Context Debug ===")
        print(f"Number of items in context: {len(context['clothing_images'])}")
        return context

from django.views.generic import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from ocr_app.models import ClothingImage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class ViewUploadData(View):
    """显示上传数据并支持删除操作"""
    def get(self, request):
        # 清理孤立的媒体文件
        self.cleanup_media_files()
        return render(request, 'ocr_app/view_upload_data.html', {
            'clothing_images': ClothingImage.objects.all()
        })

    def cleanup_media_files(self):
        """清理没有对应数据库记录的媒体文件"""
        media_root = settings.MEDIA_ROOT
        clothing_dir = os.path.join(media_root, 'clothing_images')
        label_dir = os.path.join(media_root, 'label_images')

        # 获取数据库中的所有文件名
        db_clothing_files = set(ClothingImage.objects.values_list('image', flat=True))
        db_label_files = set(ClothingImage.objects.values_list('label_image', flat=True))

        # 清理衣物图片目录
        if os.path.exists(clothing_dir):
            for file in os.listdir(clothing_dir):
                file_path = os.path.join('clothing_images', file)
                if file_path not in db_clothing_files:
                    os.remove(os.path.join(clothing_dir, file))
                    print(f"Removed orphaned file: {file}")

        # 清理标签图片目录
        if os.path.exists(label_dir):
            for file in os.listdir(label_dir):
                file_path = os.path.join('label_images', file)
                if file_path not in db_label_files:
                    os.remove(os.path.join(label_dir, file))
                    print(f"Removed orphaned file: {file}")

    def post(self, request):
        """处理删除请求"""
        try:
            data = json.loads(request.body)
            clothing_id = data.get('id')
            clothing = ClothingImage.objects.get(id=clothing_id)

            # 删除图片文件
            if clothing.image and os.path.exists(clothing.image.path):
                os.remove(clothing.image.path)
            if clothing.label_image and os.path.exists(clothing.label_image.path):
                os.remove(clothing.label_image.path)

            # 删除数据库记录
            clothing.delete()

            return JsonResponse({'success': True})
        except ClothingImage.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'Clothing item not found'
            })
        except Exception as e:
            print(f"Error deleting item: {str(e)}")  # 添加错误日志
            return JsonResponse({
                'success': False, 
                'message': str(e)
            })

def test_classifier(request):
    """测试分类器是否正常工作"""
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            classifier = ImageClassifier()
            result = classifier.classify_image(request.FILES['image'])
            print(f"Classification result: {result}")
            return JsonResponse({
                'success': True,
                'prediction': result
            })
        except Exception as e:
            print(f"Test classifier error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    return JsonResponse({
        'success': False,
        'error': 'No image provided'
    })

class ManualInputView(View):
    def get(self, request, clothing_id):
        try:
            clothing = ClothingImage.objects.get(id=clothing_id)
            return render(request, 'ocr_app/manual_input.html', {
                'clothing': clothing
            })
        except ClothingImage.DoesNotExist:
            return redirect('clothing_list')

    def post(self, request):
        try:
            data = json.loads(request.body)
            clothing_id = data.get('clothing_id')
            materials = data.get('materials', [])
            
            clothing = ClothingImage.objects.get(id=clothing_id)
            clothing.materials = materials
            clothing.save()
            
            print(f"Manually saved materials: {materials}")  # 添加调试信息
            
            return JsonResponse({'success': True})
        except ClothingImage.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'error': 'Clothing not found'
            })
        except Exception as e:
            print(f"Error in manual input: {str(e)}")  # 添加错误日志
            return JsonResponse({
                'success': False, 
                'error': str(e)
            })

def ensure_media_dirs():
    """确保媒体目录存在"""
    media_root = settings.MEDIA_ROOT
    clothing_dir = os.path.join(media_root, 'clothing_images')
    label_dir = os.path.join(media_root, 'label_images')
    
    for directory in [media_root, clothing_dir, label_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

class ImageCheckView(View):
    def get(self, request):
        images = ClothingImage.objects.all()
        media_root = settings.MEDIA_ROOT
        clothing_dir = os.path.join(media_root, 'clothing_images')
        label_dir = os.path.join(media_root, 'label_images')
        
        clothing_files = []
        label_files = []
        
        if os.path.exists(clothing_dir):
            clothing_files = os.listdir(clothing_dir)
        if os.path.exists(label_dir):
            label_files = os.listdir(label_dir)
            
        context = {
            'images': images,
            'clothing_files': clothing_files,
            'label_files': label_files,
            'media_root': media_root,
        }
        
        return render(request, 'ocr_app/image_check.html', context)

class ImportExistingImagesView(View):
    def get(self, request):
        media_root = settings.MEDIA_ROOT
        clothing_dir = os.path.join(media_root, 'clothing_images')
        label_dir = os.path.join(media_root, 'label_images')
        
        imported = 0
        errors = []
        
        # 获取所有衣物图片
        if os.path.exists(clothing_dir):
            for filename in os.listdir(clothing_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.heic')):
                    # 检查是否已存在记录
                    image_path = f'clothing_images/{filename}'
                    if not ClothingImage.objects.filter(image=image_path).exists():
                        try:
                            # 创建新记录
                            clothing = ClothingImage(image=image_path)
                            clothing.save()
                            imported += 1
                        except Exception as e:
                            errors.append(f"Error importing {filename}: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'imported': imported,
            'errors': errors
        })

@method_decorator(csrf_exempt, name='dispatch')
class SaveLabelTextView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            clothing_id = data.get('id')
            text = data.get('text', '')
            
            clothing = ClothingImage.objects.get(id=clothing_id)
            clothing.recognized_text = text
            clothing.save()
            
            return JsonResponse({'success': True})
        except ClothingImage.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Clothing not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })

@require_POST
def delete_clothing(request, clothing_id):
    try:
        print(f"\n=== Delete Clothing Debug ===")
        print(f"Attempting to delete clothing ID: {clothing_id}")
        
        clothing = ClothingImage.objects.get(id=clothing_id)
        
        # 安全删除图片文件
        if clothing.image:
            try:
                if os.path.exists(clothing.image.path):
                    print(f"Deleting clothing image: {clothing.image.path}")
                    os.remove(clothing.image.path)
                else:
                    print(f"Warning: Clothing image file not found: {clothing.image.path}")
            except Exception as e:
                print(f"Error deleting clothing image: {str(e)}")
        
        if clothing.label_image:
            try:
                if os.path.exists(clothing.label_image.path):
                    print(f"Deleting label image: {clothing.label_image.path}")
                    os.remove(clothing.label_image.path)
                else:
                    print(f"Warning: Label image file not found: {clothing.label_image.path}")
            except Exception as e:
                print(f"Error deleting label image: {str(e)}")
        
        # 删除数据库记录
        clothing.delete()
        print("Successfully deleted clothing record from database")
        
        return JsonResponse({
            'status': 'success',
            'message': '衣類が正常に削除されました。'
        })
    except ClothingImage.DoesNotExist:
        print(f"Error: Clothing item not found - ID: {clothing_id}")
        return JsonResponse({
            'status': 'error',
            'message': '衣類が見つかりませんでした。'
        }, status=404)
    except Exception as e:
        print(f"Unexpected error while deleting clothing: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def process_label_image(label_image):
    """Process the label image with OCR"""
    try:
        print(f"\nProcessing label image: {label_image.name}")
        
        # 使用 PIL 打开图像
        img = Image.open(label_image)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 使用临时文件
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_path = temp_file.name
            img.save(temp_path, 'JPEG', quality=95)
        
        try:
            # Process with OCR
            ocr_processor = OCRProcessor()
            result = ocr_processor.process_image(temp_path)
            
            if result and result.get('status') == 'success':
                print(f"Raw OCR Result: {result}")
                
                # 提取识别的文本
                recognized_texts = [text_info['text'] for text_info in result.get('detected_texts', [])]
                print(f"Extracted texts: {recognized_texts}")
                
                # 从文本中提取材料信息
                materials = []
                
                # 首先尝试从OCR结果的materials字段获取材料信息
                if 'materials' in result:
                    print(f"Processing materials from OCR result: {result['materials']}")
                    for material_data in result['materials']:
                        if isinstance(material_data, dict):
                            material_name = material_data.get('material', '')
                            if material_name and material_name not in materials:
                                materials.append(material_name)
                                print(f"Added material: {material_name}")
                
                # 如果OCR结果中没有足够的材料信息，从recognized_text中提取
                full_text = " ".join(recognized_texts)
                print(f"Attempting to extract materials from full text: {full_text}")
                
                # 使用OCRProcessor的extract_material_and_percentage方法提取材料
                ocr_processor = OCRProcessor()
                extracted_materials = ocr_processor.extract_material_and_percentage(full_text)
                
                # 合并提取到的材料
                for material in extracted_materials:
                    if material not in materials:
                        materials.append(material)
                        print(f"Added material from text analysis: {material}")
                
                print(f"Final materials list: {materials}")
                
                return {
                    'recognized_texts': recognized_texts,
                    'materials': materials
                }
            else:
                print("Warning: No text recognized in the label image")
                print(f"OCR Result: {result}")
                return None
                
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                print(f"Cleaned up temporary file: {temp_path}")
            
    except Exception as e:
        print(f"Error processing label image: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

@require_http_methods(["POST"])
def delete_all_clothing(request):
    """Delete all clothing items"""
    try:
        # 获取所有服装记录
        clothing_items = ClothingImage.objects.all()
        
        # 记录删除的数量
        deleted_count = clothing_items.count()
        
        # 删除所有记录
        clothing_items.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Successfully deleted {deleted_count} items',
            'deleted_count': deleted_count
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@require_http_methods(["POST"])
def save_materials(request):
    """Save materials for a clothing item"""
    try:
        data = json.loads(request.body)
        clothing_id = data.get('id')
        materials = data.get('materials', [])
        
        # 获取服装记录
        clothing = ClothingImage.objects.get(id=clothing_id)
        
        # 更新材料列表
        clothing.materials = materials
        clothing.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Materials updated successfully'
        })
    except ClothingImage.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Clothing item not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@require_http_methods(["POST"])
def update_category(request, clothing_id):
    """Update clothing category view function"""
    try:
        print("\n=== Category Update Debug ===")
        print(f"Received request for clothing ID: {clothing_id}")
        print(f"Request method: {request.method}")
        print(f"Request headers: {request.headers}")
        
        # Parse JSON data from request body
        data = json.loads(request.body)
        new_category = data.get('category')
        
        print(f"Parsed request data: {data}")
        print(f"New category: {new_category}")
        
        if not new_category:
            print("Error: No category specified")
            return JsonResponse({
                'status': 'error',
                'message': 'No category specified'
            }, status=400)
            
        # Get clothing object first to check if it exists
        try:
            clothing = ClothingImage.objects.get(id=clothing_id)
            print(f"Found clothing item: {clothing.id}")
            print(f"Current category: {clothing.category}")
        except ClothingImage.DoesNotExist:
            print(f"Error: Clothing item not found - ID: {clothing_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'Clothing item not found'
            }, status=404)
        
        # Validate category
        valid_categories = ['tshirt', 'pant', 'longsleeve', 'shortpant']
        if new_category not in valid_categories:
            print(f"Error: Invalid category - {new_category}")
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid category: {new_category}'
            }, status=400)
        
        # Update category
        clothing.category = new_category
        clothing.save()
        
        print(f"Successfully updated category to: {new_category}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Category updated successfully'
        })
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON data - {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)






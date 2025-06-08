from tensorflow.keras.applications.vgg16 import preprocess_input, VGG16
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
from PIL import Image
import io
import joblib
import os

class ImageClassifier:
    def __init__(self):
        try:
            # 初始化类别标签映射
            self.CATEGORY_LABELS = {
                'pant': 0,
                'shortpant': 1,
                'longsleeve': 2,
                'tshirt': 3
            }
            self.LABELS_TO_CATEGORY = {v: k for k, v in self.CATEGORY_LABELS.items()}
            
            # 加载预训练的VGG16模型
            base_model = VGG16(weights='imagenet', include_top=False, pooling='avg')
            self.feature_extractor = Model(inputs=base_model.input, outputs=base_model.output)
            print("Feature extractor loaded successfully")
            
            # 加载分类Pipeline
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, 'ml_models', 'image_classification_pipeline.pkl')
            print(f"Looking for model at: {model_path}")
            
            if not os.path.exists(model_path):
                print(f"Model file not found at {model_path}")
                # 尝试其他可能的路径
                alternate_path = os.path.join(base_dir, 'ml_models', 'image_classification_pipeline .pkl')
                if os.path.exists(alternate_path):
                    model_path = alternate_path
                    print(f"Found model at alternate path: {model_path}")
                else:
                    raise FileNotFoundError(f"Model file not found at {model_path} or {alternate_path}")
            
            self.pipeline = joblib.load(model_path)
            print("Classification pipeline loaded successfully")
            
        except Exception as e:
            print(f"Error initializing classifier: {str(e)}")
            raise e

    def preprocess_image(self, image_file, target_size=(224, 224)):
        """预处理图片并提取特征"""
        try:
            print("\n=== Image Preprocessing Debug ===")
            # 处理上传的文件
            if hasattr(image_file, 'read'):
                print("Processing uploaded file...")
                image_content = image_file.read()
                image = Image.open(io.BytesIO(image_content))
                # 重置文件指针，以便后续处理
                if hasattr(image_file, 'seek'):
                    image_file.seek(0)
            else:
                print("Processing file path...")
                image = Image.open(image_file)
            
            print(f"Original image size: {image.size}")
            print(f"Original image mode: {image.mode}")
            
            # 预处理图像
            image = image.resize(target_size)
            print(f"Resized to: {image.size}")
            
            image = image.convert('RGB')
            print("Converted to RGB")
            
            x = img_to_array(image)
            print(f"Converted to array shape: {x.shape}")
            
            x = np.expand_dims(x, axis=0)
            print(f"Expanded dimensions: {x.shape}")
            
            x = preprocess_input(x)
            print("Applied VGG16 preprocessing")
            
            # 提取特征
            print("Extracting features with VGG16...")
            features = self.feature_extractor.predict(x)
            print(f"Extracted features shape: {features.shape}")
            
            return features.flatten()
            
        except Exception as e:
            print(f"Preprocessing error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error details: {str(e)}")
            raise e

    def classify_image(self, image_file):
        """使用模型对图片进行分类"""
        try:
            print("\n=== Image Classification Debug ===")
            print(f"Processing image: {getattr(image_file, 'name', str(image_file))}")
            
            # 提取特征
            print("Extracting features...")
            features = self.preprocess_image(image_file)
            print(f"Features shape: {features.shape}")
            
            # 使用Pipeline进行预测
            print("Making prediction...")
            prediction = self.pipeline.predict([features])[0]
            confidence = max(self.pipeline.predict_proba([features])[0])
            
            # 获取类别名称
            category = self.LABELS_TO_CATEGORY.get(prediction, 'unknown')
            
            result = {
                'category': category,
                'confidence': float(confidence)
            }
            print(f"Classification result: {result}")
            
            return result
            
        except Exception as e:
            print(f"Classification error: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error details: {str(e)}")
            raise e 
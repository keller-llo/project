from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from ocr_app.services.image_classifier import ImageClassifier
import os
import numpy as np
from PIL import Image
import io

class ImageClassifierTests(TestCase):
    def setUp(self):
        """测试前的准备工作"""
        # 初始化分类器
        self.classifier = ImageClassifier()
        
        # 设置测试图片目录
        self.test_images_dir = r"C:\Users\chink\OneDrive\デスクトップ\testers"
        
        # 确保测试图片目录存在
        if not os.path.exists(self.test_images_dir):
            raise Exception(f"测试图片目录不存在: {self.test_images_dir}")
            
        # 获取测试图片列表
        self.test_images = [f for f in os.listdir(self.test_images_dir) 
                           if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not self.test_images:
            raise Exception("测试目录中没有找到图片文件")
            
        print(f"\n找到以下测试图片：")
        for img in self.test_images:
            print(f"- {img}")
        
    def test_classifier_initialization(self):
        """测试分类器是否正确初始化"""
        self.assertIsNotNone(self.classifier.feature_extractor)
        self.assertIsNotNone(self.classifier.pipeline)
        self.assertIsNotNone(self.classifier.CATEGORY_LABELS)
        print("\n可用的类别标签：", self.classifier.CATEGORY_LABELS)
        
    def test_classify_real_images(self):
        """测试实际图片的分类"""
        print("\n开始测试实际图片分类：")
        
        for image_name in self.test_images:
            # 从文件名中获取预期的类别
            expected_category = None
            if 'pant' in image_name.lower():
                expected_category = 'pant'
            elif 'short' in image_name.lower():
                expected_category = 'shortpant'
            elif 'long' in image_name.lower():
                expected_category = 'longsleeve'
            elif 'tshirt' in image_name.lower():
                expected_category = 'tshirt'
            
            image_path = os.path.join(self.test_images_dir, image_name)
            print(f"\n测试图片: {image_name}")
            if expected_category:
                print(f"预期类别: {expected_category}")
            
            # 读取图片文件
            with open(image_path, 'rb') as f:
                image_file = SimpleUploadedFile(
                    name=image_name,
                    content=f.read(),
                    content_type='image/jpeg'
                )
                
            # 测试分类
            result = self.classifier.classify_image(image_file)
            
            # 打印分类结果
            print(f"分类结果: {result['category']}")
            print(f"置信度: {result['confidence']:.2f}")
            
            # 验证结果格式
            self.assertIsInstance(result, dict)
            self.assertIn('category', result)
            self.assertIn('confidence', result)
            
            # 验证类别
            self.assertIn(result['category'], self.classifier.CATEGORY_LABELS.keys())
            
            # 验证置信度
            self.assertIsInstance(result['confidence'], float)
            self.assertTrue(0 <= result['confidence'] <= 1)
            
            # 如果有预期类别，验证分类结果
            if expected_category:
                self.assertEqual(result['category'], expected_category, 
                               f"图片 {image_name} 被错误分类为 {result['category']}")
            
    def test_invalid_image(self):
        """测试处理无效图片的情况"""
        print("\n测试无效图片处理：")
        
        # 测试空文件
        with self.assertRaises(Exception):
            self.classifier.classify_image(None)
            print("- 成功捕获空文件异常")
            
        # 测试损坏的图片文件
        invalid_image = SimpleUploadedFile(
            name='invalid.jpg',
            content=b'invalid image content',
            content_type='image/jpeg'
        )
        with self.assertRaises(Exception):
            self.classifier.classify_image(invalid_image)
            print("- 成功捕获损坏文件异常") 
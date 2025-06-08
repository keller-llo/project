from paddleocr import PaddleOCR, draw_ocr
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageOps, ExifTags
import io
import tempfile
import unicodedata
import re
from rapidfuzz import process, fuzz
import os

class OCRProcessor:
    def __init__(self):
        # 使用最新的PP-OCRv4模型进行初始化
        self.jp_ocr = PaddleOCR(
            use_angle_cls=True,
            lang='japan',
            # 使用默认路径，PaddleOCR会自动下载所需模型
            use_gpu=False,                # 是否使用GPU
            enable_mkldnn=True,           # 启用mkldnn加速
            total_process_num=4,          # 减少处理线程数以提高稳定性
            show_log=False,               # 不显示日志
            # OCR检测参数
            det_db_thresh=0.2,            # 降低文本检测阈值，提高召回率
            det_db_box_thresh=0.2,        # 降低文本框检测阈值
            det_db_unclip_ratio=2.0,      # 增加文本框扩张比例
            det_max_batch_num=10,         # 增加批处理数量
            rec_max_text_length=50,       # 增加最大文本长度
            drop_score=0.3                # 降低文本识别分数阈值
        )

        # 材料字典 - 添加英文材料名称
        self.material_mapping = {
            # 日文材料名称
            "綿": "cotton",
            "コットン": "cotton",  # 保持原始形式
            "ポリエステル": "polyester",
            "ナイロン": "nylon",
            "ウール": "wool",
            "毛": "wool",  # 添加"毛"作为"wool"的同义词
            "シルク": "silk",
            "アクリル": "acrylic",
            "レーヨン": "rayon",
            "麻": "hemp",
            "カシミヤ": "cashmere",
            "ポリウレタン": "polyurethane",
            "スパンデックス": "spandex",
            "モダール": "modal",
            "テンセル": "tencel",
            "ビスコース": "viscose",
            "アルパカ": "alpaca",
            "ラムウール": "lamb wool",
            "アンゴラ": "angora",
            "ヘンプ": "hemp",
            "コーデュロイ": "corduroy",
            "フリース": "fleece",
            "デニム": "denim",
            "エラスタン": "elastane",
            "ポリエチレン": "polyethylene",
            "リネン": "linen",
            "トリアセテート": "triacetate",
            # 英文材料名称
            "cotton": "cotton",
            "polyester": "polyester",
            "nylon": "nylon",
            "wool": "wool",
            "silk": "silk",
            "acrylic": "acrylic",
            "rayon": "rayon",
            "hemp": "hemp",
            "cashmere": "cashmere",
            "polyurethane": "polyurethane",
            "spandex": "spandex",
            "modal": "modal",
            "tencel": "tencel",
            "viscose": "viscose",
            "alpaca": "alpaca",
            "lamb wool": "lamb wool",
            "angora": "angora",
            "corduroy": "corduroy",
            "fleece": "fleece",
            "denim": "denim",
            "elastane": "elastane",
            "polyethylene": "polyethylene",
            "linen": "linen",
            "triacetate": "triacetate",
            "錦": "cotton"
        }

        # 创建所有材料的列表（包括日文和英文）
        self.material_dict = list(self.material_mapping.keys()) + list(set(self.material_mapping.values()))

    def normalize_text(self, text):
        """标准化文本"""
        text = unicodedata.normalize('NFKC', text)  # 转换为兼容性分解并重新组合
        text = re.sub(r'\s+', '', text)  # 移除多余空格
        text = text.replace('-', '')  # 移除连字符
        return text.lower()

    def normalize_material_name(self, text):
        """标准化材料名称"""
        # 移除所有空格、连字符和特殊字符
        text = re.sub(r'[\s\-・.。,、／]', '', text)
        # 移除百分比
        text = re.sub(r'\d+[%％]', '', text)
        return text

    def extract_material_and_percentage(self, text):
        """从文本中提取材料名称，使用字典匹配和模糊匹配进行纠正"""
        print(f"\nExtracting materials from: {text}")
        
        # 创建小写的材料映射字典（保持原始形式）
        lowercase_mapping = {}
        for k in self.material_mapping.keys():
            lowercase_mapping[k.lower()] = k  # 保持原始形式，不转换为英文
        
        materials_found = []
        
        # 将文本分成单词，使用更精确的分割规则
        pattern = r'[a-zA-Z]+|[ァ-ンー]+|[ぁ-ん]+|[一-龥]+|(?:[ァ-ンー]+[a-zA-Z]*)+|[ポナアレウシ][ァ-ンー]+|レーヨン|ポリエステル|ナイロン|ウール|シルク|コットン'
        words = re.findall(pattern, text)
        print(f"Split words: {words}")
        
        # 对分割后的单词进行合并检查
        i = 0
        while i < len(words) - 1:
            combined = words[i] + words[i + 1]
            # 检查合并后的词是否是材料名
            if combined.lower() in lowercase_mapping:
                words[i] = combined
                words.pop(i + 1)
            else:
                i += 1
        
        for word in words:
            # 标准化单词
            word = re.sub(r'[\s\-・.。,、／]', '', word)
            word = re.sub(r'\d+[%％]', '', word)
            word_lower = word.lower()  # 转换为小写进行比较
            print(f"Processing word: {word} (lowercase: {word_lower})")
            
            # 1. 首先尝试精确匹配
            if word_lower in lowercase_mapping:
                material = lowercase_mapping[word_lower]  # 使用原始形式
                if material not in materials_found:
                    materials_found.append(material)
                    print(f"Found material (exact match): {material}")
                continue
            
            # 2. 如果没有精确匹配，尝试模糊匹配
            matches = process.extract(word_lower, lowercase_mapping.keys(), scorer=fuzz.ratio, limit=3)
            print(f"Fuzzy matches for {word_lower}: {matches}")
            
            # 如果最佳匹配的分数超过阈值
            if matches and matches[0][1] >= 70:  # 降低阈值到70
                best_match = matches[0][0]  # 获取最佳匹配的材料名
                material = lowercase_mapping[best_match]  # 获取原始形式
                if material not in materials_found:
                    materials_found.append(material)
                    print(f"Found material (fuzzy match): {word} -> {material} (score: {matches[0][1]})")
        
        print(f"All materials found: {materials_found}")
        return materials_found

    def process_image(self, image_path):
        try:
            print("\n=== Starting Advanced Japanese OCR Processing ===")
            print(f"Processing image: {image_path}")
            
            # 打开图像
            img = Image.open(image_path)
            
            # 如果图像是RGBA模式，转换为RGB
            if img.mode == 'RGBA':
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                # 粘贴原图到白色背景上
                background.paste(img, mask=img.split()[3])  # 使用alpha通道作为mask
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 转换为numpy数组进行处理
            img_array = np.array(img)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # 检测是否为黑底白字
            mean_brightness = np.mean(gray)
            print(f"Mean brightness: {mean_brightness}")
            
            # 如果是深色背景，进行反转
            if mean_brightness < 128:
                print("Dark background detected, inverting image...")
                gray = cv2.bitwise_not(gray)
            
            # 使用高斯模糊减少噪声
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # 使用Otsu's二值化方法
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 应用形态学操作来清理噪声
            kernel = np.ones((2,2), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            
            # 再次检查是否需要反转
            if mean_brightness < 128:
                print("Ensuring white text on black background...")
                cleaned = cv2.bitwise_not(cleaned)
            
            # 转回PIL图像
            processed_img = Image.fromarray(cleaned)
            
            # 使用临时文件
            temp_path = None
            try:
                # 创建临时文件
                temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
                temp_path = temp_file.name
                temp_file.close()  # 立即关闭文件
                
                # 保存处理后的图像
                processed_img.save(temp_path, 'JPEG', quality=100)
                
                # 使用PP-OCRv4进行文本检测和识别
                jp_results = self.jp_ocr.ocr(temp_path)
                print(f"Raw OCR results: {jp_results}")
                
                if jp_results:
                    # 存储识别的文本
                    detected_texts = []
                    all_recognized_text = []
                    materials = []
                    
                    for result_group in jp_results:
                        if isinstance(result_group, list):
                            for line in result_group:
                                if isinstance(line, (list, tuple)) and len(line) >= 2:
                                    text_info = line[1]
                                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                        text = str(text_info[0])
                                        confidence = float(text_info[1])
                                    else:
                                        text = str(text_info)
                                        confidence = 0.5
                                        
                                    if text.strip():
                                        text = text.strip()
                                        all_recognized_text.append(text)
                                        detected_texts.append({
                                            'text': text,
                                            'confidence': confidence
                                        })
                                        
                                        # 检查是否是材料
                                        is_material, material_name = self.is_potential_material(text)
                                        if is_material and material_name and material_name not in materials:
                                            materials.append(material_name)
                                            print(f"Found material: {material_name} from text: {text}")
                
                    # 从完整文本中再次尝试提取材料
                    full_text = " ".join(all_recognized_text)
                    print(f"\nExtracting materials from: {full_text}")
                    extracted_materials = self.extract_material_and_percentage(full_text)
                    for material in extracted_materials:
                        if material not in materials:
                            materials.append(material)
                            print(f"Found additional material from full text: {material}")
                    
                    return {
                        'status': 'success',
                        'detected_texts': detected_texts,
                        'recognized_texts': all_recognized_text,
                        'materials': materials
                    }
                else:
                    print("No text detected in the image")
                    return {
                        'status': 'error',
                        'message': 'No text detected in the image',
                        'detected_texts': [],
                        'recognized_texts': [],
                        'materials': []
                    }
                    
            finally:
                # 清理临时文件
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                        print(f"Cleaned up temporary file: {temp_path}")
                    except Exception as e:
                        print(f"Warning: Failed to delete temporary file: {e}")
        
        except Exception as e:
            print(f"Processing error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': str(e),
                'detected_texts': [],
                'recognized_texts': [],
                'materials': []
            }

    def is_potential_material(self, text):
        """检查文本是否可能是材料名称"""
        # 首先标准化文本
        text = self.normalize_material_name(text)
        text_lower = text.lower()
        
        print(f"\nChecking potential material: {text_lower}")
        
        # 所有已知材料名称（日文和英文）
        all_materials = {
            # 日文材料名称
            'ポリエステル': 'ポリエステル',
            'ナイロン': 'ナイロン',
            'レーヨン': 'レーヨン',
            'アクリル': 'アクリル',
            'ポリウレタン': 'ポリウレタン',
            '綿': '綿',
            '錦': '綿',  # 添加直接映射
            'コットン': 'コットン',  # 保持原始形式
            'ウール': 'ウール',
            'シルク': 'シルク',
            '麻': '麻',
            'カシミヤ': 'カシミヤ',
            # 英文材料名称
            'polyester': 'polyester',
            'nylon': 'nylon',
            'rayon': 'rayon',
            'acrylic': 'acrylic',
            'polyurethane': 'polyurethane',
            'cotton': 'cotton',  # 保持原始形式
            'wool': 'wool',
            'silk': 'silk',
            'hemp': 'hemp',
            'cashmere': 'cashmere'
        }
        
        # 如果文本为空或只包含特殊字符，直接返回False
        if not text_lower or text_lower.strip('-_.,。、'):
            print(f"Empty or invalid text: {text_lower}")
            return False, None
        
        # 1. 首先进行模糊匹配
        matches = process.extract(text_lower, all_materials.keys(), scorer=fuzz.ratio, limit=3)
        print(f"Fuzzy matches: {matches}")
        
        # 降低匹配阈值以捕获更多可能的匹配
        if matches and matches[0][1] >= 70:
            matched_material = all_materials[matches[0][0]]
            print(f"Found fuzzy match: {text_lower} -> {matched_material} (score: {matches[0][1]})")
            return True, matched_material
            
        # 2. 如果模糊匹配失败，检查文本是否完全包含材料名称
        for material_name, normalized in all_materials.items():
            # 只有当文本长度接近材料名称长度时才考虑包含关系
            if (material_name.lower() in text_lower or text_lower in material_name.lower()) and \
               abs(len(text_lower) - len(material_name)) <= 2:
                print(f"Found material by containment: {normalized}")
                return True, normalized
        
        print(f"No material match found for: {text_lower}")
        return False, None
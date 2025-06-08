import logging

logger = logging.getLogger(__name__)

class ClothingRecommender:

    """
    Clothing Recommendation Service: Generates wearing suggestions based on materials and weather information
    """

    def __init__(self):
        self.material_translations = {
            'cotton': {
                'chinese': ['棉', '棉花'],
                'japanese': ['綿', 'コットン'],
                'english': ['cotton']
            },
            'linen': {
                'chinese': ['麻'],
                'japanese': ['麻', 'リネン'],
                'english': ['linen']
            },
            'silk': {
                'chinese': ['丝绸', '蚕丝'],
                'japanese': ['絹', 'シルク'],
                'english': ['silk', 'silk fiber']
            },
            'wool': {
                'chinese': ['羊毛', '羊绒'],
                'japanese': ['ウール'],
                'english': ['wool']
            },
            'cashmere': {
                'chinese': ['羊绒', '开司米羊绒'],
                'japanese': ['カシミヤ', 'カシミア'],
                'english': ['cashmere']
            },
            'polyester': {
                'chinese': ['涤纶', '聚酯纤维'],
                'japanese': ['ポリエステル'],
                'english': ['polyester']
            },
            'nylon': {
                'chinese': ['锦纶', '尼龙'],
                'japanese': ['ナイロン'],
                'english': ['nylon']
            },
            'acrylic': {
                'chinese': ['腈纶', '丙烯酸纤维'],
                'japanese': ['アクリル'],
                'english': ['acrylic']
            },
            'spandex': {
                'chinese': ['氨纶', '莱卡', '弹力纤维'],
                'japanese': ['スパンデックス', 'エラスタン'],
                'english': ['spandex', 'elastane', 'lycra']
            },
            'vinylon': {
                'chinese': ['维纶', '聚乙烯醇纤维'],
                'japanese': ['ビニロン'],
                'english': ['vinylon', 'polyvinyl alcohol fiber']
            },
            'polypropylene': {
                'chinese': ['丙纶', '聚丙烯纤维'],
                'japanese': ['ポリプロピレン'],
                'english': ['polypropylene']
            },
            'polyurethane': {
                'chinese': ['聚氨酯', '氨纶'],
                'japanese': ['ポリウレタン'],
                'english': ['polyurethane']
            },
            'rayon': {
                'chinese': ['人造丝', '再生纤维素纤维'],
                'japanese': ['レーヨン', '人絹'],
                'english': ['rayon', 'viscose']
            },
            'modal': {
                'chinese': ['莫代尔', '莫代尔纤维'],
                'japanese': ['モダール'],
                'english': ['modal']
            },
            'lyocell': {
                'chinese': ['天丝', '莱赛尔'],
                'japanese': ['テンセル'],
                'english': ['lyocell', 'tencel']
            },
            'bamboo fiber': {
                'chinese': ['竹纤维', '竹炭纤维'],
                'japanese': ['竹繊維', 'バンブーファイバー'],
                'english': ['bamboo fiber', 'bamboo charcoal fiber']
            },
            'acetate fiber': {
                'chinese': ['醋酸纤维', '醋酸酯'],
                'japanese': ['アセテート', 'ビスコース'],
                'english': ['acetate fiber', 'acetate']
            },
            'leather': {
                'chinese': ['皮革', '真皮', '牛皮'],
                'japanese': ['レザー', '革'],
                'english': ['leather', 'genuine leather']
            },
            'alpaca wool': {
                'chinese': ['羊驼毛', '羊驼绒'],
                'japanese': ['アルパカウール', 'アルパカ'],
                'english': ['alpaca wool', 'alpaca']
            },
            'velvet': {
                'chinese': ['天鹅绒', '丝绒', '绒布'],
                'japanese': ['ベルベット', 'ビロード'],
                'english': ['velvet']
            },
            'flannel': {
                'chinese': ['法兰绒', '绒布', '绒毛布'],
                'japanese': ['フランネル', 'ネル生地'],
                'english': ['flannel']
            },
            'corduroy': {
                'chinese': ['灯芯绒', '条绒'],
                'japanese': ['コーデュロイ', '畝物', '畝布'],
                'english': ['corduroy']
            },
            'denim': {
                'chinese': ['牛仔布', '丹宁布'],
                'japanese': ['デニム'],
                'english': ['denim']
            },
            # 添加原始字典中未包含的材料
            'ram wool': {
                'chinese': ['羊羔毛'],
                'japanese': ['ラムウール'],
                'english': ['ram wool']
            },
            'angora': {
                'chinese': ['兔毛', '安哥拉兔毛'],
                'japanese': ['アンゴラ'],
                'english': ['angora']
            },
            'hemp': {
                'chinese': ['麻'],
                'japanese': ['ヘンプ'],
                'english': ['hemp']
            },
            'fleece': {
                'chinese': ['抓绒', '摇粒绒'],
                'japanese': ['フリース'],
                'english': ['fleece']
            }
        }
        # Material translations for cross-reference
        self.material_properties = {
        'cotton': {
            'temp_range': (15, 30),
            'humidity_range': (30, 60),
            'weather_conditions': ['Clear', 'Clouds', 'Light Rain'],
            'properties': ['breathable', 'moisture-wicking', 'comfortable'],
            'description': 'Perfect for warm weather, cotton offers excellent breathability and moisture absorption.',
            'seasonal_use': ['spring', 'summer']
        },
        'linen': {
            'temp_range': (20, 35),
            'humidity_range': (30, 70),
            'weather_conditions': ['Clear', 'Clouds', 'Hot'],
            'properties': ['highly breathable', 'moisture-wicking', 'cooling'],
            'description': 'Ideal for hot weather, linen keeps you cool with superior breathability.',
            'seasonal_use': ['summer']
        },
        'silk': {
            'temp_range': (18, 25),
            'humidity_range': (40, 60),
            'weather_conditions': ['Clear', 'Clouds'],
            'properties': ['temperature-regulating', 'lightweight', 'smooth'],
            'description': 'A versatile luxury fiber that adapts to body temperature.',
            'seasonal_use': ['spring', 'summer', 'fall']
        },
        'wool': {
            'temp_range': (-10, 15),
            'humidity_range': (40, 70),
            'weather_conditions': ['Cold', 'Snow', 'Rain', 'Clear'],
            'properties': ['warm', 'water-resistant', 'insulating'],
            'description': 'Excellent for cold weather, providing warmth even when damp.',
            'seasonal_use': ['fall', 'winter']
        },
        'cashmere': {
            'temp_range': (-5, 15),
            'humidity_range': (30, 50),
            'weather_conditions': ['Clear', 'Cold', 'Snow'],
            'properties': ['extremely soft', 'warm', 'lightweight'],
            'description': 'Premium warm material perfect for cold weather while remaining lightweight.',
            'seasonal_use': ['fall', 'winter']
        },
        'polyester': {
            'temp_range': (10, 25),
            'humidity_range': (30, 80),
            'weather_conditions': ['Clear', 'Rain', 'Snow', 'Clouds'],
            'properties': ['durable', 'quick-drying', 'lightweight'],
            'description': 'Versatile synthetic fiber suitable for various weather conditions.',
            'seasonal_use': ['all seasons']
        },
        'nylon': {
            'temp_range': (5, 25),
            'humidity_range': (30, 80),
            'weather_conditions': ['Clear', 'Rain', 'Light Snow'],
            'properties': ['strong', 'water-resistant', 'lightweight'],
            'description': 'Durable synthetic material good for outdoor activities.',
            'seasonal_use': ['all seasons']
        },
        'spandex': {
            'temp_range': (15, 30),
            'humidity_range': (30, 70),
            'weather_conditions': ['Clear', 'Clouds', 'Indoor'],
            'properties': ['stretchy', 'form-fitting', 'moisture-wicking'],
            'description': 'Stretchy material perfect for athletic wear and comfort.',
            'seasonal_use': ['all seasons']
        },
        'modal': {
            'temp_range': (15, 30),
            'humidity_range': (40, 60),
            'weather_conditions': ['Clear', 'Clouds'],
            'properties': ['soft', 'breathable', 'eco-friendly'],
            'description': 'Sustainable fabric with excellent softness and breathability.',
            'seasonal_use': ['spring', 'summer']
        },
        'lyocell': {
            'temp_range': (15, 30),
            'humidity_range': (40, 60),
            'weather_conditions': ['Clear', 'Clouds', 'Light Rain'],
            'properties': ['eco-friendly', 'moisture-wicking', 'antibacterial'],
            'description': 'Sustainable material with excellent moisture management.',
            'seasonal_use': ['spring', 'summer', 'fall']
        },
        'bamboo fiber': {
            'temp_range': (15, 30),
            'humidity_range': (40, 70),
            'weather_conditions': ['Clear', 'Clouds', 'Humid'],
            'properties': ['antibacterial', 'moisture-wicking', 'eco-friendly'],
            'description': 'Natural fiber with antibacterial properties and good breathability.',
            'seasonal_use': ['spring', 'summer']
        },
        'leather': {
            'temp_range': (5, 20),
            'humidity_range': (40, 60),
            'weather_conditions': ['Clear', 'Light Rain', 'Cold'],
            'properties': ['durable', 'water-resistant', 'protective'],
            'description': 'Durable material that offers protection and style.',
            'seasonal_use': ['fall', 'winter']
        },
        'corduroy': {
            'temp_range': (5, 20),
            'humidity_range': (30, 60),
            'weather_conditions': ['Clear', 'Cold', 'Clouds'],
            'properties': ['warm', 'durable', 'comfortable'],
            'description': 'Warm and durable fabric perfect for cool weather.',
            'seasonal_use': ['fall', 'winter']
        },
        'denim': {
            'temp_range': (10, 25),
            'humidity_range': (30, 70),
            'weather_conditions': ['Clear', 'Clouds', 'Light Rain'],
            'properties': ['durable', 'versatile', 'protective'],
            'description': 'Sturdy and versatile material suitable for various conditions.',
            'seasonal_use': ['all seasons']
        },
        'flannel': {
            'temp_range': (0, 15),
            'humidity_range': (30, 60),
            'weather_conditions': ['Cold', 'Clear', 'Snow'],
            'properties': ['warm', 'soft', 'comfortable'],
            'description': 'Soft, warm fabric ideal for cold weather comfort.',
            'seasonal_use': ['fall', 'winter']
        },
        'velvet': {
            'temp_range': (5, 20),
            'humidity_range': (30, 50),
            'weather_conditions': ['Clear', 'Cold', 'Indoor'],
            'properties': ['warm', 'luxurious', 'soft'],
            'description': 'Luxurious fabric best suited for cooler temperatures.',
            'seasonal_use': ['fall', 'winter']
        },
        # 添加之前缺失的材料
        'ram wool': {
            'temp_range': (-5, 15),
            'humidity_range': (40, 60),
            'weather_conditions': ['Cold', 'Snow', 'Clear'],
            'properties': ['warm', 'soft', 'lightweight'],
            'description': 'Soft and warm wool from young sheep, perfect for cold weather.',
            'seasonal_use': ['fall', 'winter']
        },
        'angora': {
            'temp_range': (-3, 10),
            'humidity_range': (30, 50),
            'weather_conditions': ['Cold', 'Clear'],
            'properties': ['extremely soft', 'warm', 'fluffy'],
            'description': 'Luxuriously soft wool from Angora rabbits, providing exceptional warmth.',
            'seasonal_use': ['winter']
        },
        'hemp': {
            'temp_range': (15, 30),
            'humidity_range': (40, 70),
            'weather_conditions': ['Clear', 'Clouds', 'Mild'],
            'properties': ['durable', 'breathable', 'eco-friendly'],
            'description': 'Sustainable and strong natural fiber with excellent breathability.',
            'seasonal_use': ['spring', 'summer', 'fall']
        },
        'fleece': {
            'temp_range': (0, 15),
            'humidity_range': (30, 60),
            'weather_conditions': ['Cold', 'Clear', 'Snow'],
            'properties': ['warm', 'soft', 'lightweight'],
            'description': 'Synthetic fabric that provides excellent insulation and warmth.',
            'seasonal_use': ['fall', 'winter']
        },
        'alpaca wool': {
            'temp_range': (-5, 15),
            'humidity_range': (40, 60),
            'weather_conditions': ['Cold', 'Snow', 'Clear'],
            'properties': ['warmer than wool', 'soft', 'lightweight'],
            'description': 'Warmer and lighter than traditional wool, perfect for cold weather.',
            'seasonal_use': ['fall', 'winter']
        },
        'acrylic': {
            'temp_range': (10, 25),
            'humidity_range': (30, 70),
            'weather_conditions': ['Clouds', 'Light Rain', 'Clear', 'Indoor'],
            'properties': ['warm', 'lightweight', 'soft', 'quick-drying'],
            'description': 'Synthetic fiber with good insulation and versatility, suitable for various conditions.',
            'seasonal_use': ['fall', 'spring', 'early winter']
            }
        }

    def normalize_material_name(self, material, language):
        if not material:
            return None

            # 将材料转换为小写
        material = material.lower().strip()
        """Convert material names from different languages to standard English names"""
        if language == 'english':
            return material

        # Search through translations to find English equivalent
        for eng_name, translations in self.material_translations.items():
            if material in translations.get(language, []):
                return eng_name

        return material

    def get_material_properties(self, material, language='english'):
        """Get detailed properties for a specific material"""
        material_eng = self.normalize_material_name(material, language)
        return self.material_properties.get(material_eng, None)

    def get_recommendation(self, materials, weather_data):
        """Generate clothing recommendations based on weather"""
        temperature = weather_data.get('temperature', 20)
        humidity = weather_data.get('humidity', 50)
        condition = weather_data.get('condition', 'Clear')
        
        # Category display mapping
        category_display = {
            'tshirt': 'T-shirt',
            'pant': 'Pants',
            'longsleeve': 'Long Sleeve',
            'shortpant': 'Short Pants'
        }
        
        # Generate detailed recommendations based on temperature and weather conditions
        if temperature >= 30:
            recommendation_text = (
                f"Hot weather ({temperature}°C):\n"
                "Recommended clothing:\n"
                "- Loose, lightweight cotton T-shirts\n"
                "- Breathable shorts\n"
                "Tips:\n"
                "- Choose light-colored clothing\n"
                "- Avoid tight-fitting clothes\n"
                "- Consider wearing a sun hat"
            )
            recommended_categories = ['tshirt', 'shortpant']
            
        elif 25 <= temperature < 30:
            if humidity > 70:
                recommendation_text = (
                    f"Humid and warm ({temperature}°C, Humidity {humidity}%):\n"
                    "Recommended clothing:\n"
                    "- Moisture-wicking short-sleeve T-shirts\n"
                    "- Loose-fitting shorts\n"
                    "Material recommendations:\n"
                    "- Prefer cotton and linen fabrics\n"
                    "- Avoid non-breathable synthetic materials"
                )
            else:
                recommendation_text = (
                    f"Warm weather ({temperature}°C):\n"
                    "Recommended clothing:\n"
                    "- Comfortable short-sleeve T-shirts\n"
                    "- Casual shorts\n"
                    "- Consider bringing a light jacket"
                )
            recommended_categories = ['tshirt', 'shortpant']
            
        elif 20 <= temperature < 25:
            if condition in ['Rain', 'Drizzle']:
                recommendation_text = (
                    f"Mild with rain ({temperature}°C):\n"
                    "Recommended clothing:\n"
                    "- Long-sleeve shirts or T-shirts\n"
                    "- Long pants\n"
                    "Material recommendations:\n"
                    "- Choose water-resistant or quick-drying fabrics\n"
                    "- Avoid easily discolored clothing"
                )
                recommended_categories = ['longsleeve', 'pant']
            else:
                recommendation_text = (
                    f"Pleasant weather ({temperature}°C):\n"
                    "Recommended clothing:\n"
                    "- Long-sleeve T-shirts or shirts\n"
                    "- Choice of long pants or shorts\n"
                    "Tips:\n"
                    "- Bring a light jacket\n"
                    "- Adjust based on activities"
                )
                recommended_categories = ['longsleeve', 'pant', 'shortpant']
                
        elif 15 <= temperature < 20:
            recommendation_text = (
                f"Cool weather ({temperature}°C):\n"
                "Recommended clothing:\n"
                "- Long-sleeve shirts or sweaters\n"
                "- Long pants\n"
                "Tips:\n"
                "- Consider a light coat\n"
                "- Jeans or casual pants recommended"
            )
            recommended_categories = ['longsleeve', 'pant']
            
        elif 10 <= temperature < 15:
            recommendation_text = (
                f"Getting cold ({temperature}°C):\n"
                "Recommended clothing:\n"
                "- Warm long-sleeve tops\n"
                "- Thicker pants\n"
                "Tips:\n"
                "- Layer with a light sweater\n"
                "- Consider thermal underwear"
            )
            recommended_categories = ['longsleeve', 'pant']
            
        else:  # temperature < 10
            recommendation_text = (
                f"Cold weather ({temperature}°C):\n"
                "Recommended clothing:\n"
                "- Thermal underwear\n"
                "- Sweater or warm top\n"
                "- Insulated pants\n"
                "Tips:\n"
                "- Wear thermal base layers\n"
                "- Choose wool, down, or other warm materials\n"
                "- Pay attention to keeping neck and other exposed areas warm"
            )
            recommended_categories = ['longsleeve', 'pant']

        # Filter suitable clothing from database
        recommended_items = []
        for item in materials:
            if item.category in recommended_categories:
                recommendation = {
                    'id': item.id,
                    'image_url': item.image.url if item.image else None,
                    'label_image': item.label_image.url if item.label_image else None,
                    'category': category_display.get(item.category, item.category),
                    'materials': item.materials,
                    'recognized_text': item.recognized_text if hasattr(item, 'recognized_text') else None
                }
                recommended_items.append(recommendation)
                
        return {
            'items': recommended_items,
            'text': recommendation_text,
            'temperature': temperature,
            'humidity': humidity,
            'condition': condition
        }


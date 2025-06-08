from pathlib import Path
import pickle
import logging

def test_model_loading():
    """测试模型加载"""
    try:
        model_path = Path(__file__).parent / 'ml_models' / 'image_classification_pipeline.pkl'
        print(f"Testing model loading from: {model_path}")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
            
        print("Model loaded successfully!")
        print(f"Model type: {type(model)}")
        return True
        
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

if __name__ == "__main__":
    test_model_loading() 
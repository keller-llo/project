from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import joblib
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def create_sample_data():
    """创建示例训练数据"""
    n_samples = 100
    n_features = 224 * 224 * 3  # 对应图片大小和RGB通道
    
    X = np.random.rand(n_samples, n_features)
    y = np.random.choice(['longsleeve', 'shirt', 'shortpant', 'pant'], n_samples)
    
    return X, y

def train_and_save_model():
    """训练并保存新的模型"""
    try:
        # 创建示例数据
        X, y = create_sample_data()
        
        # 创建分类pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', SVC(kernel='linear', probability=True))
        ])
        
        # 训练模型
        print("Training model...")
        pipeline.fit(X, y)
        
        # 确保目录存在
        model_dir = Path(__file__).parent / 'ml_models'
        model_dir.mkdir(exist_ok=True)
        
        # 使用joblib保存模型
        model_path = model_dir / 'clothing_classifier.joblib'
        print(f"Saving model to {model_path}")
        joblib.dump(pipeline, model_path)
        print("Model saved successfully!")
        
        # 测试加载
        print("Testing model loading...")
        loaded_model = joblib.load(model_path)
        print("Model loaded successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    train_and_save_model() 
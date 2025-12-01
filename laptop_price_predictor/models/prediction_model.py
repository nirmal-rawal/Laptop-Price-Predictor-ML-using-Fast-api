import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any
import asyncio
from functools import lru_cache

from laptop_price_predictor.core.config import settings
from laptop_price_predictor.core.logger import logger


class LaptopPriceModel:
    """Machine learning model for laptop price prediction"""
    
    def __init__(self):
        self.model = None
        self.df = None
        self.is_loaded = False
        self.settings = settings
    
    async def load_model(self):
        """Load model and data (lazy initialization)"""
        if not self.is_loaded:
            try:
                model_path = Path(self.settings.model_path)
                data_path = Path(self.settings.data_path)
                
                logger.info(f"Loading model from: {model_path}")
                logger.info(f"Loading data from: {data_path}")
                
                if not model_path.exists():
                    raise FileNotFoundError(f"Model file not found: {model_path}")
                if not data_path.exists():
                    raise FileNotFoundError(f"Data file not found: {data_path}")
                
                # Load model and data in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                self.model, self.df = await asyncio.gather(
                    loop.run_in_executor(None, self._load_pickle, model_path),
                    loop.run_in_executor(None, self._load_pickle, data_path)
                )
                
                self.is_loaded = True
                logger.info("Model and data loaded successfully")
                
            except Exception as e:
                logger.error(f"Error loading model: {e}", exc_info=True)
                raise
    
    def _load_pickle(self, file_path: Path):
        """Load pickle file"""
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    
    def preprocess_features(self, features: Dict[str, Any]) -> pd.DataFrame:
        """Preprocess input features for prediction"""
        feature_dict = {
            'Company': [features['company']],
            'TypeName': [features['type_name']],
            'Ram': [features['ram']],
            'Weight': [features['weight']],
            'Touchscreen': [features['touchscreen']],
            'Ips': [features['ips']],
            'ppi': [features['ppi']],
            'Cpu brand': [features['cpu_brand']],
            'HDD': [features['hdd']],
            'SSD': [features['ssd']],
            'Gpu brand': [features['gpu_brand']],
            'os': [features['os']]
        }
        
        return pd.DataFrame(feature_dict)
    
    async def predict(self, features: Dict[str, Any]) -> float:
        """Make price prediction"""
        if not self.is_loaded:
            await self.load_model()
        
        try:
            input_df = self.preprocess_features(features)
            
            # Run prediction in thread pool
            loop = asyncio.get_event_loop()
            raw_prediction = await loop.run_in_executor(
                None, self.model.predict, input_df
            )
            
            prediction_value = self._process_prediction(raw_prediction)
            return prediction_value
            
        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            raise
    
    def _process_prediction(self, raw_prediction) -> float:
        """Process raw prediction into final price"""
        if isinstance(raw_prediction, (np.ndarray, list)):
            prediction_value = float(raw_prediction[0])
        else:
            prediction_value = float(raw_prediction)
        
        # Apply transformations if needed
        if prediction_value < 100:
            prediction_value = np.exp(prediction_value)
        
        if prediction_value < 1000:
            prediction_value = prediction_value * 1000
        
        return max(1000, min(prediction_value, 500000))
    
    def format_price(self, price: float) -> str:
        """Format price as Indian Rupees"""
        try:
            if price < 100:
                price = price * 1000
            return f"₹{price:,.2f}"
        except Exception as e:
            logger.error(f"Price formatting error: {e}")
            return f"₹{price:.2f}"


# Global prediction model instance
prediction_model = LaptopPriceModel()
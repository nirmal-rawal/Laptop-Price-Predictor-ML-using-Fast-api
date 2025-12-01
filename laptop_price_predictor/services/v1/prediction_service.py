import uuid
from typing import Dict
from datetime import datetime, timezone
import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np

from laptop_price_predictor.models.user_input_schema_model import LaptopFeatures, PredictionResponse, PredictionRecord
from laptop_price_predictor.models.prediction_model import prediction_model
from laptop_price_predictor.repositories.prediction_repository import prediction_repository
from laptop_price_predictor.utils.cache import prediction_cache
from laptop_price_predictor.core.logger import logger


class PredictionService:
    """Service layer for prediction operations"""
    
    def __init__(self):
        self.prediction_repository = prediction_repository
        self.prediction_model = prediction_model
        self.cache = prediction_cache
        self._executor = ThreadPoolExecutor(max_workers=1)
        self.is_model_loaded = False
    
    async def initialize_model(self):
        """Eager initialization of model"""
        await self.prediction_model.load_model()
        self.is_model_loaded = True
        logger.info("Prediction service initialized")
    
    async def predict_price(self, features: LaptopFeatures) -> PredictionResponse:
        """Predict laptop price with feature validation"""
        # Create a cache key from features
        cache_key = self._create_cache_key(features)
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info("Returning cached prediction")
            return cached_result
        
        feature_dict = features.model_dump()
        logger.info(f"Making prediction for features: {feature_dict}")
        
        # Run prediction in thread pool executor
        loop = asyncio.get_event_loop()
        predicted_price = await loop.run_in_executor(
            self._executor, 
            lambda: asyncio.run(self.prediction_model.predict(feature_dict))
        )
        
        # Apply price correction
        predicted_price = self._apply_price_correction(predicted_price)
        prediction_id = str(uuid.uuid4())
        price_formatted = self.prediction_model.format_price(predicted_price)
        
        response = PredictionResponse(
            prediction_id=prediction_id,
            predicted_price=predicted_price,
            price_formatted=price_formatted,
            features=features
        )
        
        # Cache the result
        self.cache.set(cache_key, response)
        
        # Save to database (fire and forget)
        asyncio.create_task(self._save_prediction_record(feature_dict, response))
        
        return response
    
    async def get_prediction_history(self, limit: int = 100) -> list:
        """Get prediction history"""
        return await self.prediction_repository.get_all_predictions(limit)
    
    async def get_prediction_by_id(self, prediction_id: str):
        """Get prediction by ID"""
        prediction = await self.prediction_repository.get_prediction(prediction_id)
        return prediction
    
    def _create_cache_key(self, features: LaptopFeatures) -> str:
        """Create cache key from features"""
        feature_dict = features.model()
        return f"prediction:{hash(frozenset(feature_dict.items()))}"
    
    def _apply_price_correction(self, price: float) -> float:
        """Apply correction to price if it seems unreasonable"""
        original_price = price
        
        if price < 100:
            price = np.exp(price)
            logger.info(f"Applied exp() transformation: {original_price} -> {price}")
        
        if price < 10000:
            price = price * 100
            logger.info(f"Applied scaling: {original_price} -> {price}")
        
        price = max(10000, min(price, 500000))
        
        if original_price != price:
            logger.info(f"Price corrected: {original_price} -> {price}")
        
        return price
    
    async def _save_prediction_record(self, features: Dict, response: PredictionResponse):
        """Save prediction record to database"""
        try:
            record = PredictionRecord(
                input_features=features,
                output_prediction=response.predicted_price,
                price_formatted=response.price_formatted,
                timestamp=datetime.now(timezone.utc).isoformat(),
                prediction_id=response.prediction_id
            )
            
            await self.prediction_repository.save_prediction(record)
            logger.info(f"Prediction saved with ID: {response.prediction_id}")
            
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
    
    async def clear_cache(self):
        """Clear prediction cache"""
        self.cache.clear()
        logger.info("Prediction cache cleared")


# Global prediction service instance
prediction_service = PredictionService()
from typing import List, Optional, Dict

from laptop_price_predictor.models.user_input_schema_model import PredictionRecord
from laptop_price_predictor.repositories.mongodb_curd_operations_repository import mongodb_repository


class PredictionRepository:
    """Prediction repository for database operations"""
    
    def __init__(self):
        self.mongodb_repo = mongodb_repository
    
    async def save_prediction(self, prediction_record: PredictionRecord) -> str:
        """Save prediction record to database"""
        return self.mongodb_repo.insert_prediction(prediction_record.model_dump())
     
    async def get_prediction(self, prediction_id: str) -> Optional[PredictionRecord]:
        """Get prediction by ID"""
        record = self.mongodb_repo.find_prediction_by_id(prediction_id)
        return PredictionRecord(**record) if record else None
    
    async def get_all_predictions(self, limit: int = 100, skip: int = 0) -> List[PredictionRecord]:
        """Get all predictions with pagination"""
        records = self.mongodb_repo.find_all_predictions(limit, skip)
        return [PredictionRecord(**record) for record in records]
    
    async def get_predictions_by_company(self, company: str, limit: int = 50) -> List[PredictionRecord]:
        """Get predictions by company"""
        records = self.mongodb_repo.find_predictions_by_company(company, limit)
        return [PredictionRecord(**record) for record in records]
    
    async def get_predictions_by_price_range(self, min_price: float, max_price: float, limit: int = 50) -> List[PredictionRecord]:
        """Get predictions by price range"""
        records = self.mongodb_repo.find_predictions_by_price_range(min_price, max_price, limit)
        return [PredictionRecord(**record) for record in records]
    
    async def update_prediction(self, prediction_id: str, update_data: Dict) -> bool:
        """Update prediction record"""
        return self.mongodb_repo.update_prediction(prediction_id, update_data)
    
    async def delete_prediction(self, prediction_id: str) -> bool:
        """Delete prediction by ID"""
        return self.mongodb_repo.delete_prediction(prediction_id)
    
    async def delete_predictions_by_company(self, company: str) -> int:
        """Delete all predictions for a company"""
        return self.mongodb_repo.delete_predictions_by_company(company)
    
    async def get_predictions_count(self) -> int:
        """Get total count of predictions"""
        return self.mongodb_repo.get_predictions_count()
    
    async def get_companies_stats(self) -> List[Dict]:
        """Get statistics by company"""
        return self.mongodb_repo.get_companies_stats()
    
    async def get_price_statistics(self) -> Dict:
        """Get overall price statistics"""
        return self.mongodb_repo.get_price_statistics()


# Global prediction repository instance
prediction_repository = PredictionRepository()
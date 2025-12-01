from typing import List, Dict, Optional
import uuid
from datetime import datetime, timezone
from bson import ObjectId

from laptop_price_predictor.core.mongodb_config import mongodb_config
from laptop_price_predictor.core.config import settings
from laptop_price_predictor.core.logger import logger


class MongoDBRepository:
    """MongoDB repository for database operations"""
    
    def __init__(self):
        self.mongodb_config = mongodb_config
        self.settings = settings
        self.collection = None
    
    def _get_collection(self):
        """Get collection (lazy initialization)"""
        if self.collection is None:
            database = self.mongodb_config.get_database()
            self.collection = database[self.settings.mongodb_collection_name]
        return self.collection
    
    # CREATE Operations
    def insert_prediction(self, prediction_data: Dict) -> str:
        """Insert prediction record"""
        collection = self._get_collection()
        prediction_id = str(uuid.uuid4())
        prediction_data['prediction_id'] = prediction_id
        prediction_data['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        collection.insert_one(prediction_data)
        return prediction_id
    
    def insert_many_predictions(self, predictions_data: List[Dict]) -> List[str]:
        """Insert multiple prediction records"""
        collection = self._get_collection()
        prediction_ids = []
        
        for data in predictions_data:
            prediction_id = str(uuid.uuid4())
            data['prediction_id'] = prediction_id
            data['timestamp'] = datetime.now(timezone.utc).isoformat()
            prediction_ids.append(prediction_id)
        
        collection.insert_many(predictions_data)
        return prediction_ids
    
    # READ Operations
    def find_prediction_by_id(self, prediction_id: str) -> Optional[Dict]:
        """Find prediction by ID"""
        collection = self._get_collection()
        record = collection.find_one({"prediction_id": prediction_id})
        return self._convert_objectid_to_str(record) if record else None
    
    def find_all_predictions(self, limit: int = 100, skip: int = 0) -> List[Dict]:
        """Find all predictions with pagination"""
        collection = self._get_collection()  
        cursor = collection.find().sort('timestamp', -1).skip(skip).limit(limit)
        return [self._convert_objectid_to_str(record) for record in cursor]
    
    def find_predictions_by_company(self, company: str, limit: int = 50) -> List[Dict]:
        """Find predictions by company"""
        collection = self._get_collection()
        cursor = collection.find(
            {"input_features.company": company}
        ).sort('timestamp', -1).limit(limit)
        return [self._convert_objectid_to_str(record) for record in cursor]
    
    def find_predictions_by_price_range(self, min_price: float, max_price: float, limit: int = 50) -> List[Dict]:
        """Find predictions by price range"""
        collection = self._get_collection()
        cursor = collection.find({
            "output_prediction": {"$gte": min_price, "$lte": max_price}
        }).sort('timestamp', -1).limit(limit)
        return [self._convert_objectid_to_str(record) for record in cursor]
    
    # UPDATE Operations
    def update_prediction(self, prediction_id: str, update_data: Dict) -> bool:
        """Update prediction record"""
        collection = self._get_collection()
        update_data.pop('prediction_id', None)
        update_data.pop('_id', None)
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        result = collection.update_one(
            {"prediction_id": prediction_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    # DELETE Operations
    def delete_prediction(self, prediction_id: str) -> bool:
        """Delete prediction by ID"""
        collection = self._get_collection()
        result = collection.delete_one({"prediction_id": prediction_id})
        return result.deleted_count > 0
    
    def delete_predictions_by_company(self, company: str) -> int:
        """Delete all predictions for a company"""
        collection = self._get_collection()
        result = collection.delete_many({"input_features.company": company})
        return result.deleted_count
    
    # STATISTICS Operations
    def get_predictions_count(self) -> int:
        """Get total count of predictions"""
        collection = self._get_collection()
        return collection.count_documents({})
    
    def get_companies_stats(self) -> List[Dict]:
        """Get statistics by company"""
        collection = self._get_collection()
        pipeline = [
            {
                "$group": {
                    "_id": "$input_features.company",
                    "count": {"$sum": 1},
                    "avg_price": {"$avg": "$output_prediction"},
                    "min_price": {"$min": "$output_prediction"},
                    "max_price": {"$max": "$output_prediction"}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        return list(collection.aggregate(pipeline))
    
    def get_price_statistics(self) -> Dict:
        """Get overall price statistics"""
        collection = self._get_collection()
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_predictions": {"$sum": 1},
                    "avg_price": {"$avg": "$output_prediction"},
                    "min_price": {"$min": "$output_prediction"},
                    "max_price": {"$max": "$output_prediction"},
                    "std_dev_price": {"$stdDevPop": "$output_prediction"}
                }
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        return result[0] if result else {}
    
    # Helper method
    def _convert_objectid_to_str(self, record: Dict) -> Dict:
        """Convert ObjectId to string for JSON serialization"""
        if '_id' in record and isinstance(record['_id'], ObjectId):
            record['_id'] = str(record['_id'])
        return record


# Global MongoDB repository instance
mongodb_repository = MongoDBRepository()
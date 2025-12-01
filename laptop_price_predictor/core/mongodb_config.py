from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional

from laptop_price_predictor.core.config import settings
from laptop_price_predictor.core.logger import logger


class MongoDBConfig:
    """MongoDB configuration and connection management"""
    
    _client: Optional[MongoClient] = None
    _database: Optional[Database] = None
    
    def __init__(self):
        self.settings = settings
    
    def get_database(self) -> Database:
        """Get database connection"""
        if self._database is None:
            self._initialize_connection()
        return self._database
    
    def _initialize_connection(self):
        """Initialize MongoDB connection"""
        try:
            self._client = MongoClient(self.settings.mongodb_url)
            self._database = self._client[self.settings.mongodb_db_name]
            # Test connection
            self._database.command('ping')
            logger.info("MongoDB connection established successfully")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("MongoDB connection closed")


# Global MongoDB config instance
mongodb_config = MongoDBConfig()
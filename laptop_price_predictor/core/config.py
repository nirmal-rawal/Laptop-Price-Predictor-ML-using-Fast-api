from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings configuration"""
    
    # MongoDB Configuration
    mongodb_url: str = Field(default="mongodb://localhost:27017")
    mongodb_db_name: str = Field(default="laptop_price_predictor")
    mongodb_collection_name: str = Field(default="predictions")
    
    # Application Configuration
    app_env: str = Field(default="development")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    
    # Model Configuration
    model_path: str = Field(default="ml_model/linear_regression.pkl")
    data_path: str = Field(default="ml_model/df.pkl")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        protected_namespaces = ('settings_',)


def get_settings() -> Settings:
    """Get settings instance"""
    settings = Settings()
    
    # Resolve relative paths using pathlib
    project_root = Path(__file__).parent.parent.parent
    model_path = Path(settings.model_path)
    data_path = Path(settings.data_path)
    
    if not model_path.is_absolute():
        settings.model_path = str(project_root / model_path)
    
    if not data_path.is_absolute():
        settings.data_path = str(project_root / data_path)
    
    return settings


# Global settings instance
settings = get_settings()   
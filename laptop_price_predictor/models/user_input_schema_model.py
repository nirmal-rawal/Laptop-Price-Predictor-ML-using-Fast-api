from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, List, Annotated
from enum import Enum


class Company(str, Enum):
    APPLE = "Apple"
    HP = "HP"
    ACER = "Acer"
    ASUS = "Asus"
    DELL = "Dell"
    LENOVO = "Lenovo"
    MSI = "MSI"
    TOSHIBA = "Toshiba"
    SAMSUNG = "Samsung"
    OTHER = "Other"


class TypeName(str, Enum):
    ULTRABOOK = "Ultrabook"
    NOTEBOOK = "Notebook"
    NETBOOK = "Netbook"
    GAMING = "Gaming"
    TWO_IN_ONE = "2 in 1 Convertible"
    WORKSTATION = "Workstation"


class CpuBrand(str, Enum):
    INTEL_CORE_I3 = "Intel Core i3"
    INTEL_CORE_I5 = "Intel Core i5"
    INTEL_CORE_I7 = "Intel Core i7"
    AMD_PROCESSOR = "AMD Processor"
    OTHER_INTEL = "Other Intel Processor"


class GpuBrand(str, Enum):
    INTEL = "Intel"
    AMD = "AMD"
    NVIDIA = "Nvidia"


class OS(str, Enum):
    MAC = "Mac"
    WINDOWS = "Windows"
    LINUX = "Others/No OS/Linux"


class LaptopFeatures(BaseModel):
    """Pydantic model for laptop feature input"""
    
    company: Annotated[Company, Field(..., description="Laptop manufacturer")]
    type_name: Annotated[TypeName, Field(..., description="Laptop type")]
    ram: Annotated[int, Field(..., ge=2, le=64, description="RAM in GB")]
    weight: Annotated[float, Field(..., ge=0.5, le=5.0, description="Weight in kg")]
    touchscreen: Annotated[int, Field(0, ge=0, le=1, description="Touchscreen (0=No, 1=Yes)")]
    ips: Annotated[int, Field(0, ge=0, le=1, description="IPS display (0=No, 1=Yes)")]
    ppi: Annotated[float, Field(..., ge=90, le=400, description="Pixels per inch")]
    cpu_brand: Annotated[CpuBrand, Field(..., description="CPU brand and model")]
    hdd: Annotated[int, Field(0, ge=0, le=2000, description="HDD storage in GB")]
    ssd: Annotated[int, Field(0, ge=0, le=2048, description="SSD storage in GB")]
    gpu_brand: Annotated[GpuBrand, Field(..., description="GPU brand")]
    os: Annotated[OS, Field(..., description="Operating system")]
    
    @validator('ram')
    def validate_ram(cls, v):
        valid_ram = [2, 4, 6, 8, 12, 16, 24, 32, 64]
        if v not in valid_ram:
            raise ValueError(f"RAM must be one of {valid_ram}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "company": "Dell",
                "type_name": "Notebook",
                "ram": 8,
                "weight": 2.0,
                "touchscreen": 0,
                "ips": 1,
                "ppi": 141.21,
                "cpu_brand": "Intel Core i5",
                "hdd": 0,
                "ssd": 256,
                "gpu_brand": "Intel",
                "os": "Windows"
            }
        }


class PredictionResponse(BaseModel):
    """Pydantic model for prediction response"""
    
    prediction_id: str
    predicted_price: float
    price_formatted: str
    confidence: Optional[float] = None
    features: LaptopFeatures
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction_id": "12345",
                "predicted_price": 55578.05,
                "price_formatted": "₹55,578.05",
                "confidence": 0.85,
                "features": {
                    "company": "Dell",
                    "type_name": "Notebook",
                    "ram": 8,
                    "weight": 2.0,
                    "touchscreen": 0,
                    "ips": 1,
                    "ppi": 141.21,
                    "cpu_brand": "Intel Core i5",
                    "hdd": 0,
                    "ssd": 256,
                    "gpu_brand": "Intel",
                    "os": "Windows"
                }
            }
        }


class PredictionRecord(BaseModel):
    """Pydantic model for MongoDB prediction record"""
    
    input_features: dict
    output_prediction: float
    price_formatted: str
    timestamp: str
    prediction_id: str
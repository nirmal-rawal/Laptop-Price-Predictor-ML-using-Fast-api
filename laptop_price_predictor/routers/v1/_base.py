from fastapi import APIRouter

from laptop_price_predictor.routers.v1.predictions import router as prediction_router
from laptop_price_predictor.routers.v1.crud_operations import router as crud_router

# Create base router
base_router = APIRouter(prefix='/v1')

# Include all routers with proper tags
base_router.include_router(router=prediction_router, prefix="/prediction", tags=['api'])
base_router.include_router(router=crud_router, prefix="/admin", tags=['api'])
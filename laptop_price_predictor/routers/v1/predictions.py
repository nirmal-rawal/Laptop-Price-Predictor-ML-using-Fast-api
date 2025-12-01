from fastapi import APIRouter, HTTPException, status
from typing import List

from laptop_price_predictor.services.v1.prediction_service import prediction_service
from laptop_price_predictor.models.user_input_schema_model import LaptopFeatures, PredictionResponse, PredictionRecord


# Create router
router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict Laptop Price",
    description="Predict the price of a laptop based on its specifications"
)
async def predict_price(features: LaptopFeatures):
    try:
        return await prediction_service.predict_price(features)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictionRecord,
    summary="Get Prediction by ID",
    description="Retrieve a specific prediction by its ID"
)
async def get_prediction(prediction_id: str):
    prediction = await prediction_service.get_prediction_by_id(prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    return prediction


@router.get(
    "/predictions",
    response_model=List[PredictionRecord],
    summary="Get Prediction History",
    description="Retrieve recent prediction history"
)
async def get_prediction_history(limit: int = 100):
    if limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit cannot exceed 1000"
        )
    return await prediction_service.get_prediction_history(limit)


@router.delete(
    "/cache",
    summary="Clear Prediction Cache",
    description="Clear all cached predictions"
)
async def clear_cache():
    await prediction_service.clear_cache()
    return {"message": "Prediction cache cleared successfully"}


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the service is healthy"
)
async def health_check():
    return {
        "status": "healthy",
        "service": "Laptop Price Predictor"
    }
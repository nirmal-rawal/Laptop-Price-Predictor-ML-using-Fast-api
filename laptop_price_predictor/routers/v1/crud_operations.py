from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Dict

from laptop_price_predictor.repositories.prediction_repository import prediction_repository
from laptop_price_predictor.models.user_input_schema_model import PredictionRecord


# Create router
router = APIRouter()


@router.get("/", response_model=List[PredictionRecord], summary="Get All Predictions")
async def get_all_predictions(
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    try:
        return await prediction_repository.get_all_predictions(limit=limit, skip=skip)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve predictions: {str(e)}"
        )


@router.get("/{prediction_id}", response_model=PredictionRecord, summary="Get Prediction")
async def get_prediction(prediction_id: str):
    prediction = await prediction_repository.get_prediction(prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    return prediction


@router.get("/company/{company}", response_model=List[PredictionRecord], summary="Get Predictions By Company")
async def get_predictions_by_company(
    company: str,
    limit: int = Query(50, ge=1, le=200)
):
    try:
        return await prediction_repository.get_predictions_by_company(company, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve predictions: {str(e)}"
        )


@router.get("/price-range", response_model=List[PredictionRecord], summary="Get Predictions By Price Range")
async def get_predictions_by_price_range(
    min_price: float = Query(0, ge=0, description="Minimum price"),
    max_price: float = Query(1000000, ge=0, description="Maximum price"),
    limit: int = Query(50, ge=1, le=200, description="Number of records to return")
):
    if min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price"
        )
    
    try:
        return await prediction_repository.get_predictions_by_price_range(
            min_price, max_price, limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve predictions: {str(e)}"
        )


@router.put("/{prediction_id}", response_model=Dict, summary="Update Prediction")
async def update_prediction(prediction_id: str, update_data: Dict):
    allowed_fields = {'input_features', 'output_prediction', 'price_formatted'}
    if not set(update_data.keys()).issubset(allowed_fields):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only these fields can be updated: {allowed_fields}"
        )
    
    success = await prediction_repository.update_prediction(prediction_id, update_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found or no changes made"
        )
    
    return {
        "message": "Prediction updated successfully",
        "prediction_id": prediction_id,
        "updated_fields": list(update_data.keys())
    }


@router.delete("/{prediction_id}", response_model=Dict, summary="Delete Prediction")
async def delete_prediction(prediction_id: str):
    success = await prediction_repository.delete_prediction(prediction_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    
    return {
        "message": "Prediction deleted successfully",
        "prediction_id": prediction_id
    }


@router.delete("/company/{company}", response_model=Dict, summary="Delete Predictions By Company")
async def delete_predictions_by_company(company: str):
    deleted_count = await prediction_repository.delete_predictions_by_company(company)
    
    return {
        "message": f"Deleted {deleted_count} predictions for company {company}",
        "company": company,
        "deleted_count": deleted_count
    }


@router.get("/stats/count", response_model=Dict, summary="Get Predictions Count")
async def get_predictions_count():
    count = await prediction_repository.get_predictions_count()
    return {"total_predictions": count}


@router.get("/stats/companies", response_model=List[Dict], summary="Get Companies Statistics")
async def get_companies_stats():
    return await prediction_repository.get_companies_stats()


@router.get("/stats/price", response_model=Dict, summary="Get Price Statistics")
async def get_price_statistics():
    return await prediction_repository.get_price_statistics()
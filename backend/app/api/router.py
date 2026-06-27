from app.api.v1.endpoints.analysis import router as analysis_router
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])

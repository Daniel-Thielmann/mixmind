from fastapi import APIRouter
from fastapi import File
from fastapi import UploadFile

from app.schemas.response import UploadResponse
from app.services.storage_service import storage_service

router = APIRouter()

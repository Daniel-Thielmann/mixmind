from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def analysis_status():
    """
    Endpoint temporário.

    Será substituído posteriormente pelo endpoint responsável
    por analisar duas músicas.
    """

    return {"service": "Analysis Service", "status": "available"}

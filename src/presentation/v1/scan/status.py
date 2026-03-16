from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/",
    summary="Статус сервиса сканирования",
    description="Проверка доступности сервиса сканирования.",
)
async def scan_status():
    return {"data": "start scan"}

from fastapi import APIRouter
from fastapi import Depends

from src.di import get_alert_service
from src.schemas import AlertItem
from src.service.alert_service import AlertService

router = APIRouter(tags=["Alerts"], prefix="/alerts")


@router.get("", response_model=list[AlertItem])
async def list_alerts_view(
    service: AlertService = Depends(get_alert_service),
):
    return await service.list_alerts()

from fastapi import Depends

from src.adapters.path_file_adapter import PathLibFileAdapter
from src.database.base import get_session
from src.service.alert_service import AlertService
from src.service.file_service import FileService


def get_alert_service(
        session=Depends(get_session),
):
    return AlertService(session)


def get_file_service(
        session=Depends(get_session),
        storage=PathLibFileAdapter(),
):
    return FileService(
        session,
        storage,
    )
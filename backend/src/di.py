from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.path_file_adapter import PathLibFileAdapter
from src.database.base import get_session
from src.service.alert_service import AlertService
from src.service.file_service import FileService
from src.repositories.file_repo import FileRepo
from src.repositories.alert_repo import AlertRepo


def get_file_adapter():
    return PathLibFileAdapter()

def get_file_repository(
    session: AsyncSession = Depends(get_session),
):
    return FileRepo(session)


def get_alert_repository(
    session: AsyncSession = Depends(get_session),
):
    return AlertRepo(session)


def get_alert_service(
    repo=Depends(get_alert_repository),
):
    return AlertService(repo=repo)


def get_file_service(
        repo=Depends(get_file_repository),
        storage=Depends(get_file_adapter),
):
    return FileService(
        storage_adapter=storage,
        file_repo=repo,
    )

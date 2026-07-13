from src.dto import AlertDTO
from src.repositories.alert_repo import AlertRepo


class AlertService:

    def __init__(self, repo: AlertRepo):
        self.repo = repo

    async def create_alert(self, file_id: str, level: str, message: str) -> AlertDTO:
        return await self.repo.create(
            file_id=file_id,
            level=level,
            message=message
        )

    async def list_alerts(self) -> list[AlertDTO]:
        return await self.repo.get_alert_list()

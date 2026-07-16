from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dto import AlertDTO
from src.models import Alert


class AlertRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Alert

    async def create(self, **kwargs) -> AlertDTO:
        alert = Alert(**kwargs)

        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return AlertDTO(
            id=alert.id,
            file_id=alert.file_id,
            level=alert.level,
            message=alert.message,
        )

    async def get_alert_list(self) -> list[AlertDTO]:
        result = await self.session.execute(
            select(self.model).order_by(self.model.created_at.desc())
        )
        return [
            AlertDTO(
                id=alert.id,
                file_id=alert.file_id,
                level=alert.level,
                message=alert.message,
                created_at=alert.created_at,
            ) for alert in result.scalars().all()
        ]

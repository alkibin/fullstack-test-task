from src.models import Alert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class AlertService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_alert(self, file_id: str, level: str, message: str) -> Alert:
        alert = Alert(file_id=file_id, level=level, message=message)

        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def list_alerts(self) -> list[Alert]:
        result = await self.session.execute(
            select(Alert).order_by(Alert.created_at.desc())
        )
        return list(result.scalars().all())

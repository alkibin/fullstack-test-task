import asyncio
import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import exceptions
from src.tasks.handlers import scan_file_for_threats
from src.config import settings
from src.models import StoredFile


class FileService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_files(self) -> list[StoredFile]:
        result = await self.session.execute(
            select(StoredFile).order_by(StoredFile.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_file(self, file_id: str) -> StoredFile:
        file_item = await self.session.get(StoredFile, file_id)
        if not file_item:
            raise exceptions.NotFoundError(file_id)

        return file_item

    async def create_file(self, title: str, upload_file: UploadFile) -> StoredFile:
        content = await upload_file.read()
        if not content:
            raise exceptions.EmptyFileError()

        file_id = str(uuid4())
        suffix = Path(upload_file.filename or "").suffix
        stored_name = f"{file_id}{suffix}"
        stored_path = settings.STORAGE_DIR / stored_name

        await asyncio.to_thread(stored_path.write_bytes, content)

        file_item = StoredFile(
            id=file_id,
            title=title,
            original_name=upload_file.filename or stored_name,
            stored_name=stored_name,
            mime_type=upload_file.content_type or mimetypes.guess_type(stored_name)[0] or "application/octet-stream",
            size=len(content),
            processing_status="uploaded",
        )

        self.session.add(file_item)
        await self.session.commit()
        await self.session.refresh(file_item)

        scan_file_for_threats.delay(file_item.id)

        return file_item

    async def update_file(self, file_id: str, title: str) -> StoredFile:
        file_item = await self.get_file(file_id)

        file_item.title = title
        await self.session.commit()
        await self.session.refresh(file_item)
        return file_item

    async def delete_file(self, file_id: str) -> None:
        file_item = await self.get_file(file_id)

        stored_path = settings.STORAGE_DIR / file_item.stored_name
        await asyncio.to_thread(stored_path.unlink, missing_ok=True)

        await self.session.delete(file_item)
        await self.session.commit()

    async def get_file_path(self, file_id: str) -> tuple[StoredFile, Path]:
        file_item = await self.get_file(file_id)
        stored_path = settings.STORAGE_DIR / file_item.stored_name
        exists = await asyncio.to_thread(stored_path.exists)
        if not exists:
            raise exceptions.StoredFileMissingError(file_id)

        return file_item, stored_path

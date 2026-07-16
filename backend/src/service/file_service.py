import mimetypes
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src import exceptions
from src.interfaces.file_storage import FileStorage
from src.models import StoredFile
from src.tasks.handlers import scan_file_for_threats


class FileService:

    def __init__(self, session: AsyncSession, storage_adapter: FileStorage):
        self.session = session
        self.storage = storage_adapter

    async def list_files(self) -> list[StoredFile]:
        result = await self.session.execute(
            select(StoredFile).order_by(StoredFile.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_file(self, file_id: str) -> StoredFile:
        file_item = await self.session.get(StoredFile, file_id)
        if not file_item:
            raise exceptions.NotFoundError(file_id)

        if not await self.storage.exists(str(file_item.stored_name)):
            raise exceptions.EmptyFileError()

        return file_item

    async def create_file(
        self,
        title: str,
        filename: str,
        content_type: str | None,
        stream: AsyncIterator[bytes],
    ) -> StoredFile:
        size, file_id, stored_name = await self.storage.save_stream(
            filename, stream
        )
        if size == 0:
            await self.storage.delete(stored_name)
            raise exceptions.EmptyFileError()

        file_item = StoredFile(
            id=file_id,
            title=title,
            original_name=filename or stored_name,
            stored_name=stored_name,
            mime_type=content_type or mimetypes.guess_type(stored_name)[0] or "application/octet-stream",
            size=size,
            processing_status="uploaded",
        )
        self.session.add(file_item)
        await self.session.commit()
        await self.session.refresh(file_item)

        scan_file_for_threats.delay(file_item.id)

        return file_item

    async def rename_file(self, file_id: str, title: str) -> StoredFile:
        file_item = await self.get_file(file_id)
        file_item.title = title
        await self.session.commit()
        await self.session.refresh(file_item)
        return file_item

    async def delete_file(self, file_id: str) -> None:
        file_item = await self.get_file(file_id)
        await self.storage.delete(file_item.stored_name)
        await self.session.delete(file_item)
        await self.session.commit()

    async def download_file(self, file_id: str):
        file_item = await self.get_file(file_id)
        file_stream_iter = self.storage.get_stream(file_item.stored_name)
        return file_item, file_stream_iter

import mimetypes
from typing import AsyncIterator

from src import exceptions
from src.dto import FileWithMetaDTO
from src.interfaces.file_storage import FileStorage
from src.repositories.file_repo import FileRepo
from src.tasks.handlers import scan_file_for_threats


class FileService:

    def __init__(
            self,
            storage_adapter: FileStorage,
            file_repo: FileRepo
    ):
        self.storage = storage_adapter
        self.repo = file_repo

    async def list_files(self) -> list[FileWithMetaDTO]:
        return await self.repo.get_files_with_meta()

    async def get_file(self, file_name_id: int) -> FileWithMetaDTO:
        file_item = await self.repo.get_full_file_data(file_name_id=file_name_id)
        if not file_item:
            raise exceptions.NotFoundError(file_name_id)

        if not await self.storage.exists(str(file_item.stored_name)):
            raise exceptions.EmptyFileError()

        return file_item

    async def create_file(
        self,
        title: str,
        filename: str,
        content_type: str | None,
        stream: AsyncIterator[bytes],
    ) -> FileWithMetaDTO:
        size, file_id, stored_name, hash_ = await self.storage.save_stream(
            filename, stream
        )

        if size == 0:
            await self.storage.delete(stored_name)
            raise exceptions.EmptyFileError()

        file_in_storage = await self.repo.get_by_field(file_hash=hash_)
        if not file_in_storage:
            file_obj = await self.repo.create_file_with_link(
                id=file_id,
                title=title,
                original_name=filename or stored_name,
                stored_name=stored_name,
                mime_type=content_type or mimetypes.guess_type(stored_name)[0] or "application/octet-stream",
                size=size,
                processing_status="uploaded",
                file_hash=hash_,
            )
            scan_file_for_threats.delay(file_obj.file_id)
        else:
            file_links = await self.repo.fetch_file_links(file_in_storage.id)
            if await self.find_by_name(title, file_links):
                raise exceptions.FileAllreadyExists()
            file_obj = await self.repo.create_file_link(
                title=title,
                file_id=file_in_storage.id,
            )
            await self.storage.delete(stored_name)
        return await self.repo.get_full_file_data(file_obj.id)

    async def find_by_name(self, name: str, files):
        return next((file for file in files if file.title == name), None)

    async def rename_file(self, file_name_id: int, title: str) -> FileWithMetaDTO:
        file_item = await self.repo.get_full_file_data(file_name_id)
        if not file_item:
            raise exceptions.NotFoundError(file_name_id)
        await self.repo.update_link(file_name_id, title=title)
        return await self.repo.get_full_file_data(file_name_id)

    async def delete_file(self, file_link_id: int) -> None:
        file_item = await self.repo.get_full_file_data(file_name_id=file_link_id)

        if not file_item:
            raise exceptions.NotFoundError(file_link_id)

        await self.repo.delete_file_link(file_link_id)

        if not await self.repo.check_file_has_links(file_item.file_id):
            await self.repo.delete_file(file_item.file_id)
            _ = await self.storage.delete(file_item.stored_name)

    async def download_file(self, file_id: int):
        file_item = await self.get_file(file_id)
        file_stream_iter = await self.storage.get_stream(file_item.stored_name)
        return file_item, file_stream_iter

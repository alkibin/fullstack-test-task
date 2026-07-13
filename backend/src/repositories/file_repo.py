from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.dto import FileWithMetaDTO
from src.models import StoredFile, FileName


class FileRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = StoredFile

    async def get_files_with_meta(self):
        query = (
            select(FileName, StoredFile)
            .join(StoredFile)
            .order_by(FileName.created_at.desc())
        )
        result = await self.session.execute(query)
        items = []
        for file_name, stored_file in result.all():
            items.append(FileWithMetaDTO(
                id=file_name.id,
                file_id=stored_file.id,
                title=file_name.title,
                original_name=stored_file.original_name,
                mime_type=stored_file.mime_type,
                size=stored_file.size,
                processing_status=stored_file.processing_status,
                scan_status=stored_file.scan_status,
                scan_details=stored_file.scan_details,
                metadata_json=stored_file.metadata_json,
                requires_attention=stored_file.requires_attention,
                created_at=stored_file.created_at,
                updated_at=stored_file.updated_at,
                stored_name=stored_file.stored_name,
            ))
        return items

    async def get_full_file_data(self, file_name_id: int) -> FileWithMetaDTO | None:
        query = (
            select(FileName, self.model)
            .join(self.model)
            .where(FileName.id == file_name_id)
        )
        raw_res = await self.session.execute(query)
        result = raw_res.first()
        if not result:
            return None

        file_name, stored_file = result
        return FileWithMetaDTO(
            id=file_name.id,
            file_id=stored_file.id,
            title=file_name.title,
            original_name=stored_file.original_name,
            mime_type=stored_file.mime_type,
            size=stored_file.size,
            stored_name=stored_file.stored_name,
            processing_status=stored_file.processing_status,
            scan_status=stored_file.scan_status,
            scan_details=stored_file.scan_details,
            metadata_json=stored_file.metadata_json,
            requires_attention=stored_file.requires_attention,
            created_at=stored_file.created_at,
            updated_at=stored_file.updated_at,
        )

    async def create_file_with_link(self, **file_data):
        file_item = StoredFile(
            id=file_data['id'],
            original_name=file_data['original_name'],
            stored_name=file_data['stored_name'],
            mime_type=file_data['mime_type'],
            size=file_data['size'],
            processing_status=file_data['processing_status'],
            file_hash=file_data['file_hash'],
        )
        self.session.add(file_item)
        file_link = FileName(
            file_id=file_item.id,
            title=file_data['title'],
        )
        self.session.add(file_link)

        await self.session.commit()
        await self.session.refresh(file_link)

        return await self.get_full_file_data(file_link.id)


    async def create_file_link(self, **kwargs):
        new_link = FileName(**kwargs)
        self.session.add(new_link)
        await self.session.commit()
        await self.session.refresh(new_link)
        return new_link

    async def get_by_field(self, **kwargs):
        query = (
            select(StoredFile).filter_by(**kwargs)
        )
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def update_link(self, file_id, **kwargs):
        query = (
            update(FileName)
            .where(FileName.file_id==file_id)
            .values(**kwargs)
            .returning(FileName)
        )
        await self.session.execute(query)
        await self.session.commit()

    async def delete_file(self, file_id):
        file = await self.session.get(StoredFile, file_id)
        if file:
            await self.session.delete(file)
            await self.session.commit()

    async def delete_file_link(self, file_link_id):
        file = await self.session.get(FileName, file_link_id)
        if file:
            await self.session.delete(file)
            await self.session.commit()

    async def fetch_file_links(self, file_id):
        query = select(FileName).filter_by(file_id=file_id)
        res = await self.session.execute(query)
        return res.scalars().all()

    async def check_file_has_links(self, file_id: str) -> bool:
        await self.session.execute(
            select(StoredFile).where(StoredFile.id == file_id).with_for_update()
        )
        query = select(FileName).where(FileName.file_id == file_id)
        result = await self.session.execute(query)
        return bool(result.scalars().all())





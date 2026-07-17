from urllib.parse import quote

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File, Form, UploadFile
from fastapi.responses import StreamingResponse

from src.api.upload_utils import iter_upload_file
from src.di import get_file_service
from src.schemas import FileItem, FileUpdate
from src.service.file_service import FileService

router = APIRouter(tags=["File"], prefix="/files")


@router.get("", response_model=list[FileItem])
async def list_files_view(service: FileService = Depends(get_file_service)):
    return await service.list_files()


@router.post("", response_model=FileItem, status_code=201)
async def create_file_view(
    title: str = Form(...),
    file: UploadFile = File(...),
    service: FileService = Depends(get_file_service)
):
    file_item = await service.create_file(
        title=title,
        filename=file.filename or "",
        content_type=file.content_type,
        stream=iter_upload_file(file),
    )
    return FileItem.model_validate(file_item)


@router.get("/{file_id}", response_model=FileItem)
async def get_file_view(
        file_id: int,
        service: FileService = Depends(get_file_service),
):
    file_item = await service.get_file(file_id)
    return FileItem.model_validate(file_item)


@router.patch("/{file_id}", response_model=FileItem)
async def update_file_view(
    file_id: int,
    payload: FileUpdate,
    service: FileService = Depends(get_file_service),
):
    file_item = await service.rename_file(file_name_id=file_id, title=payload.title)
    return FileItem.model_validate(file_item)


@router.get("/{file_id}/download")
async def download_file(
        file_id: int,
        service: FileService = Depends(get_file_service),
):
    file_item, stream = await service.download_file(file_id=file_id)
    encoded_filename = quote(file_item.original_name)
    return StreamingResponse(
        content=stream,
        media_type=file_item.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{encoded_filename}"'}
    )


@router.delete("/{file_id}", status_code=204)
async def delete_file_view(
    file_id: int,
    service: FileService = Depends(get_file_service),
):
    await service.delete_file(file_link_id=file_id)

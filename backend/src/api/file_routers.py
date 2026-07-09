from fastapi import APIRouter
from fastapi import Depends
from fastapi import File, Form, UploadFile
from fastapi.responses import FileResponse

from src.schemas import FileItem, FileUpdate
from src.service.file_service import FileService
from src.di import get_file_service

router = APIRouter(tags=["File"], prefix="/files")


@router.get("", response_model=list[FileItem])
async def list_files_view(
    service: FileService = Depends(get_file_service),
):
    return await service.list_files()


@router.post("", response_model=FileItem, status_code=201)
async def create_file_view(
    title: str = Form(...),
    file: UploadFile = File(...),
    service: FileService = Depends(get_file_service)
):
    file_item = await service.create_file(title=title, upload_file=file)
    return file_item


@router.get("/{file_id}", response_model=FileItem)
async def get_file_view(
        file_id: str,
        service: FileService = Depends(get_file_service),
):
    return await service.get_file(file_id)


@router.patch("/{file_id}", response_model=FileItem)
async def update_file_view(
    file_id: str,
    payload: FileUpdate,
    service: FileService = Depends(get_file_service),
):
    return await service.update_file(file_id=file_id, title=payload.title)


@router.get("/{file_id}/download")
async def download_file(
        file_id: str,
        service: FileService = Depends(get_file_service),
):
    file_item, stored_path = await service.get_file_path(file_id=file_id)
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete("/{file_id}", status_code=204)
async def delete_file_view(
        file_id: str,
        service: FileService = Depends(get_file_service),
):
    await service.delete_file(file_id)

from typing import AsyncIterator

from fastapi import UploadFile

from src.config import settings


async def iter_upload_file(
        upload_file: UploadFile,
        chunk_size: int = settings.UPLOAD_CHUNK_SIZE,
) -> AsyncIterator[bytes]:
    while chunk := await upload_file.read(chunk_size):
        yield chunk
import asyncio
from pathlib import Path
import hashlib
from typing import AsyncIterator
from uuid import uuid4

from src.config import settings
from src.interfaces.file_storage import FileStorage


class PathLibFileAdapter(FileStorage):

    storage_dir: Path = settings.STORAGE_DIR
    chunk_size: int = settings.UPLOAD_CHUNK_SIZE

    async def save_stream(self, name: str, stream: AsyncIterator[bytes]) -> tuple[str, str, str, str]:
        file_id = str(uuid4())
        suffix = Path(name).suffix
        stored_name = f"{file_id}{suffix}"

        path = self.storage_dir / stored_name
        size = 0
        f = await asyncio.to_thread(path.open, "wb")
        try:
            async for chunk in stream:
                _ = await asyncio.to_thread(f.write, chunk)
                hash_ = self.calc_hash_md5(chunk)
                size += len(chunk)
            return size, file_id, stored_name, self.hash_to_str(hash_)
        finally:
            await asyncio.to_thread(f.close)

    def calc_hash_md5(self, chunk: bytes) -> str:
        h = hashlib.md5()
        def calc(chunk: bytes) -> bytes:
            h.update(chunk)
        calc(chunk)
        return h

    def hash_to_str(self, hash) -> str:
        return hash.hexdigest()

    async def delete(self, file_stored_name: str):
        stored_path = self.storage_dir / file_stored_name
        _ = await asyncio.to_thread(stored_path.unlink, missing_ok=True)

    async def get_stream(self, name: str) -> AsyncIterator[bytes]:
        path = self.storage_dir / name
        f = await asyncio.to_thread(path.open, "rb")
        try:
            while chunk := await asyncio.to_thread(f.read, self.chunk_size):
                yield chunk
        finally:
            await asyncio.to_thread(f.close)

    async def exists(self, stored_name: str) -> bool:
        stored_path = self.storage_dir / stored_name
        return await asyncio.to_thread(stored_path.exists)
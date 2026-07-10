from typing import AsyncIterator, Protocol
from abc import ABC, abstractmethod

class FileStorage(ABC):
    @abstractmethod
    async def save_stream(self, name: str, stream: bytes):
        pass

    @abstractmethod
    async def get_stream(self, name: str) -> AsyncIterator[bytes]:
        pass

    @abstractmethod
    async def delete(self, name: str) -> None:
        pass

    @abstractmethod
    async def exists(self, name: str) -> bool:
        pass

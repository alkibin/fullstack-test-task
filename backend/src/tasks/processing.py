from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.config import settings
from src.models import Alert, StoredFile

engine = create_async_engine(settings.db_url)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

SUSPICIOUS_EXTENSIONS = {".exe", ".bat", ".cmd", ".sh", ".js"}
MAX_SAFE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_MIMES = ["application/pdf", "application/octet-stream"]


async def scan_file_for_threats_(file_id: str) -> bool | None:
    async with async_session_maker() as session:
        file_item = await _get_file(session, file_id)
        file_item.processing_status = "processing"
        reasons: list[str] = []
        extension = Path(file_item.original_name).suffix.lower()

        if extension in SUSPICIOUS_EXTENSIONS:
            reasons.append(f"suspicious extension {extension}")

        if file_item.size > MAX_SAFE_SIZE_BYTES:
            reasons.append("file is larger than 10 MB")

        if extension == ".pdf" and file_item.mime_type not in ALLOWED_MIMES:
            reasons.append("pdf extension does not match mime type")

        file_item.scan_status = "suspicious" if reasons else "clean"
        file_item.scan_details = ", ".join(reasons) if reasons else "no threats found"
        file_item.requires_attention = bool(reasons)
        await session.commit()
        return True


async def extract_file_metadata_(file_id: str) -> bool | None:
    async with async_session_maker() as session:
        file_item = await _get_file(session, file_id)

        stored_path = settings.STORAGE_DIR / file_item.stored_name
        if not stored_path.exists():
            file_item.processing_status = "failed"
            file_item.scan_status = file_item.scan_status or "failed"
            file_item.scan_details = "stored file not found during metadata extraction"
            await session.commit()
            return

        metadata = {
            "extension": Path(file_item.original_name).suffix.lower(),
            "size_bytes": file_item.size,
            "mime_type": file_item.mime_type,
        }

        line_count = 0
        char_count = 0
        if file_item.mime_type.startswith("text/"):
            with open(stored_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line_count += 1
                    char_count += len(line)

            metadata["line_count"] = line_count
            metadata["char_count"] = char_count
        elif file_item.mime_type == "application/pdf":
            with open(stored_path, 'rb') as f:
                header = f.read(1024 * 1024)
            metadata["approx_page_count"] = max(header.count(b"/Type /Page"), 1)

        file_item.metadata_json = metadata
        file_item.processing_status = "processed"
        await session.commit()
        return



async def send_file_alert_(file_id: str) -> None:
    async with async_session_maker() as session:
        file_item = await _get_file(session, file_id)

        if file_item.processing_status == "failed":
            alert = Alert(file_id=file_id, level="critical", message="File processing failed")
        elif file_item.requires_attention:
            alert = Alert(
                file_id=file_id,
                level="warning",
                message=f"File requires attention: {file_item.scan_details}",
            )
        else:
            alert = Alert(file_id=file_id, level="info", message="File processed successfully")

        session.add(alert)
        await session.commit()


async def _get_file(session: AsyncSession, file_id: str) -> StoredFile:
    file_item = await session.get(StoredFile, file_id)
    if not file_item:
        raise FileNotFoundError(file_id)
    return file_item

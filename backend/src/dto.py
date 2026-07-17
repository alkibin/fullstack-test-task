from dataclasses import dataclass
from datetime import datetime, UTC


@dataclass
class FileWithMetaDTO:
    id: int
    file_id: str
    title: str
    original_name: str
    mime_type: str
    stored_name: str
    size: int
    processing_status: str
    scan_status: str | None
    scan_details: str | None
    metadata_json: dict | None
    requires_attention: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class AlertDTO:
    id: int
    file_id: str
    level: str
    message: str
    created_at: datetime = datetime.now(UTC)
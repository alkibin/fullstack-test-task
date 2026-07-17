from unittest.mock import AsyncMock
from datetime import datetime

from src.dto import FileWithMetaDTO, AlertDTO


mock_file_repo = AsyncMock()
mock_file_repo.get_file_with_meta = AsyncMock()
mock_file_repo.get_full_file_data = AsyncMock(
    return_value=FileWithMetaDTO(
        id=1,
        file_id="1",
        title='title',
        size=123,
        original_name='original_name',
        stored_name='stored_name',
        mime_type='mimetype',
        processing_status="pending",
        scan_status="scan_status",
        scan_details="scan_details",
        metadata_json={"id": "id"},
        requires_attention=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
)
mock_file_repo.create_file_with_link = AsyncMock()
mock_file_repo.get_by_field = AsyncMock()


mock_alert_repo = AsyncMock()
mock_alert_repo.get_alert_list = AsyncMock(
    return_value=[
        AlertDTO(
            id=444,
            file_id="444",
            level="level",
            message="message",
        )
    ]
)


mock_files_adapter = AsyncMock()
mock_files_adapter.save_stream = AsyncMock(
    return_value=(255, 1, 'test_stor_name', 'hash')
)



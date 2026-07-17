import asyncio

from src.celery_app import celery_app
from src.tasks.processing import scan_file_for_threats_, extract_file_metadata_, send_file_alert_

_worker_loop: asyncio.AbstractEventLoop | None = None

def run_in_worker_loop(coroutine):
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
    return _worker_loop.run_until_complete(coroutine)


@celery_app.task(bind=True, max_retries=3)
def scan_file_for_threats(self, file_id: str) -> None:
    try:
        run_in_worker_loop(scan_file_for_threats_(file_id))
        extract_file_metadata.delay(file_id)
    except FileNotFoundError as e:
        pass


@celery_app.task(bind=True, max_retries=3)
def extract_file_metadata(self, file_id: str) -> None:
    try:
        run_in_worker_loop(extract_file_metadata_(file_id))
        send_file_alert.delay(file_id)
    except FileNotFoundError as e:
        pass


@celery_app.task(bind=True, max_retries=3)
def send_file_alert(self, file_id: str) -> None:
    run_in_worker_loop(send_file_alert_(file_id))

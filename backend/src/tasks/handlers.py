import asyncio

from src.celery_app import celery_app
from src.tasks.processing import scan_file_for_threats, extract_file_metadata, send_file_alert

_worker_loop: asyncio.AbstractEventLoop | None = None

def run_in_worker_loop(coroutine):
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(coroutine)


@celery_app.task(bind=True, max_retries=3)
def scan_file_for_threats(file_id: str) -> None:
    try:
        run_in_worker_loop(scan_file_for_threats(file_id))
        extract_file_metadata.delay(file_id)
    except FileNotFoundError as e:
        pass


@celery_app.task(bind=True, max_retries=3)
def extract_file_metadata(file_id: str) -> None:
    try:
        run_in_worker_loop(extract_file_metadata(file_id))
        send_file_alert.delay(file_id)
    except FileNotFoundError as e:
        pass


@celery_app.task(bind=True, max_retries=3)
def send_file_alert(file_id: str) -> None:
    run_in_worker_loop(send_file_alert(file_id))

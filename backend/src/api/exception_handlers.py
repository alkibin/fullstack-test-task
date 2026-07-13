from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.exceptions import BaseError, EmptyFileError, NotFoundError, FileAllreadyExists


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(EmptyFileError)
    async def empty_file_handler(request: Request, exc: EmptyFileError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(BaseError)
    async def domain_error_handler(request: Request, exc: BaseError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(BaseError)
    async def exists_file_error_handler(request: Request, exc: FileAllreadyExists):
        return JSONResponse(status_code=400, content={"detail": str(exc)})
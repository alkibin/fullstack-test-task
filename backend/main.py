from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.exception_handlers import register_exception_handlers
from src.api.file_routers import router as file_router
from src.api.alert_routers import router as alert_router


app = FastAPI()
app.include_router(file_router)
app.include_router(alert_router)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
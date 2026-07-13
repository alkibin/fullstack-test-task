from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


class StoredFile(Base):

    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255), unique=True)
    mime_type: Mapped[str] = mapped_column(String(255))
    size: Mapped[int]
    processing_status: Mapped[str] = mapped_column(String(50), default="uploaded")
    scan_status: Mapped[str | None] = mapped_column(String(50))
    scan_details: Mapped[str | None] = mapped_column(String(500))
    metadata_json: Mapped[dict | None] = mapped_column(JSON)
    requires_attention: Mapped[bool] = mapped_column(Boolean, default=False)
    file_hash: Mapped[str | None] = mapped_column(String(255), unique=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="file",
        cascade="all, delete-orphan",
    )
    names: Mapped[list["FileName"]] = relationship(
        back_populates="file",
        cascade="all, delete-orphan",
    )


class FileName(Base):

    __tablename__ = "file_names"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    file_id: Mapped[str] = mapped_column(String(36), ForeignKey("files.id"))

    file: Mapped["StoredFile"] = relationship(
        back_populates="names",
    )


class Alert(Base):

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(String(36), ForeignKey("files.id"), index=True)
    level: Mapped[str] = mapped_column(String(50))
    message: Mapped[str] = mapped_column(String(500))

    file: Mapped["StoredFile"] = relationship(back_populates="alerts")

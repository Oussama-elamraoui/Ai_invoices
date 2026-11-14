from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.invoice import Invoice


class ProcessingJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "processing_jobs"

    original_filename: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    storage_key: Mapped[str] = mapped_column(
        String(1024), nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30), default="PENDING", nullable=False, index=True
    )

    total_files: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    processed_files: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    failed_files: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="processing_job",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<ProcessingJob id={self.id} status={self.status!r}>"
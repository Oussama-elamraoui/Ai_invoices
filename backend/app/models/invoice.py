import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    Uuid,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.client import Client
    from app.models.invoice_item import InvoiceItem
    from app.models.processing_job import ProcessingJob
    from app.models.supplier import Supplier


class Invoice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "invoices"

    supplier_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("clients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    processing_job_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("processing_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    invoice_number: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    invoice_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    due_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    currency: Mapped[str] = mapped_column(
        String(3), default="MAD", nullable=False
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0.00"), nullable=False
    )
    tax_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0.00"), nullable=False
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0.00"), nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30), default="DRAFT", nullable=False, index=True
    )
    source_filename: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    supplier: Mapped["Supplier"] = relationship(
        back_populates="invoices"
    )
    client: Mapped["Client"] = relationship(
        back_populates="invoices"
    )
    processing_job: Mapped["ProcessingJob | None"] = relationship(
        back_populates="invoices"
    )
    items: Mapped[list["InvoiceItem"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="InvoiceItem.line_number",
    )

    __table_args__ = (
        UniqueConstraint(
            "supplier_id",
            "invoice_number",
            name="uq_invoice_supplier_number",
        ),
        CheckConstraint(
            "subtotal >= 0 AND tax_total >= 0 AND total >= 0",
            name="ck_invoice_nonnegative_totals",
        ),
        CheckConstraint(
            "length(currency) = 3",
            name="ck_invoice_currency_length",
        ),
        Index("ix_invoice_date_status", "invoice_date", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"<Invoice id={self.id} "
            f"number={self.invoice_number!r} status={self.status!r}>"
        )
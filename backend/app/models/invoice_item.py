from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.invoice import Invoice

import uuid

class InvoiceItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "invoice_items"



    invoice_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    line_number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False
    )
    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), nullable=False
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0.00"), nullable=False
    )
    line_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )

    product_code: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    invoice: Mapped["Invoice"] = relationship(
        back_populates="items"
    )

    __table_args__ = (
        UniqueConstraint(
            "invoice_id",
            "line_number",
            name="uq_invoice_item_line_number",
        ),
        CheckConstraint(
            "quantity > 0",
            name="ck_invoice_item_positive_quantity",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_invoice_item_nonnegative_price",
        ),
        CheckConstraint(
            "tax_rate >= 0 AND tax_rate <= 100",
            name="ck_invoice_item_tax_rate",
        ),
        CheckConstraint(
            "subtotal >= 0 AND tax_amount >= 0 AND line_total >= 0",
            name="ck_invoice_item_nonnegative_amounts",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<InvoiceItem id={self.id} "
            f"line={self.line_number} description={self.description!r}>"
        )
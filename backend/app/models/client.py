from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.invoice import Invoice


class Client(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "clients"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    tax_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    email: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    phone: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    address: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    country: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="client",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_clients_tax_id", "tax_id"),
    )

    def __repr__(self) -> str:
        return f"<Client id={self.id} name={self.name!r}>"
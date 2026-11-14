import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.invoice_item import InvoiceItemInput, InvoiceItemResponse


class InvoiceDraftInput(BaseModel):
    supplier_id: uuid.UUID | None = None
    client_id: uuid.UUID | None = None
    invoice_number: str = Field(min_length=1, max_length=100)
    invoice_date: date
    due_date: date | None = None
    currency: str = Field(default="MAD", pattern=r"^[A-Z]{3}$")
    notes: str | None = None
    items: list[InvoiceItemInput] = Field(min_length=1)


class InvoiceConfirmInput(InvoiceDraftInput):
    supplier_id: uuid.UUID
    client_id: uuid.UUID


class InvoiceResponse(BaseModel):
    id: uuid.UUID
    supplier_id: uuid.UUID
    client_id: uuid.UUID
    processing_job_id: uuid.UUID | None
    invoice_number: str
    invoice_date: date
    due_date: date | None
    currency: str
    subtotal: Decimal
    tax_total: Decimal
    total: Decimal
    status: str
    confirmed_at: datetime | None
    items: list[InvoiceItemResponse]

    model_config = ConfigDict(from_attributes=True)
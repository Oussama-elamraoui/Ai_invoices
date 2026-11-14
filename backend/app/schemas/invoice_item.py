import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class InvoiceItemInput(BaseModel):
    description: str = Field(min_length=1)
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    product_code: str | None = None


class InvoiceItemResponse(InvoiceItemInput):
    id: uuid.UUID
    line_number: int
    subtotal: Decimal
    tax_amount: Decimal
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)
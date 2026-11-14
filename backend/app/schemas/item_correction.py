from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class ItemCorrection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_index: int = Field(ge=0)
    field: Literal[
        "description",
        "quantity",
        "unit_price",
        "tax_rate",
        "product_code",
    ]
    value: str | float | None


class ItemCorrectionsInput(BaseModel):
    corrections: list[ItemCorrection] = Field(min_length=1)
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InvoiceDraftResponse(BaseModel):
    id: UUID
    processing_job_id: UUID
    source_filename: str
    extracted_data: dict[str, Any]
    status: str
    validation_errors: list[str]
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceDraftUpdate(BaseModel):
    extracted_data: dict[str, Any]
    notes: str | None = None
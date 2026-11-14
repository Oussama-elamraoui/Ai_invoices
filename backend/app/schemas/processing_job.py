import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProcessingJobResponse(BaseModel):
    id: uuid.UUID
    original_filename: str
    status: str
    total_files: int
    processed_files: int
    failed_files: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
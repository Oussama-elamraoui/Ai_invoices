from pydantic import BaseModel, Field


class ApproveCorrectionsInput(BaseModel):
    approved_fields: list[str] = Field(default_factory=list)
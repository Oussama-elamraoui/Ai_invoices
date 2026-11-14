import uuid
from pydantic import BaseModel, ConfigDict, EmailStr


class ClientCreate(BaseModel):
    name: str
    tax_id: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    country: str | None = None


class ClientResponse(ClientCreate):
    id: uuid.UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
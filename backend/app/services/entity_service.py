from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import supplier_repository, client_repository


async def search_suppliers(
    db: AsyncSession,
    query: str = "",
    skip: int = 0,
    limit: int = 50,
):
    return await supplier_repository.search(db, query, skip, limit)


async def search_clients(
    db: AsyncSession,
    query: str = "",
    skip: int = 0,
    limit: int = 50,
):
    return await client_repository.search(db, query, skip, limit)


async def require_entities(
    db: AsyncSession,
    supplier_id: UUID,
    client_id: UUID,
):
    supplier = await supplier_repository.get_by_id(db, supplier_id)
    client = await client_repository.get_by_id(db, client_id)

    if not supplier or not supplier.is_active:
        raise HTTPException(422, "Supplier not found or inactive")

    if not client or not client.is_active:
        raise HTTPException(422, "Client not found or inactive")

    return supplier, client
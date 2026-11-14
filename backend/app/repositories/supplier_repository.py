from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.supplier import Supplier


async def get_by_id(db: AsyncSession, supplier_id: UUID) -> Supplier | None:
    return await db.get(Supplier, supplier_id)


async def search(
    db: AsyncSession,
    query: str = "",
    skip: int = 0,
    limit: int = 50,
) -> list[Supplier]:
    filters = [Supplier.is_active.is_(True)]
    if query:
        filters.append(Supplier.name.ilike(f"%{query}%"))

    stmt = (
        select(Supplier)
        .where(*filters)
        .order_by(Supplier.name)
        .offset(skip)
        .limit(limit)
    )
    return list((await db.scalars(stmt)).all())


async def create(db: AsyncSession, data: dict):
    supplier = Supplier(**data)
    db.add(supplier)
    await db.flush()
    await db.refresh(supplier)
    return supplier
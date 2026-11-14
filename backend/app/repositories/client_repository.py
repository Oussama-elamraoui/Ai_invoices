from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.client import Client


async def get_by_id(db: AsyncSession, client_id: UUID) -> Client | None:
    return await db.get(Client, client_id)


async def search(
    db: AsyncSession,
    query: str = "",
    skip: int = 0,
    limit: int = 50,
) -> list[Client]:
    filters = [Client.is_active.is_(True)]
    if query:
        filters.append(Client.name.ilike(f"%{query}%"))

    stmt = (
        select(Client)
        .where(*filters)
        .order_by(Client.name)
        .offset(skip)
        .limit(limit)
    )
    return list((await db.scalars(stmt)).all())


async def create(db: AsyncSession, data: dict):
    client = Client(**data)
    db.add(client)
    await db.flush()
    await db.refresh(client)
    return client
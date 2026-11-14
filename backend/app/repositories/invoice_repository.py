from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice


async def get_by_id(db: AsyncSession, invoice_id: UUID) -> Invoice | None:
    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.items))
        .where(Invoice.id == invoice_id)
    )
    return await db.scalar(stmt)


async def list_invoices(
    db: AsyncSession,
    job_id: UUID | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Invoice]:
    filters = []
    if job_id is not None:
        filters.append(Invoice.processing_job_id == job_id)
    if status is not None:
        filters.append(Invoice.status == status)

    stmt = (
        select(Invoice)
        .options(selectinload(Invoice.items))
        .where(*filters)
        .order_by(Invoice.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list((await db.scalars(stmt)).all())
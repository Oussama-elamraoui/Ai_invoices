from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice_draft import InvoiceDraft


async def create(
    db: AsyncSession,
    job_id: UUID,
    filename: str,
    extracted_data: dict,
) -> InvoiceDraft:
    draft = InvoiceDraft(
        processing_job_id=job_id,
        source_filename=filename,
        extracted_data=extracted_data,
    )

    db.add(draft)
    await db.flush()
    await db.refresh(draft)

    return draft


async def get_by_id(
    db: AsyncSession,
    draft_id: UUID,
) -> InvoiceDraft | None:
    return await db.get(InvoiceDraft, draft_id)


async def list_by_job(
    db: AsyncSession,
    job_id: UUID,
) -> list[InvoiceDraft]:
    result = await db.scalars(
        select(InvoiceDraft)
        .where(InvoiceDraft.processing_job_id == job_id)
        .order_by(InvoiceDraft.created_at.desc())
    )

    return list(result.all())
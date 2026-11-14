from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import invoice_draft_repository
from app.schemas.invoice_draft import InvoiceDraftUpdate


async def get_draft(db: AsyncSession, draft_id: UUID):
    draft = await invoice_draft_repository.get_by_id(db, draft_id)

    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    return draft


async def list_drafts(db: AsyncSession, job_id: UUID):
    return await invoice_draft_repository.list_by_job(db, job_id)


async def update_draft(
    db: AsyncSession,
    draft_id: UUID,
    payload: InvoiceDraftUpdate,
):
    draft = await get_draft(db, draft_id)

    if draft.status != "PENDING_REVIEW":
        raise HTTPException(
            status_code=409,
            detail="Only drafts pending review can be edited",
        )

    draft.extracted_data = payload.extracted_data
    draft.notes = payload.notes

    await db.commit()
    await db.refresh(draft)

    return draft
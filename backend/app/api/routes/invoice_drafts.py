from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.invoice_draft import (
    InvoiceDraftResponse,
    InvoiceDraftUpdate,
)
from app.schemas.invoice import InvoiceConfirmInput, InvoiceResponse
from app.schemas.corrections import ApproveCorrectionsInput
from app.schemas.item_correction import ItemCorrectionsInput
from app.services import invoice_draft_service
from app.services.invoice_confirmation_service import confirm_draft
from app.agents.apply_corrections import apply_approved_corrections
from app.agents.apply_item_corrections import apply_item_corrections
from app.agents.validation_agent import validate_invoice

router = APIRouter(prefix="/invoice-drafts", tags=["Invoice Drafts"])


@router.get("/job/{job_id}", response_model=list[InvoiceDraftResponse])
async def list_drafts(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await invoice_draft_service.list_drafts(db, job_id)


@router.get("/{draft_id}", response_model=InvoiceDraftResponse)
async def get_draft(
    draft_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await invoice_draft_service.get_draft(db, draft_id)


@router.patch("/{draft_id}", response_model=InvoiceDraftResponse)
async def update_draft(
    draft_id: UUID,
    payload: InvoiceDraftUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await invoice_draft_service.update_draft(
        db, draft_id, payload
    )

@router.post("/{draft_id}/confirm", response_model=InvoiceResponse)
async def confirm_invoice_draft(
    draft_id: UUID,
    payload: InvoiceConfirmInput,
    db: AsyncSession = Depends(get_db),
):
    return await confirm_draft(db, draft_id, payload)

@router.post("/{draft_id}/approve-corrections")
async def approve_corrections(
    draft_id: UUID,
    payload: ApproveCorrectionsInput,
    db: AsyncSession = Depends(get_db),
):
    draft = await invoice_draft_service.get_draft(db, draft_id)

    if draft.status != "PENDING_REVIEW":
        raise HTTPException(409, "Draft is not editable")

    suggestions = draft.extracted_data.get("correction_suggestions")

    if not suggestions:
        raise HTTPException(400, "No correction suggestions available")

    proposed = suggestions.get("corrected_data", {})
    original = draft.extracted_data

    try:
        updated = apply_approved_corrections(
            original_data=original,
            proposed_data=proposed,
            approved_fields=payload.approved_fields,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

    errors = validate_invoice(updated)

    updated["correction_suggestions"] = None
    draft.extracted_data = updated
    draft.validation_errors = errors

    await db.commit()
    await db.refresh(draft)

    return {
        "draft_id": str(draft.id),
        "validation_errors": errors,
        "extracted_data": updated,
    }
@router.post("/{draft_id}/correct-items")
async def correct_items(
    draft_id: UUID,
    payload: ItemCorrectionsInput,
    db: AsyncSession = Depends(get_db),
):
    draft = await invoice_draft_service.get_draft(db, draft_id)

    if draft.status != "PENDING_REVIEW":
        raise HTTPException(409, "Draft is not editable")

    updated = apply_item_corrections(
        draft.extracted_data,
        [item.model_dump() for item in payload.corrections],
    )

    errors = validate_invoice(updated)

    draft.extracted_data = updated
    draft.validation_errors = errors

    await db.commit()
    await db.refresh(draft)

    return {
        "draft_id": str(draft.id),
        "validation_errors": errors,
        "extracted_data": updated,
    }
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories import invoice_repository
from app.schemas.invoice import InvoiceResponse

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("/", response_model=list[InvoiceResponse])
async def list_invoices(
    job_id: UUID | None = None,
    status: str | None = Query(default=None, max_length=30),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await invoice_repository.list_invoices(
        db,
        job_id=job_id,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    invoice = await invoice_repository.get_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    return invoice

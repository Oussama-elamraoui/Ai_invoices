from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.processing_job import ProcessingJob
from app.schemas.invoice import InvoiceConfirmInput
from app.services.entity_service import require_entities


CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


async def confirm_invoice(
    db: AsyncSession,
    draft_id: UUID,
    payload: InvoiceConfirmInput,
):
    async with db.begin():
        # Lock the draft invoice to prevent concurrent confirmation.
        invoice = await db.scalar(
            select(Invoice)
            .where(Invoice.id == draft_id)
            .with_for_update()
        )

        if not invoice:
            raise HTTPException(404, "Invoice draft not found")

        if invoice.status == "CONFIRMED":
            raise HTTPException(409, "Invoice already confirmed")

        if invoice.status != "DRAFT":
            raise HTTPException(409, "Invoice is not confirmable")

        await require_entities(
            db, payload.supplier_id, payload.client_id
        )

        invoice.supplier_id = payload.supplier_id
        invoice.client_id = payload.client_id
        invoice.invoice_number = payload.invoice_number
        invoice.invoice_date = payload.invoice_date
        invoice.due_date = payload.due_date
        invoice.currency = payload.currency
        invoice.notes = payload.notes

        subtotal = Decimal("0.00")
        tax_total = Decimal("0.00")

        # Replace the draft's items with the user's reviewed items.
        invoice.items.clear()
        await db.flush()

        for index, item in enumerate(payload.items, start=1):
            line_subtotal = money(item.quantity * item.unit_price)
            tax_amount = money(
                line_subtotal * item.tax_rate / Decimal("100")
            )
            line_total = line_subtotal + tax_amount

            subtotal += line_subtotal
            tax_total += tax_amount

            invoice.items.append(
                InvoiceItem(
                    line_number=index,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    tax_rate=item.tax_rate,
                    subtotal=line_subtotal,
                    tax_amount=tax_amount,
                    line_total=line_total,
                    product_code=item.product_code,
                )
            )

        invoice.subtotal = money(subtotal)
        invoice.tax_total = money(tax_total)
        invoice.total = money(subtotal + tax_total)
        invoice.status = "CONFIRMED"

        from datetime import datetime, timezone
        invoice.confirmed_at = datetime.now(timezone.utc)

    return invoice


async def create_draft(
    db: AsyncSession,
    job_id: UUID,
    supplier_id: UUID,
    client_id: UUID,
    invoice_number: str,
    invoice_date,
    currency: str = "MAD",
):
    job = await db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(404, "Processing job not found")

    invoice = Invoice(
        processing_job_id=job_id,
        supplier_id=supplier_id,
        client_id=client_id,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        currency=currency,
        status="DRAFT",
    )

    db.add(invoice)
    await db.flush()
    await db.refresh(invoice)
    return invoice
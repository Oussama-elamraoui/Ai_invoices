from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.invoice_draft import InvoiceDraft
from app.schemas.invoice import InvoiceConfirmInput
from app.services.entity_service import require_entities


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


async def confirm_draft(
    db: AsyncSession,
    draft_id: UUID,
    payload: InvoiceConfirmInput,
):
    async with db.begin():
        draft = await db.scalar(
            select(InvoiceDraft)
            .where(InvoiceDraft.id == draft_id)
            .with_for_update()
        )

        if not draft:
            raise HTTPException(404, "Draft not found")

        if draft.status == "CONFIRMED":
            raise HTTPException(409, "Draft already confirmed")

        if draft.status != "PENDING_REVIEW":
            raise HTTPException(409, "Draft is not ready for confirmation")

        await require_entities(
            db,
            payload.supplier_id,
            payload.client_id,
        )

        invoice = Invoice(
            supplier_id=payload.supplier_id,
            client_id=payload.client_id,
            processing_job_id=draft.processing_job_id,
            invoice_number=payload.invoice_number,
            invoice_date=payload.invoice_date,
            due_date=payload.due_date,
            currency=payload.currency,
            notes=payload.notes,
            source_filename=draft.source_filename,
            status="CONFIRMED",
            confirmed_at=datetime.now(timezone.utc),
        )

        subtotal = Decimal("0.00")
        tax_total = Decimal("0.00")

        for line_number, item in enumerate(payload.items, start=1):
            line_subtotal = money(item.quantity * item.unit_price)
            tax_amount = money(
                line_subtotal * item.tax_rate / Decimal("100")
            )
            line_total = line_subtotal + tax_amount

            subtotal += line_subtotal
            tax_total += tax_amount

            invoice.items.append(
                InvoiceItem(
                    line_number=line_number,
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

        db.add(invoice)
        await db.flush()

        draft.status = "CONFIRMED"
        draft.confirmed_invoice_id = invoice.id

    return invoice
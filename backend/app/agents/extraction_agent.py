import base64
import mimetypes
from pathlib import Path

import pymupdf as fitz
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from app.core.config import settings


class InvoiceItemData(BaseModel):
    description: str
    quantity: float | None = None
    unit_price: float | None = None
    tax_rate: float | None = None
    product_code: str | None = None


class InvoiceData(BaseModel):
    supplier_name: str | None = None
    supplier_tax_id: str | None = None
    client_name: str | None = None
    invoice_number: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    currency: str | None = None
    items: list[InvoiceItemData] = Field(default_factory=list)
    notes: str | None = None


def load_images(file_path: str) -> list[str]:
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        document = fitz.open(path)
        images = []

        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            encoded = base64.b64encode(pixmap.tobytes("png")).decode()
            images.append(f"data:image/png;base64,{encoded}")

        return images

    mime_type = mimetypes.guess_type(path)[0]

    if mime_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValueError("Unsupported invoice file type")

    encoded = base64.b64encode(path.read_bytes()).decode()
    return [f"data:{mime_type};base64,{encoded}"]


async def extract_invoice(file_path: str) -> dict:
    if (
        settings.OPENAI_API_KEY is None
        or not settings.OPENAI_API_KEY.get_secret_value().strip()
    ):
        raise RuntimeError(
            "Set OPENAI_API_KEY in .env before processing invoices."
        )

    images = load_images(file_path)

    message_content = [
        {
            "type": "text",
            "text": (
                "Extract invoice information accurately. "
                "Do not invent missing values. Use null when unknown. "
                "Preserve invoice item quantities, prices and tax rates. "
                "Return dates in YYYY-MM-DD format when possible."
            ),
        }
    ]

    for image_url in images:
        message_content.append({
            "type": "image_url",
            "image_url": {"url": image_url},
        })

    extractor = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
        model=settings.OPENAI_MODEL,
        temperature=0,
    ).with_structured_output(InvoiceData)

    result = await extractor.ainvoke([
        {"role": "user", "content": message_content}
    ])

    return result.model_dump(mode="json")
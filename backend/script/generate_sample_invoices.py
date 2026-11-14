"""Generate synthetic PDF invoices and a ZIP batch using only the standard library."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


OUTPUT_DIR = Path(__file__).resolve().parents[1] / "sample_invoices"

INVOICES = {
    "01_standard_mad.pdf": [[
        "INVOICE",
        "Atlas Office Supplies (DEMO)",
        "Supplier tax ID: MA-SAMPLE-001",
        "BILL TO: Northstar Design Studio (DEMO)",
        "Invoice number: DEMO-2026-001",
        "Invoice date: 2026-10-12    Due date: 2026-11-11",
        "Currency: MAD",
        "",
        "DESCRIPTION                 QTY       UNIT PRICE       TAX",
        "A4 copy paper                 10          150.00        20%",
        "Ink cartridge                 2           320.00        20%",
        "",
        "Subtotal: MAD 2,140.00",
        "Tax: MAD 428.00",
        "TOTAL DUE: MAD 2,568.00",
        "Payment terms: Net 30 days",
    ]],
    "02_mixed_tax_eur.pdf": [[
        "INVOICE",
        "Lumen Cloud Services (DEMO)",
        "Supplier tax ID: EU-SAMPLE-002",
        "BILL TO: Northstar Design Studio (DEMO)",
        "Invoice number: DEMO-2026-002",
        "Invoice date: 2026-10-15    Due date: 2026-11-14",
        "Currency: EUR",
        "",
        "DESCRIPTION                 QTY       UNIT PRICE       TAX",
        "Monthly hosting               3            40.00        10%",
        "Implementation support        2            75.00        20%",
        "",
        "Subtotal: EUR 270.00",
        "Tax: EUR 42.00",
        "TOTAL DUE: EUR 312.00",
        "Reference: Workspace migration",
    ]],
    "03_incomplete_review.pdf": [[
        "INVOICE",
        "Cedar Consulting (DEMO)",
        "Supplier tax ID: MA-SAMPLE-003",
        "BILL TO: Northstar Design Studio (DEMO)",
        "Invoice number:",
        "Invoice date: 2026-10-18",
        "Currency: MAD",
        "",
        "DESCRIPTION                 QTY       UNIT PRICE       TAX",
        "Consulting session            1          1,200.00        20%",
        "Travel reimbursement          1            180.00         0%",
        "",
        "Subtotal: MAD 1,380.00",
        "Tax: MAD 240.00",
        "TOTAL DUE: MAD 1,620.00",
        "Note: Invoice number was omitted from the source document.",
    ]],
    "04_multi_page.pdf": [
        [
            "INVOICE",
            "Marigold Furniture (DEMO)",
            "Supplier tax ID: MA-SAMPLE-004",
            "BILL TO: Northstar Design Studio (DEMO)",
            "Invoice number: DEMO-2026-004",
            "Invoice date: 2026-10-20    Due date: 2026-11-19",
            "Currency: MAD",
            "",
            "DESCRIPTION                 QTY       UNIT PRICE       TAX",
            "Studio desk                   2          2,400.00        20%",
            "Ergonomic chair               4          1,150.00        20%",
            "",
            "Continued on page 2",
        ],
        [
            "INVOICE DEMO-2026-004 - PAGE 2",
            "DESCRIPTION                 QTY       UNIT PRICE       TAX",
            "Desk lamp                     3            280.00        20%",
            "Delivery fee                  1            350.00         0%",
            "",
            "Subtotal: MAD 10,590.00",
            "Tax: MAD 2,968.00",
            "TOTAL DUE: MAD 13,558.00",
            "Payment terms: Net 30 days",
        ],
    ],
    "05_rif_tech_mad.pdf": [[
        "INVOICE",
        "Rif Tech Solutions (DEMO)",
        "Address: 18 Avenue Hassan II, Rabat, Morocco",
        "Supplier tax ID: MA-SAMPLE-005",
        "Supplier ICE: 002345678000067",
        "Email: billing@riftech.example    Phone: +212 537 00 00 05",
        "BILL TO: Northstar Design Studio (DEMO)",
        "Client address: 42 Rue Oued Ziz, Casablanca, Morocco",
        "Client tax ID: MA-SAMPLE-CLIENT-001",
        "Client ICE: 001234567000089",
        "Invoice number: DEMO-2026-005",
        "Invoice date: 2026-10-22    Due date: 2026-11-21",
        "Currency: MAD",
        "",
        "DESCRIPTION                 QTY       UNIT PRICE       TAX",
        "Workstation computer          2        8,500.00        20%",
        "Business software license     5        1,200.00        20%",
        "Delivery and setup             1          450.00         0%",
        "",
        "Subtotal: MAD 23,450.00",
        "Tax: MAD 4,600.00",
        "TOTAL DUE: MAD 28,050.00",
        "Payment terms: Net 30 days",
        "Payment method: Bank transfer",
        "Bank: Demo Bank Maroc    IBAN: MA64 0000 0000 0000 0000 0000 005",
        "Reference: DEMO-2026-005",
    ]],
    "06_blue_dune_mad.pdf": [[
        "INVOICE",
        "Blue Dune Printworks (DEMO)",
        "Address: 7 Avenue des FAR, Marrakech, Morocco",
        "Supplier tax ID: MA-SAMPLE-006",
        "Supplier ICE: 003456789000078",
        "Email: accounts@bluedune.example    Phone: +212 524 00 00 06",
        "BILL TO: Northstar Design Studio (DEMO)",
        "Client address: 42 Rue Oued Ziz, Casablanca, Morocco",
        "Client tax ID: MA-SAMPLE-CLIENT-001",
        "Client ICE: 001234567000089",
        "Invoice number: DEMO-2026-006",
        "Invoice date: 2026-10-24    Due date: 2026-11-23",
        "Currency: MAD",
        "",
        "DESCRIPTION                 QTY       UNIT PRICE       TAX",
        "A4 marketing brochures       500            8.00        20%",
        "Business cards             1000            1.50        20%",
        "Artwork and setup fee          1          700.00        20%",
        "",
        "Subtotal: MAD 6,200.00",
        "Tax: MAD 1,240.00",
        "TOTAL DUE: MAD 7,440.00",
        "Payment terms: Net 30 days",
        "Payment method: Bank transfer",
        "Bank: Demo Bank Maroc    IBAN: MA64 0000 0000 0000 0000 0000 006",
        "Reference: DEMO-2026-006",
    ]],
}


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_page(lines: list[str]) -> bytes:
    commands = []
    y = 744
    for index, line in enumerate(lines):
        size = 18 if index == 0 else 10
        commands.extend([
            "BT",
            f"/F1 {size} Tf",
            f"48 {y} Td",
            f"({pdf_escape(line)}) Tj",
            "ET",
        ])
        y -= 18 if index == 0 else 16
    return ("\n".join(commands) + "\n").encode("ascii")


def make_pdf(pages: list[list[str]]) -> bytes:
    page_ids = [3 + 2 * index for index in range(len(pages))]
    font_id = 3 + 2 * len(pages)
    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: (
            f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] "
            f"/Count {len(pages)} >>"
        ).encode("ascii"),
        font_id: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }

    for index, lines in enumerate(pages):
        page_id = page_ids[index]
        content_id = page_id + 1
        content = make_page(lines)
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        ).encode("ascii")
        objects[content_id] = (
            f"<< /Length {len(content)} >>\nstream\n".encode("ascii")
            + content
            + b"endstream"
        )

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_id in range(1, font_id + 1):
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n".encode("ascii"))
        output.extend(objects[object_id])
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {font_id + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {font_id + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(output)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filenames = []
    for filename, pages in INVOICES.items():
        (OUTPUT_DIR / filename).write_bytes(make_pdf(pages))
        filenames.append(filename)

    with ZipFile(OUTPUT_DIR / "sample_invoices.zip", "w", ZIP_DEFLATED) as archive:
        for filename in filenames:
            archive.write(OUTPUT_DIR / filename, arcname=filename)

    print(f"Generated {len(filenames)} PDFs and {OUTPUT_DIR / 'sample_invoices.zip'}")


if __name__ == "__main__":
    main()

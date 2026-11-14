from decimal import Decimal


def validate_invoice(data: dict) -> list[str]:
    errors = []

    if not data.get("supplier_name"):
        errors.append("Missing supplier name")

    if not data.get("client_name"):
        errors.append("Missing client name")

    if not data.get("invoice_number"):
        errors.append("Missing invoice number")

    if not data.get("invoice_date"):
        errors.append("Missing invoice date")

    items = data.get("items", [])

    if not items:
        errors.append("Invoice has no items")

    for index, item in enumerate(items, start=1):
        if not item.get("description"):
            errors.append(f"Item {index}: missing description")

        quantity = item.get("quantity")
        unit_price = item.get("unit_price")
        tax_rate = item.get("tax_rate")

        if quantity is None or Decimal(str(quantity)) <= 0:
            errors.append(f"Item {index}: invalid quantity")

        if unit_price is None or Decimal(str(unit_price)) < 0:
            errors.append(f"Item {index}: invalid unit price")

        if tax_rate is not None and not (
            Decimal("0") <= Decimal(str(tax_rate)) <= Decimal("100")
        ):
            errors.append(f"Item {index}: invalid tax rate")

    return errors
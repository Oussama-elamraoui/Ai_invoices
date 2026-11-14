from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def reconcile_invoice(data: dict) -> dict:
    subtotal = Decimal("0")
    tax_total = Decimal("0")
    errors = []

    for index, item in enumerate(data.get("items", []), start=1):
        quantity = item.get("quantity")
        unit_price = item.get("unit_price")
        tax_rate = item.get("tax_rate")

        if quantity is None or unit_price is None or tax_rate is None:
            errors.append(f"Item {index}: insufficient data for calculation")
            continue

        quantity = Decimal(str(quantity))
        unit_price = Decimal(str(unit_price))
        tax_rate = Decimal(str(tax_rate))

        line_subtotal = money(quantity * unit_price)
        line_tax = money(line_subtotal * tax_rate / Decimal("100"))

        subtotal += line_subtotal
        tax_total += line_tax

    subtotal = money(subtotal)
    tax_total = money(tax_total)
    total = money(subtotal + tax_total)

    return {
        "calculated_subtotal": str(subtotal),
        "calculated_tax_total": str(tax_total),
        "calculated_total": str(total),
        "errors": errors,
        "status": "NEEDS_REVIEW" if errors else "CALCULATED",
    }
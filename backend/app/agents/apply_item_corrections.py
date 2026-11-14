from copy import deepcopy


def apply_item_corrections(
    invoice_data: dict,
    corrections: list[dict],
) -> dict:
    updated = deepcopy(invoice_data)

    items = updated.get("items", [])

    allowed_fields = {
        "description",
        "quantity",
        "unit_price",
        "tax_rate",
        "product_code",
    }

    for correction in corrections:
        index = correction["item_index"]
        field = correction["field"]
        value = correction["value"]

        if not isinstance(index, int) or isinstance(index, bool):
            raise ValueError("Invalid item index")

        if not 0 <= index < len(items):
            raise ValueError("Item index out of range")

        if field not in allowed_fields:
            raise ValueError("Field cannot be corrected")

        items[index][field] = value

    updated["items"] = items
    return updated
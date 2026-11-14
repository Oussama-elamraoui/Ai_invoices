from copy import deepcopy
from typing import Any


def apply_approved_corrections(
    original_data: dict[str, Any],
    proposed_data: dict[str, Any],
    approved_fields: list[str],
) -> dict[str, Any]:
    unknown_fields = set(approved_fields) - proposed_data.keys()
    if unknown_fields:
        raise ValueError(
            "Approved fields must exist in the proposed corrections."
        )

    updated = deepcopy(original_data)
    for field in approved_fields:
        updated[field] = deepcopy(proposed_data[field])
    return updated

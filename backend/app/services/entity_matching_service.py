from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier
from app.models.client import Client
from app.services.entity_matching_service import (
    match_supplier,
    match_client,
)

async def match_entity(db, model, name, tax_id=None):
    # First: exact tax ID
    if tax_id:
        result = await db.scalars(
            select(model).where(
                model.tax_id == tax_id,
                model.is_active.is_(True),
            )
        )
        matches = list(result.all())
        
        if len(matches) == 1:
            return {
                "status": "MATCHED",
                "entity_id": str(matches[0].id),
                "candidates": [],
            }

    # Second: exact case-insensitive name
    if name:
        result = await db.scalars(
            select(model).where(
                func.lower(func.trim(model.name))
                == name.strip().lower(),
                model.is_active.is_(True),
            ).limit(5)
        )
        matches = list(result.all())

        if len(matches) == 1:
            return {
                "status": "MATCHED",
                "entity_id": str(matches[0].id),
                "candidates": [],
            }

        return {
            "status": "NEEDS_REVIEW",
            "entity_id": None,
            "candidates": [
                {"id": str(item.id), "name": item.name}
                for item in matches
            ],
        }

    return {
        "status": "NEEDS_REVIEW",
        "entity_id": None,
        "candidates": [],
    }


async def match_supplier(db: AsyncSession, data: dict):
    return await match_entity(
        db,
        Supplier,
        data.get("name"),
        data.get("tax_id"),
    )


async def match_client(db: AsyncSession, data: dict):
    return await match_entity(
        db,
        Client,
        data.get("name"),
        data.get("tax_id"),
    )
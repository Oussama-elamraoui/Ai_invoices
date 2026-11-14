from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.entity_service import search_suppliers, search_clients
from app.schemas.supplier import SupplierCreate, SupplierResponse
from app.schemas.client import ClientCreate, ClientResponse
from app.repositories import supplier_repository, client_repository

router = APIRouter(prefix="/entities", tags=["Entities"])


@router.get("/suppliers", response_model=list[SupplierResponse])
async def list_suppliers(
    query: str = Query(default="", max_length=100),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await search_suppliers(db, query, skip, limit)


@router.post("/suppliers", response_model=SupplierResponse, status_code=201)
async def create_supplier(
    payload: SupplierCreate,
    db: AsyncSession = Depends(get_db),
):
    supplier = await supplier_repository.create(
        db, payload.model_dump()
    )
    await db.commit()
    await db.refresh(supplier)
    return supplier


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    supplier = await supplier_repository.get_by_id(db, supplier_id)
    if not supplier:
        raise HTTPException(404, "Supplier not found")
    return supplier


@router.get("/clients", response_model=list[ClientResponse])
async def list_clients(
    query: str = Query(default="", max_length=100),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await search_clients(db, query, skip, limit)


@router.post("/clients", response_model=ClientResponse, status_code=201)
async def create_client(
    payload: ClientCreate,
    db: AsyncSession = Depends(get_db),
):
    client = await client_repository.create(
        db, payload.model_dump()
    )
    await db.commit()
    await db.refresh(client)
    return client


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    client = await client_repository.get_by_id(db, client_id)
    if not client:
        raise HTTPException(404, "Client not found")
    return client
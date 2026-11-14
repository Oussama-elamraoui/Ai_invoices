from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.entities import router as entities_router
from app.api.routes.invoice_drafts import router as invoice_drafts_router
from app.api.routes.invoices import router as invoices_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.uploads import router as uploads_router
from app.core.config import settings
from app.core.database import close_database, engine
from app.models import Base


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.AUTO_CREATE_TABLES:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    yield
    await close_database()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG and settings.ENVIRONMENT == "development",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.APP_NAME,
    }


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {
        "message": "Invoice AI API is running",
        "docs": "/docs",
    }


for router in (
    invoice_drafts_router,
    uploads_router,
    jobs_router,
    entities_router,
    invoices_router,
):
    app.include_router(router, prefix=settings.API_V1_PREFIX)

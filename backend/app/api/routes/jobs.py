from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.processing_job import ProcessingJob
from app.schemas.processing_job import ProcessingJobResponse

router = APIRouter(prefix="/jobs", tags=["Processing Jobs"])


@router.get("/", response_model=list[ProcessingJobResponse])
async def list_jobs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.scalars(
        select(ProcessingJob)
        .order_by(ProcessingJob.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.all())


@router.get("/{job_id}", response_model=ProcessingJobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    job = await db.get(ProcessingJob, job_id)

    if not job:
        raise HTTPException(404, "Job not found")

    return {
        "id": job.id,
        "original_filename": job.original_filename,
        "status": job.status,
        "total_files": job.total_files,
        "processed_files": job.processed_files,
        "failed_files": job.failed_files,
        "error_message": job.error_message,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "created_at": job.created_at,
    }
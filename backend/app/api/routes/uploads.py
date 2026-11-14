import logging
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db
from app.models.processing_job import ProcessingJob
from app.schemas.processing_job import ProcessingJobResponse
from app.services.zip_processing_service import process_zip

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_DIR = Path("storage/uploads")
MAX_UPLOAD_SIZE = 100 * 1024 * 1024
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def run_processing(job_id: uuid.UUID, zip_path: str) -> None:
    async with AsyncSessionLocal() as db:
        job = await db.get(ProcessingJob, job_id)
        if job is None:
            logger.error("Processing job %s disappeared before execution", job_id)
            return

        try:
            job.status = "PROCESSING"
            await db.commit()

            await process_zip(db, job_id, zip_path)

            job = await db.get(ProcessingJob, job_id)
            if job is not None:
                job.status = (
                    "FAILED"
                    if job.total_files and job.failed_files == job.total_files
                    else "COMPLETED"
                )
                if job.status == "FAILED":
                    job.error_message = (
                        "All invoice files failed. Check AI configuration and server logs."
                    )
                job.completed_at = datetime.now(timezone.utc)
                await db.commit()
        except Exception as exc:
            logger.exception("ZIP processing failed for job %s", job_id)
            await db.rollback()
            job = await db.get(ProcessingJob, job_id)
            if job is not None:
                job.status = "FAILED"
                job.error_message = (
                    str(exc)
                    if isinstance(exc, ValueError)
                    else "ZIP processing failed. Check server logs."
                )
                job.completed_at = datetime.now(timezone.utc)
                await db.commit()
        finally:
            Path(zip_path).unlink(missing_ok=True)


@router.post("/", response_model=ProcessingJobResponse, status_code=202)
async def upload_zip(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(400, "Please upload a ZIP file")

    job_id = uuid.uuid4()
    zip_path = UPLOAD_DIR / f"{job_id}.zip"

    try:
        size = 0
        with zip_path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_SIZE:
                    raise HTTPException(413, "ZIP file exceeds the 100 MB limit")
                output.write(chunk)

        if not zipfile.is_zipfile(zip_path):
            raise HTTPException(400, "Uploaded file is not a valid ZIP archive")

        filename = file.filename.replace("\\", "/").rsplit("/", 1)[-1]
        job = ProcessingJob(
            id=job_id,
            original_filename=filename,
            storage_key=str(zip_path),
            status="PENDING",
        )

        db.add(job)
        await db.commit()
        await db.refresh(job)

        background_tasks.add_task(run_processing, job.id, str(zip_path))
        return job
    except HTTPException:
        await db.rollback()
        zip_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        logger.exception("Could not save uploaded ZIP file")
        await db.rollback()
        zip_path.unlink(missing_ok=True)
        raise HTTPException(500, "Could not upload ZIP file") from exc
    finally:
        await file.close()

import logging
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.invoice_workflow import invoice_workflow
from app.models.invoice_draft import InvoiceDraft
from app.models.processing_job import ProcessingJob
from app.repositories import invoice_draft_repository

logger = logging.getLogger(__name__)

SUPPORTED_FILES = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}
MAX_FILES = 100
MAX_UNCOMPRESSED_SIZE = 100 * 1024 * 1024


async def process_zip(
    db: AsyncSession,
    job_id: UUID,
    zip_path: str,
) -> list[InvoiceDraft]:
    job = await db.get(ProcessingJob, job_id)
    if job is None:
        raise ValueError(f"Processing job {job_id} no longer exists.")

    created_drafts = []
    with zipfile.ZipFile(zip_path, "r") as archive:
        files = [
            item for item in archive.infolist()
            if not item.is_dir()
            and Path(item.filename).suffix.lower() in SUPPORTED_FILES
        ]

        if len(files) > MAX_FILES:
            raise ValueError("ZIP contains too many invoice files.")

        if sum(item.file_size for item in files) > MAX_UNCOMPRESSED_SIZE:
            raise ValueError("ZIP contents exceed the uncompressed size limit.")

        if not files:
            raise ValueError("ZIP contains no supported invoice files.")

        job.total_files = len(files)
        job.started_at = datetime.now(timezone.utc)
        await db.commit()

        with tempfile.TemporaryDirectory() as temp_dir:
            for index, item in enumerate(files):
                filename = Path(item.filename).name
                file_path = Path(temp_dir) / f"{index}_{filename}"

                try:
                    file_path.write_bytes(archive.read(item))
                    result = await invoice_workflow.ainvoke(
                        {"file_path": str(file_path)}
                    )
                    data = result["invoice_data"]
                    data["reconciliation"] = result.get(
                        "reconciliation", {}
                    )
                    data["correction_suggestions"] = result.get(
                        "correction_suggestions"
                    )
                except Exception:
                    logger.exception(
                        "Invoice extraction failed for %s in job %s",
                        filename,
                        job_id,
                    )
                    draft = await invoice_draft_repository.create(
                        db=db,
                        job_id=job_id,
                        filename=filename,
                        extracted_data={},
                    )
                    draft.validation_errors = [
                        "Extraction failed. Check the AI configuration and retry."
                    ]
                    job.failed_files += 1
                else:
                    draft = await invoice_draft_repository.create(
                        db=db,
                        job_id=job_id,
                        filename=filename,
                        extracted_data=data,
                    )
                    job.processed_files += 1

                created_drafts.append(draft)
                await db.commit()

    return created_drafts

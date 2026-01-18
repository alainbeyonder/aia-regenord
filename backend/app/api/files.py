import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.upload import Upload
from app.models.user import User

router = APIRouter(prefix="/files", tags=["files"])

MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024
STORAGE_ROOT = Path("/app/storage/uploads")


@router.post("/upload")
def upload_file(
    file_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_types = {"pl_pdf", "bs_pdf", "loans_pdf"}
    if file_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file_type")
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User has no company")
    if not (file.filename or "").lower().endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    upload = Upload(
        company_id=current_user.company_id,
        user_id=current_user.id,
        file_type=file_type,
        storage_url="",
    )
    db.add(upload)
    db.flush()

    company_dir = STORAGE_ROOT / str(current_user.company_id)
    company_dir.mkdir(parents=True, exist_ok=True)
    target_path = company_dir / f"{upload.id}_{file_type}.pdf"

    size = 0
    try:
        with open(target_path, "wb") as output:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(status_code=413, detail="File too large")
                output.write(chunk)
        upload.storage_url = str(target_path)
        db.commit()
        db.refresh(upload)
        return {"status": "ok", "upload_id": upload.id}
    except HTTPException:
        if target_path.exists():
            os.remove(target_path)
        db.rollback()
        raise
    except Exception:
        if target_path.exists():
            os.remove(target_path)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to store file")


@router.get("/list")
def list_uploads(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.company_id:
        raise HTTPException(status_code=400, detail="User has no company")
    uploads = (
        db.query(Upload)
        .filter(Upload.company_id == current_user.company_id)
        .order_by(Upload.created_at.desc())
        .all()
    )
    return {
        "uploads": [
            {
                "id": upload.id,
                "company_id": upload.company_id,
                "user_id": upload.user_id,
                "file_type": upload.file_type,
                "storage_url": upload.storage_url,
                "created_at": upload.created_at.isoformat(),
            }
            for upload in uploads
        ]
    }

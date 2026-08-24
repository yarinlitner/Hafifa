from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

import schemas
from database import get_db
from logger import logger
from services import upload

router = APIRouter(tags=["Upload"])

@router.post("/upload", response_model=schemas.UploadResponse)
def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.endswith(".csv"):
        logger.warning(
            f"Failed upload attempt with invalid file: "
            f"{file.filename}"
        )
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file",
        )

    logger.info(
        f"Processing CSV file upload: {file.filename}"
    )

    try:
        content = file.file.read().decode("utf-8")
    except UnicodeDecodeError:
        logger.warning(
            f"Failed to decode uploaded file: {file.filename}"
        )
        raise HTTPException(
            status_code=400,
            detail="File must be a valid UTF-8 encoded CSV",
        )

    return upload.process_csv(
        content,
        file.filename,
        db,
    )
from pydantic import BaseModel

class UploadResponse(BaseModel):
    message: str
    inserted_rows: int
    skipped_rows: list[int]
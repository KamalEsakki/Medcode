from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CaseDocumentCreate(BaseModel):
    filename: str
    file_type: str = "Clinical Document"
    file_size_bytes: int = 10240
    download_url: Optional[str] = None
    uploaded_by: Optional[str] = "Medical Scrubber"

class CaseDocumentResponse(BaseModel):
    id: str
    session_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    download_url: Optional[str] = None
    uploaded_by: str
    created_at: datetime

    class Config:
        from_attributes = True

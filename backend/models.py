from pydantic import BaseModel

class Query(BaseModel):
    message: str
    session_id: str

class FileUpload(BaseModel):
    file_path: str
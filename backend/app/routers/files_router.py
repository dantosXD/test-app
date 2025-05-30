import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from starlette.responses import FileResponse

from .. import auth, models # For current_user dependency
from ..config import settings # If you have path settings, otherwise define here

router = APIRouter(
    prefix="/files",
    tags=["files"],
)

# Define upload directory relative to the backend root
# Ensure this directory exists and is writable by the application.
# For this example, assuming it's in `backend/uploads/`
UPLOAD_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

class FileMetadataResponse(schemas.BaseModel): # Assuming schemas is available or define here
    filename: str # The unique filename stored on server
    original_filename: str
    content_type: Optional[str] = None
    size: int # In bytes
    url: str


@router.post("/upload", response_model=FileMetadataResponse, dependencies=[Depends(auth.get_current_active_user)])
async def upload_file(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file sent")

    original_filename = file.filename
    content_type = file.content_type
    
    # Generate a unique filename to prevent overwrites and handle special characters
    file_extension = os.path.splitext(original_filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
    
    size = 0
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read() # Read file content
            buffer.write(content)
            size = len(content)
    except Exception as e:
        # Log error e
        raise HTTPException(status_code=500, detail=f"Could not save file: {original_filename}. Error: {str(e)}")
    finally:
        await file.close()

    # Construct the download URL. Adjust host/port if needed or use relative paths if frontend and backend are same origin.
    # For now, assuming relative URL is fine for frontend to prepend its own origin or a configured backend origin.
    download_url = f"/files/download/{unique_filename}"

    return FileMetadataResponse(
        filename=unique_filename,
        original_filename=original_filename,
        content_type=content_type,
        size=size,
        url=download_url
    )


@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.isfile(file_path): # Security: Check it's a file and not e.g. a directory traversal attempt
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on filename extension if needed, or let browser infer.
    # FileResponse attempts to guess media_type.
    return FileResponse(path=file_path, filename=filename) # filename suggests download name to browser

# Need to import schemas for FileMetadataResponse
from .. import schemas

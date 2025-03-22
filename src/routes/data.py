from fastapi import FastAPI, APIRouter, Depends, UploadFile,status
from fastapi.responses import JSONResponse
import os
import aiofiles
import logging

from helpers.config import get_settings, Settings
from controllers import DataController, Projectcontroller, ProcessController
from models import ResponseSignal
from .schemas.data import ProcessRequest

data_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"]
)

logger = logging.getLogger("uvicorn.error")
 
@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
    
    is_valid, result_signal = DataController().validate_uploaded_file(file)

    if not is_valid:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal
                }
            )

    project_dir_path = Projectcontroller().get_project_path(project_id= project_id)
    file_path = os.path.join(project_dir_path, file.filename)

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOADED_SUCCESS.value
        }
    )


@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, process_request: ProcessRequest):
    file_name = process_request.file_name
    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_name= file_name)
    file_chunks = process_controller.process_file_conent(
        file_content= file_content,
        file_name= file_name,
        chunk_size= process_request.chunk_size,
        chunk_overlap= process_request.overlap_size
    )
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value
            }
        )


    return file_chunks
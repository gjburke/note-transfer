import logging
import os
import shutil

from pydantic import BaseModel

from fastapi import FastAPI, File, UploadFile, Response
from fastapi.responses import JSONResponse
#from fastapi.encoders import jsonable_encoder

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

app = FastAPI()

FILES_FOLDER = os.path.join(os.getcwd(), 'files')
os.makedirs(FILES_FOLDER, exist_ok=True)

@app.post("/upload_files/")
async def upload_files(files: list[UploadFile] = File(...)) -> Response:
    # Handling the input
    if not files:
        return JSONResponse(content={"error" : "No files sent"}, status_code=400)

    # Saving the files
    for file in files:
        # Should proabbly worry about unqiue names, paths, etc eventually
        file_path = os.path.join(FILES_FOLDER, file.filename)

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
    return Response()
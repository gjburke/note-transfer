import logging
import os
import shutil

from pydantic import BaseModel

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
#from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"]
)

FILES_FOLDER = os.path.join(os.getcwd(), 'files')
os.makedirs(FILES_FOLDER, exist_ok=True)

@app.post("/process_file/")
async def process_file(file: UploadFile = File(...)):
    # Handling the input
    if not file:
        return HTTPException(detail="No file sent", status_code=400)

    # Saving the files
    # Should proabbly worry about unqiue names, paths, etc eventually
    file_path = os.path.join(FILES_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
            
    return JSONResponse(content={"markdown": f"We processed {file.filename}"}, status_code=200)
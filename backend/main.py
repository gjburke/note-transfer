import logging
import os
import tempfile
import shutil

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
#from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from transformers import pipeline


# Setting up logger
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

# Setting up FastAPI App
app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"]
)

# Settign up files folder for saving files (may be depreciated)
FILES_FOLDER = os.path.join(os.getcwd(), 'files')
os.makedirs(FILES_FOLDER, exist_ok=True)

# Load model
# use is pipe(<image data>)
transfer = pipeline("image-to-text", model="microsoft/trocr-base-handwritten")

@app.post("/process_file/")
async def process_file(file: UploadFile = File(...)):
    # Handling the input
    if not file:
        return HTTPException(detail="No file sent", status_code=400)

    # Should proabbly worry about unqiue names, paths, etc eventually
    file_path = os.path.join(FILES_FOLDER, file.filename)

    # Save new file
    with open(file_path, "wb") as f: 
        shutil.copyfileobj(file.file, f)

    # Process using text recognition
    result = transfer(file_path)
    if not result:
        os.remove(file_path)
        return HTTPException(detail="No text detected", status_code=500)

    text = result[0]['generated_text']

    os.remove(file_path)
    return JSONResponse(
        content={"markdown": text}, 
        status_code=200
    )

    #return HTTPException(detail="An error occurred during processing", status_code=500)
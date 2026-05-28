import logging
import os
import tempfile
import cv2
import numpy as np
import matplotlib.pyplot as plt
from anytree import RenderTree

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
#from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from pipeline.config import *
from pipeline.segmentation import load_seg_model, get_page_segmentations
from pipeline.structure import get_root, parse_page
from pipeline.recognition import load_text_recognition, detect_text
from pipeline.conversion import markdown_from_nodes

# Setting up logger
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

# Setting up FastAPI App
app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://note-transfer-gjburke.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"]
)

# Settign up files folder for saving files (may be depreciated)
FILES_FOLDER = os.path.join(os.getcwd(), "files")
os.makedirs(FILES_FOLDER, exist_ok=True)

# Load model
# use is pipe(<image data>)
text_model, text_processor = load_text_recognition(BASE_MODEL_NAME, ONNX_PATH)
section_model = load_seg_model(SECTION_MODEL_PATH)
line_model = load_seg_model(LINE_MODEL_PATH)

@app.post("/process_file/")
async def process_file(file: UploadFile = File(...)):
    # Handling the input
    if not file:
        return HTTPException(detail="No file sent", status_code=400)

    contents = await file.read()
    np_image_array = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_image_array, cv2.IMREAD_ANYCOLOR)

    if len(image.shape) == 2: # Grayscale
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 4: # BGRA
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
    else: # Standard BGR
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Pipeline to md
    segmentations = get_page_segmentations(
        image=image,
        section_model=section_model,
        line_model=line_model
    )

    document_root = get_root()
    parse_page(document_root, segmentations, image.shape[0], image.shape[1])

    detect_text(document_root, text_model, text_processor)

    md = markdown_from_nodes(document_root)

    print(f"{md}")

    return JSONResponse(
        content={"markdown": md}, 
        status_code=200
    )

    #return HTTPException(detail="An error occurred during processing", status_code=500)
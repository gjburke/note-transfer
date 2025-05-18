import logging

from pydantic import BaseModel

from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi import Response
#from fastapi.responses import JSONResponse
#from fastapi.encoders import jsonable_encoder

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

app = FastAPI()

@app.post("/upload_files/")
def upload_files(files: list[UploadFile] = File(...)) -> Response:
    for file in files:
        logger.debug(file.filename)
    
    return Response()
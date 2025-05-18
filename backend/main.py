from pydantic import BaseModel

from fastapi import FastAPI
from fastapi import File, UploadFile
from fastapi import Response
#from fastapi.responses import JSONResponse
#from fastapi.encoders import jsonable_encoder

app = FastAPI()

@app.post("/upload_notes/")
def upload_notes(notes: list[UploadFile] = File(...)) -> Response:
    for note in notes:
        print(note.filename)
    
    return Response()
INSTALLATION

Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate
(Windows) venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

NOTE:
Torch can be large. If you have a GPU, install the CUDA-enabled version of PyTorch instead.

RUNNING THE SERVER

From the directory containing your FastAPI file (for example: main.py):

uvicorn main:app --reload

The server will run at:
http://127.0.0.1:8000

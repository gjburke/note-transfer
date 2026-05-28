# Building
FROM python:3.12-slim AS builder
WORKDIR /build

# Install build dependencies if any wheels need compiling
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install packages into a dedicated local directory to copy cleanly over
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime   
FROM python:3.12-slim AS runner
WORKDIR /app

# System deps for OpenCV + torch
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY ./models/ ./models/

COPY main.py .
COPY pipeline/ ./pipeline/

EXPOSE 8080

ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
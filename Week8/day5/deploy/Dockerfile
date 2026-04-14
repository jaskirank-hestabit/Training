# Base 
FROM python:3.10-slim

# Build deps for llama-cpp-python (requires C++ compilation)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps 
COPY requirements.txt .
# CMAKE_ARGS enables CPU-only build; remove and set LLAMA_CUBLAS=1 for GPU
RUN CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS" \
    pip install --no-cache-dir -r requirements.txt

# Copy source 
COPY . .

# Ports 
EXPOSE 8000
EXPOSE 8501

# Default: run API 
CMD ["python", "app.py"]
# Base image with Python and PyTorch
FROM runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install system dependencies (FFmpeg is required for audio processing)
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update -o Acquire::http::No-Cache=True -o Acquire::http::Pipeline-Depth=0 --fix-missing && \
    apt-get install -y \
    ffmpeg \
    libsndfile1 \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clone RVC (Retrieval-based Voice Conversion) repository (if needed for inference script)
# RUN git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git rvc

# Copy the serverless handler
COPY handler.py .

# Run the RunPod serverless handler
CMD ["python", "-u", "handler.py"]

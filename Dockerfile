# Alpha Mask Toolkit Docker Image
# Uses NVIDIA's optimized PyTorch container for best GPU performance

FROM nvcr.io/nvidia/pytorch:23.10-py3

# Metadata
LABEL maintainer="Alpha Mask Toolkit"
LABEL description="AI-powered alpha mask generation using BiRefNet"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install additional Python dependencies not in NVIDIA base image
RUN pip install --no-cache-dir \
    opencv-python \
    scikit-image \
    kornia \
    einops \
    prettytable \
    tabulate \
    huggingface-hub \
    accelerate

# Clone BiRefNet repository
RUN git clone https://github.com/ZhengPeng7/BiRefNet.git

# Download BiRefNet model weights (~844MB)
RUN mkdir -p BiRefNet/checkpoints && \
    cd BiRefNet/checkpoints && \
    wget -O BiRefNet-general.pth \
    "https://github.com/ZhengPeng7/BiRefNet/releases/download/v1/BiRefNet-general-epoch_244.pth"

# Verify model download (should be ~844MB)
RUN ls -lh BiRefNet/checkpoints/BiRefNet-general.pth

# Copy toolkit scripts
COPY *.py ./
COPY README_ALPHA_MASKS.md ./

# Create directories for input/output volume mounting
RUN mkdir -p /app/input /app/output

# Set environment variables
ENV PYTHONPATH="/app/BiRefNet:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1

# Set default configuration for container use
ENV BASE_DIR="/app/input"
ENV MODEL_PATH="/app/BiRefNet/checkpoints/BiRefNet-general.pth"
ENV BIREFNET_PATH="/app/BiRefNet"

# Create a container-friendly version of the main script
COPY docker_entrypoint.py ./

# Default command runs the recommended direct alpha script
CMD ["python", "docker_entrypoint.py"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
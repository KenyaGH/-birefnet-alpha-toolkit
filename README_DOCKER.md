# Alpha Mask Toolkit - Docker Guide

Easy deployment of AI-powered alpha mask generation using Docker containers.

## Quick Start

### 1. Build the Container
```bash
docker build -t alpha-mask-toolkit .
```

### 2. Prepare Your Images
Create a folder structure like this:
```
your_images/
├── Camera1_converted/
│   ├── photo001.jpg
│   ├── photo002.png
│   └── ...
└── Camera2_converted/
    ├── photo003.jpg
    └── ...
```

### 3. Run Alpha Mask Generation
```bash
docker run --gpus all \
  -v /path/to/your_images:/app/input \
  alpha-mask-toolkit
```

**Output:** Creates `Camera1_alpha_mask/`, `Camera2_alpha_mask/` folders with black/white masks.

## Docker Compose (Recommended)

### Setup
```bash
# Create input directory
mkdir input

# Add your image folders
mkdir input/Photos_converted
# Copy your images to input/Photos_converted/

# Run with docker-compose
docker-compose up
```

### Different Processing Modes
```bash
# Direct alpha masks (default)
docker-compose up alpha-mask-toolkit

# RGBA to alpha conversion
docker-compose --profile converter up alpha-mask-converter
```

## Advanced Usage

### Custom Configuration
```bash
# Use different input/output suffixes
docker run --gpus all \
  -v /path/to/images:/app/input \
  -e INPUT_SUFFIX="_photos" \
  -e OUTPUT_SUFFIX="_masks" \
  alpha-mask-toolkit
```

### Different Scripts
```bash
# Run RGBA to alpha converter instead
docker run --gpus all \
  -v /path/to/images:/app/input \
  alpha-mask-toolkit python create_alpha_masks.py
```

### CPU-Only Mode
```bash
# If no GPU available
docker run \
  -v /path/to/images:/app/input \
  alpha-mask-toolkit
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_DIR` | `/app/input` | Input directory path |
| `MODEL_PATH` | `/app/BiRefNet/checkpoints/BiRefNet-general.pth` | Model weights path |
| `BIREFNET_PATH` | `/app/BiRefNet` | BiRefNet repository path |
| `SCRIPT` | `birefnet_direct_alpha.py` | Script to run |
| `CUDA_VISIBLE_DEVICES` | `0` | GPU device to use |

## Volume Mounts

### Required
- `-v /your/images:/app/input` - Your image folders

### Optional
- `-v /your/output:/app/output` - Custom output location
- `-v /your/config.py:/app/config.py` - Custom configuration

## Folder Structure

### Input Expected
```
/app/input/
├── Camera1_converted/     # Folder ending with '_converted'
│   ├── photo001.jpg      # Regular photos
│   └── photo002.png
└── Camera2_converted/
    └── photo003.jpg
```

### Output Created
```
/app/input/
├── Camera1_converted/     # Original images
├── Camera1_alpha_mask/    # Generated alpha masks
│   ├── photo001.png      # Black/white masks
│   └── photo002.png
├── Camera2_converted/
├── Camera2_alpha_mask/
│   └── photo003.png
```

## GPU Requirements

### NVIDIA Docker Runtime
```bash
# Install nvidia-docker (Ubuntu/Debian)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### Check GPU Access
```bash
# Verify GPU access in container
docker run --gpus all alpha-mask-toolkit python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

## Troubleshooting

### "No input folders found"
- Ensure folders end with `_converted`
- Check volume mount path
- Example: `mkdir input/Test_converted`

### "CUDA out of memory"
- Reduce GPU memory usage:
```bash
docker run --gpus all \
  -v /path/to/images:/app/input \
  -e CUDA_VISIBLE_DEVICES=0 \
  --memory=4g \
  alpha-mask-toolkit
```

### "Permission denied"
```bash
# Fix file permissions
sudo chown -R $USER:$USER input/
chmod -R 755 input/
```

### "Model not found"
- Container automatically downloads model during build
- Check internet connection during build
- Rebuild if download failed: `docker build --no-cache -t alpha-mask-toolkit .`

## Performance Tips

### Optimize for Speed
```bash
# Use SSD storage for input/output
# Allocate more shared memory
docker run --gpus all \
  -v /path/to/images:/app/input \
  --shm-size=2g \
  alpha-mask-toolkit
```

### Batch Processing
```bash
# Process multiple folders simultaneously
docker run --gpus all \
  -v /large/dataset:/app/input \
  --memory=8g \
  alpha-mask-toolkit
```

## Examples

### Basic Example
```bash
# Build
docker build -t alpha-mask-toolkit .

# Setup input
mkdir my_photos
mkdir my_photos/Family_converted
cp *.jpg my_photos/Family_converted/

# Process
docker run --gpus all \
  -v ./my_photos:/app/input \
  alpha-mask-toolkit

# Results in: my_photos/Family_alpha_mask/
```

### Production Example
```bash
# docker-compose.yml for production
version: '3.8'
services:
  alpha-processor:
    image: alpha-mask-toolkit:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - /data/input:/app/input
      - /data/output:/app/output
    environment:
      - CUDA_VISIBLE_DEVICES=0
    restart: unless-stopped
```

## Container Information

- **Base Image:** `nvcr.io/nvidia/pytorch:23.10-py3`
- **Size:** ~8GB (includes PyTorch, CUDA, BiRefNet model)
- **GPU:** NVIDIA GPU with CUDA support recommended
- **Memory:** 4-8GB RAM recommended
- **Storage:** ~2GB for model weights + your images

## Build Options

### Custom Build
```bash
# Build with specific tag
docker build -t my-alpha-toolkit:v1.0 .

# Build without cache
docker build --no-cache -t alpha-mask-toolkit .

# Build for specific platform
docker build --platform linux/amd64 -t alpha-mask-toolkit .
```

---

For more information, see `README_ALPHA_MASKS.md` for detailed usage of the underlying scripts.
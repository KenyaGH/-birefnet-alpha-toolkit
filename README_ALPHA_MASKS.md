# Alpha Masks Creation Guide

This documentation provides step-by-step instructions for creating alpha masks from regular photos or videos using BiRefNet and custom scripts.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Step-by-Step Process](#step-by-step-process)
- [Scripts Documentation](#scripts-documentation)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Overview

**Alpha masks** are black and white images where:
- **Black (0)** = Background
- **White (255)** = Person/Foreground object

This guide shows how to create professional-quality alpha masks from regular photos using AI-powered human segmentation.

### Process Flow Options:

**Option 1: Two-Step Process (Original)**
```
Regular Photos → BiRefNet Processing → RGBA Masks → Alpha Masks
    (JPG/PNG)         (AI Segmentation)      (Transparent)     (Black/White)
```

**Option 2: Combined Output (NEW)**
```
Regular Photos → BiRefNet Processing → RGBA Masks + Alpha Masks
    (JPG/PNG)         (AI Segmentation)      (Both outputs simultaneously)
```

**Option 3: Direct Alpha (NEW - Recommended)**
```
Regular Photos → BiRefNet Processing → Alpha Masks
    (JPG/PNG)         (AI Segmentation)      (Black/White only - 2x faster!)
```

## Prerequisites

### System Requirements:
- **Python 3.10+**
- **CUDA-capable GPU** (recommended for speed)
- **8GB+ RAM**
- **2GB+ free storage** (for model weights)

### Required Libraries:
```bash
pip install torch torchvision
pip install Pillow numpy tqdm
pip install opencv-python timm scipy scikit-image kornia einops
pip install prettytable tabulate
pip install huggingface-hub accelerate
```

## Installation

### 1. Clone BiRefNet Repository:
```bash
cd /your/project/directory
git clone https://github.com/ZhengPeng7/BiRefNet.git
```

### 2. Download Model Weights:
```bash
cd BiRefNet
mkdir -p checkpoints
cd checkpoints
wget -O BiRefNet-general.pth "https://github.com/ZhengPeng7/BiRefNet/releases/download/v1/BiRefNet-general-epoch_244.pth"
```

### 3. Verify Installation:
```bash
# Check if model file exists (should be ~844MB)
ls -lh BiRefNet-general.pth
```

## Step-by-Step Process

### Step 1: Prepare Your Images

**Organize your images in folders:**
```
your_project/
├── Cam0_converted/          # Input images
│   ├── frame_000000.png
│   ├── frame_000001.png
│   └── frame_000002.png
├── Cam1_converted/          # More input images
│   └── ...
```

**Supported formats:** PNG, JPG, JPEG
**Recommended:** High-resolution images (1024x1024+) for best results

### Step 2: Choose Your Processing Method

## METHOD 1: Direct Alpha Masks (Recommended - Fastest) ⭐

**Single command for direct alpha masks:**
```bash
python birefnet_direct_alpha.py
```

**Output:**
```
your_project/
├── Cam0_converted/          # Original images
├── Cam0_alpha_mask/        # Black/white alpha masks
├── Cam1_converted/
├── Cam1_alpha_mask/
```

**Advantages:**
- 2x faster processing
- Uses less storage space
- Single step workflow
- Same quality as 2-step process

## METHOD 2: Combined Output (Both RGBA + Alpha)

**Single command for both outputs:**
```bash
python birefnet_combined_output.py
```

**Output:**
```
your_project/
├── Cam0_converted/          # Original images
├── Cam0_mask/              # RGBA masks (transparent background)
├── Cam0_alpha_mask/        # Black/white alpha masks
├── Cam1_converted/
├── Cam1_mask/
├── Cam1_alpha_mask/
```

**Advantages:**
- Get both RGBA and alpha masks
- Single BiRefNet run
- Best for workflows needing both formats

## METHOD 3: Two-Step Process (Original)

**Step 2A: Run BiRefNet Human Segmentation**
```bash
python birefnet_all_folders.py
```

**Step 2B: Convert to Alpha Masks**
```bash
python create_alpha_masks.py
```

**Advantages:**
- Maximum flexibility
- Can process RGBA masks separately later
- Good for experimentation with different thresholds

## Scripts Documentation

### Primary Scripts (Choose One):

### Script 1: `birefnet_direct_alpha.py` ⭐ **RECOMMENDED**
**Purpose:** Direct conversion from photos to alpha masks in one step

**Key Features:**
- **Fastest processing** - 2x faster than 2-step process
- **Minimal storage** - No intermediate RGBA files
- **Same quality** - Uses identical BiRefNet processing
- **Single workflow** - Photos → Alpha masks directly
- GPU acceleration with batch processing
- Configurable thresholds and folder patterns

**Input:** Regular photos with people
**Output:** Black/white alpha masks
**Best for:** Most use cases, production workflows

### Script 2: `birefnet_combined_output.py`
**Purpose:** Create both RGBA and alpha masks simultaneously

**Key Features:**
- **Dual output** - Both RGBA and alpha masks in one run
- **Efficient** - Single BiRefNet processing for both outputs
- **Flexible** - Get transparency and alpha masks together
- **Time-saving** - Faster than running separate scripts
- GPU acceleration with batch processing

**Input:** Regular photos with people
**Output:** RGBA masks + Black/white alpha masks
**Best for:** Workflows needing both formats, VFX pipelines

### Legacy Scripts (Two-Step Process):

### Script 3: `birefnet_all_folders.py`
**Purpose:** AI-powered human segmentation using BiRefNet (Step 1 of 2)

**Key Features:**
- Processes all `*_converted` folders automatically
- Creates corresponding `*_mask` folders
- Uses state-of-the-art BiRefNet model
- GPU acceleration and batch processing

**Input:** Regular photos with people
**Output:** RGBA images with transparent backgrounds

### Script 4: `create_alpha_masks.py`
**Purpose:** Convert RGBA masks to pure black/white alpha masks (Step 2 of 2)

**Key Features:**
- Configurable input/output folder patterns
- Adjustable sensitivity threshold
- Supports multiple image formats
- Progress tracking and error handling

**Input:** RGBA masks (from BiRefNet)
**Output:** Black/white alpha masks

## Configuration

### Direct Alpha Configuration (`birefnet_direct_alpha.py`) - RECOMMENDED:

```python
# MAIN CONFIGURATION - CHANGE THESE FOR YOUR PROJECT
BASE_DIR = "/your/project/directory"           # Your working directory
MODEL_PATH = "/path/to/BiRefNet-general.pth"   # Model weights location
INPUT_SUFFIX = "_converted"                    # Input folder pattern
OUTPUT_SUFFIX = "_alpha_mask"                  # Output folder pattern
ALPHA_THRESHOLD = 128                          # Mask sensitivity (0-255)
INPUT_SIZE = (1024, 1024)                      # Processing resolution
```

### Combined Output Configuration (`birefnet_combined_output.py`):

```python
# MAIN CONFIGURATION - CHANGE THESE FOR YOUR PROJECT
BASE_DIR = "/your/project/directory"           # Your working directory
MODEL_PATH = "/path/to/BiRefNet-general.pth"   # Model weights location
INPUT_SUFFIX = "_converted"                    # Input folder pattern
RGBA_OUTPUT_SUFFIX = "_mask"                   # RGBA folder pattern
ALPHA_OUTPUT_SUFFIX = "_alpha_mask"            # Alpha folder pattern
ALPHA_THRESHOLD = 128                          # Mask sensitivity (0-255)
```

### Legacy Configuration:

**BiRefNet Configuration (`birefnet_all_folders.py`):**
```python
BASE_DIR = "/your/project/directory"           # Your working directory
MODEL_PATH = "/path/to/BiRefNet-general.pth"   # Model weights location
INPUT_SIZE = (1024, 1024)                      # Processing resolution
BATCH_SIZE = 1                                 # Adjust based on GPU memory
```

**Alpha Mask Configuration (`create_alpha_masks.py`):**
```python
BASE_DIR = "/your/project/directory"           # Your working directory
INPUT_SUFFIX = "_mask"                         # Input folder pattern
OUTPUT_SUFFIX = "_alpha_mask"                  # Output folder pattern
ALPHA_THRESHOLD = 128                          # Mask sensitivity (0-255)
SUPPORTED_EXTENSIONS = [".png", ".jpg"]       # File types to process
```

### Threshold Guide:
- **ALPHA_THRESHOLD = 50**: More inclusive (captures subtle edges)
- **ALPHA_THRESHOLD = 128**: Balanced (recommended default)
- **ALPHA_THRESHOLD = 200**: Stricter (cleaner masks, may lose details)

## Troubleshooting

### Common Issues:

#### 1. "Model weights not found"
```bash
# Solution: Download model weights
cd BiRefNet/checkpoints
wget -O BiRefNet-general.pth "https://github.com/ZhengPeng7/BiRefNet/releases/download/v1/BiRefNet-general-epoch_244.pth"
```

#### 2. "CUDA out of memory"
```python
# Solution: Reduce batch size in birefnet_all_folders.py
BATCH_SIZE = 1  # or even smaller input size
INPUT_SIZE = (512, 512)  # reduce resolution
```

#### 3. "No folders found"
- Check `INPUT_SUFFIX` matches your folder names
- Verify `BASE_DIR` path is correct
- Ensure folders contain supported image files

#### 4. "Poor mask quality"
- Adjust `ALPHA_THRESHOLD` (try 50-200 range)
- Check input image quality/resolution
- Verify lighting conditions in original photos

#### 5. "Permission denied"
```bash
# Solution: Fix file permissions
chmod +x *.py
chmod -R 755 your_project_directory
```

### Performance Tips:

1. **GPU Usage:**
   ```python
   # Check if CUDA is available
   import torch
   print(torch.cuda.is_available())
   ```

2. **Memory Optimization:**
   - Process smaller batches
   - Use lower resolution for testing
   - Close other GPU applications

3. **Speed Optimization:**
   - Use SSD storage
   - Ensure sufficient RAM
   - Process images in batches

## Examples

### Example 1: Quick Start (Recommended)
```bash
# 1. Setup
mkdir my_project
cd my_project

# 2. Create input folder
mkdir Cam0_converted
# Copy your images to Cam0_converted/

# 3. Run direct alpha mask creation (one step!)
python birefnet_direct_alpha.py
# Done! Check Cam0_alpha_mask/ folder
```

### Example 2: Combined Output
```bash
# Same setup as above, then:
python birefnet_combined_output.py
# Creates both Cam0_mask/ and Cam0_alpha_mask/ folders
```

### Example 3: Legacy Two-Step Process
```bash
# Same setup as above, then:
python birefnet_all_folders.py      # Step 1: Create RGBA masks
python create_alpha_masks.py        # Step 2: Convert to alpha masks
```

### Example 2: Custom Configuration
```python
# Edit create_alpha_masks.py for different naming:
BASE_DIR = "/home/user/video_project"
INPUT_SUFFIX = "_processed"        # Look for *_processed folders
OUTPUT_SUFFIX = "_binary_mask"     # Create *_binary_mask folders
ALPHA_THRESHOLD = 150              # Stricter masking
```

### Example 3: Different Input Types

**For video frames:**
```bash
# Extract frames from video first
ffmpeg -i video.mp4 -vf fps=30 frame_%06d.png

# Then follow normal process
```

**For batch photos:**
```bash
# Organize photos in folders
mkdir Person1_photos Person2_photos
# Copy respective photos to each folder
# Run scripts
```

## File Structure Reference

### Complete Project Structure:
```
your_project/
├── BiRefNet/                       # Cloned repository
│   ├── models/
│   ├── checkpoints/
│   │   └── BiRefNet-general.pth    # Downloaded model weights
│   └── ...
├── alpha_mask_toolkit/             # Toolkit folder
│   ├── birefnet_direct_alpha.py    # RECOMMENDED: Direct alpha masks
│   ├── birefnet_combined_output.py # Both RGBA + alpha masks
│   ├── birefnet_all_folders.py     # Legacy: RGBA masks only
│   ├── create_alpha_masks.py       # Legacy: RGBA → alpha conversion
│   └── README_ALPHA_MASKS.md       # This documentation
├── Cam0_converted/                 # Input: Original photos
│   ├── frame_000000.png
│   └── ...
├── Cam0_mask/                      # Output: RGBA masks (if using combined/legacy)
│   ├── frame_000000.png            # Person with transparent background
│   └── ...
├── Cam0_alpha_mask/                # Output: Black/white alpha masks
│   ├── frame_000000.png            # Black background, white person
│   └── ...
```

### Processing Method Comparison:

| Method | Commands | Speed | Storage | Use Case |
|--------|----------|-------|---------|----------|
| **Direct Alpha** ⭐ | `python birefnet_direct_alpha.py` | **Fastest** | **Minimal** | Alpha masks only |
| **Combined Output** | `python birefnet_combined_output.py` | Fast | Medium | Need both formats |
| **Legacy Two-Step** | `python birefnet_all_folders.py`<br>`python create_alpha_masks.py` | Slower | Most | Experimentation |

## Quality Guidelines

### Input Image Requirements:
- **Resolution:** 1024x1024+ recommended
- **Format:** PNG (best), JPG (good)
- **Content:** Clear person with decent lighting
- **Background:** Any (AI removes automatically)

### Expected Results:
- **BiRefNet masks:** Precise human segmentation with soft edges
- **Alpha masks:** Clean black/white silhouettes
- **Quality:** Professional-grade for VFX/compositing

### When to Use:
- **VFX compositing:** Replace/remove backgrounds
- **Motion capture:** Person tracking reference
- **AI training:** Dataset preparation
- **Video editing:** Professional masking workflows

## Support & Updates

### Getting Help:
1. Check this documentation first
2. Verify configuration settings
3. Test with smaller datasets
4. Check BiRefNet repository for updates

### Version Information:
- **BiRefNet:** Latest from GitHub releases
- **Scripts:** Custom implementation
- **Python:** 3.10+ required
- **CUDA:** 11.8+ recommended

---

**Created for professional alpha mask generation workflows**
*Last updated: September 2025*
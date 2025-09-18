#!/usr/bin/env python3
"""
BiRefNet Direct Alpha Masks - Skip RGBA step, go straight to black/white alpha masks
Processes input folders → creates alpha mask folders directly

This script uses BiRefNet AI model to create alpha masks from photos containing people.
Alpha masks are black/white images where:
- Black (0) = Background
- White (255) = Person/Foreground object
"""

import os
import sys
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
from torchvision import transforms
from tqdm import tqdm
from pathlib import Path

# ============================================================================
# USER CONFIGURATION - EDIT THESE VALUES FOR YOUR PROJECT
# ============================================================================

# REQUIRED: Set your project paths
BASE_DIR = "/path/to/your/project"  # TODO: Change this to your project directory
MODEL_PATH = "./BiRefNet/checkpoints/BiRefNet-general.pth"  # Path to BiRefNet model weights
BIREFNET_PATH = "./BiRefNet"  # Path to BiRefNet repository

# Input/Output folder patterns
INPUT_SUFFIX = "_converted"          # Look for folders ending with this (e.g., "Cam0_converted")
OUTPUT_SUFFIX = "_alpha_mask"        # Alpha masks folder suffix (e.g., "Cam0_alpha_mask")

# Processing settings
INPUT_SIZE = (1024, 1024)           # Image processing resolution (higher = better quality, slower)
ALPHA_THRESHOLD = 128               # 0-255, controls mask sensitivity
                                   # 50 = more inclusive (captures subtle edges)
                                   # 128 = balanced (recommended)
                                   # 200 = stricter (cleaner masks, may lose details)

# Hardware settings
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ============================================================================
# AUTOMATIC SETUP - Do not modify unless you know what you're doing
# ============================================================================

# Add BiRefNet to Python path
if os.path.exists(BIREFNET_PATH):
    sys.path.append(BIREFNET_PATH)
else:
    print(f"ERROR: BiRefNet not found at {BIREFNET_PATH}")
    print("Please ensure BiRefNet is cloned to the correct location")
    sys.exit(1)

try:
    from models.birefnet import BiRefNet
    from utils import check_state_dict
except ImportError as e:
    print(f"ERROR: Failed to import BiRefNet modules: {e}")
    print("Please ensure BiRefNet is properly installed and BIREFNET_PATH is correct")
    sys.exit(1)

# ============================================================================
# BIREFNET DIRECT ALPHA PROCESSOR
# ============================================================================

class BiRefNetDirectAlphaProcessor:
    def __init__(self):
        print(f"Loading BiRefNet model on {DEVICE}...")

        # Initialize model
        self.model = BiRefNet(bb_pretrained=False)

        # Load weights
        if os.path.exists(MODEL_PATH):
            state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
            if 'module.' in list(state_dict.keys())[0]:
                state_dict = check_state_dict(state_dict, unwanted_prefix='module.')
            self.model.load_state_dict(state_dict)
        else:
            raise FileNotFoundError(f"Model weights not found at {MODEL_PATH}")

        self.model.to(DEVICE)
        self.model.eval()

        # Standard ImageNet normalization
        self.normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )

        print(f"✓ BiRefNet model loaded successfully on {DEVICE}")

    def preprocess_image(self, image):
        """Preprocess image for BiRefNet"""
        original_size = image.size
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = image.resize(INPUT_SIZE, Image.Resampling.LANCZOS)
        image_tensor = transforms.ToTensor()(image)
        image_tensor = self.normalize(image_tensor)
        return image_tensor, original_size

    def postprocess_to_alpha_mask(self, mask, original_size, threshold=ALPHA_THRESHOLD):
        """Postprocess model output directly to black/white alpha mask"""
        # Apply sigmoid to get probabilities
        mask = torch.sigmoid(mask)

        # Resize to original size
        mask = F.interpolate(
            mask.unsqueeze(0),
            size=(original_size[1], original_size[0]),
            mode='bilinear',
            align_corners=False
        ).squeeze(0)

        # Convert to numpy
        mask = mask.cpu().numpy().squeeze()

        # Convert directly to black/white alpha mask
        # Values above threshold = white (255), below = black (0)
        alpha_mask = (mask > (threshold / 255.0)).astype(np.uint8) * 255

        return alpha_mask

    @torch.no_grad()
    def process_image_to_alpha(self, image):
        """Process single image directly to alpha mask"""
        tensor, orig_size = self.preprocess_image(image)
        batch = tensor.unsqueeze(0).to(DEVICE)

        # Run BiRefNet inference
        outputs = self.model(batch)
        if isinstance(outputs, list):
            mask = outputs[-1]
        else:
            mask = outputs

        # Convert directly to alpha mask
        alpha_mask = self.postprocess_to_alpha_mask(mask[0], orig_size)
        return alpha_mask

def process_folder(processor, input_folder, output_folder):
    """Process all PNG files in a folder - create alpha masks directly"""
    print(f"\n--- Processing {Path(input_folder).name} → {Path(output_folder).name} ---")

    # Create output directory
    os.makedirs(output_folder, exist_ok=True)

    # Get supported image files
    image_files = []
    for ext in ['.png', '.jpg', '.jpeg']:
        image_files.extend(Path(input_folder).glob(f"*{ext}"))
        image_files.extend(Path(input_folder).glob(f"*{ext.upper()}"))

    if not image_files:
        print(f"No image files found in {input_folder}")
        return

    print(f"Found {len(image_files)} image files")

    success_count = 0
    for img_path in tqdm(image_files, desc="Creating alpha masks"):
        try:
            # Load image
            image = Image.open(img_path)

            # Generate alpha mask directly from BiRefNet
            alpha_mask = processor.process_image_to_alpha(image)

            # Save as black/white PNG
            alpha_image = Image.fromarray(alpha_mask, mode='L')
            output_file = Path(output_folder) / f"{img_path.stem}.png"
            alpha_image.save(output_file, 'PNG')

            success_count += 1

        except Exception as e:
            print(f"Error processing {img_path.name}: {e}")
            continue

    print(f"✓ {success_count}/{len(image_files)} alpha masks created in {Path(output_folder).name}")

def find_input_folders(base_directory, suffix):
    """Find all folders ending with specified suffix"""
    base_path = Path(base_directory)
    if not base_path.exists():
        print(f"Error: Base directory not found: {base_directory}")
        return []

    folders = [d for d in base_path.iterdir()
              if d.is_dir() and d.name.endswith(suffix)]

    # Filter out backup/temp folders
    exclude_keywords = ['backup', 'temp', 'proper', 'mask', 'alpha']
    folders = [f for f in folders
              if not any(keyword in f.name.lower() for keyword in exclude_keywords)]

    return folders

def main():
    """Main processing function"""
    print("BiRefNet Direct Alpha Masks Generator")
    print("Converts photos directly to black/white alpha masks using AI")
    print("=" * 70)

    # Check configuration
    if BASE_DIR == "/path/to/your/project":
        print("ERROR: Please configure BASE_DIR in the script before running!")
        print("Edit the script and change BASE_DIR to your project directory")
        return

    if not os.path.exists(BASE_DIR):
        print(f"ERROR: Base directory not found: {BASE_DIR}")
        print("Please create the directory or update BASE_DIR in the script")
        return

    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: BiRefNet model not found at: {MODEL_PATH}")
        print("Please download the model weights:")
        print("wget -O BiRefNet-general.pth \"https://github.com/ZhengPeng7/BiRefNet/releases/download/v1/BiRefNet-general-epoch_244.pth\"")
        return

    print(f"Configuration:")
    print(f"  Base Directory: {BASE_DIR}")
    print(f"  Model Path: {MODEL_PATH}")
    print(f"  Input Suffix: '{INPUT_SUFFIX}' (looking for folders like 'Cam0{INPUT_SUFFIX}')")
    print(f"  Output Suffix: '{OUTPUT_SUFFIX}' (will create folders like 'Cam0{OUTPUT_SUFFIX}')")
    print(f"  Alpha Threshold: {ALPHA_THRESHOLD} (lower=more inclusive, higher=stricter)")
    print(f"  Device: {DEVICE}")
    print("=" * 70)

    # Find all input folders
    input_folders = find_input_folders(BASE_DIR, INPUT_SUFFIX)

    if not input_folders:
        print(f"No folders ending with '{INPUT_SUFFIX}' found in {BASE_DIR}")
        print("\nTo use this script:")
        print(f"1. Create folders ending with '{INPUT_SUFFIX}' (e.g., 'Images{INPUT_SUFFIX}')")
        print("2. Put your photos (PNG/JPG) in those folders")
        print("3. Run this script again")
        print("\nExample folder structure:")
        print(f"  {BASE_DIR}/")
        print(f"  ├── Camera1{INPUT_SUFFIX}/")
        print(f"  │   ├── photo001.jpg")
        print(f"  │   └── photo002.png")
        print(f"  └── Camera2{INPUT_SUFFIX}/")
        print(f"      └── photo003.jpg")
        return

    print(f"Found {len(input_folders)} input folders:")
    for folder in sorted(input_folders):
        print(f"  - {folder.name}")

    try:
        # Initialize BiRefNet processor (only once)
        processor = BiRefNetDirectAlphaProcessor()

        # Process each folder
        for input_folder in sorted(input_folders):
            folder_name = input_folder.name

            # Create output folder name
            output_folder_name = folder_name.replace(INPUT_SUFFIX, OUTPUT_SUFFIX)
            output_folder = Path(BASE_DIR) / output_folder_name

            process_folder(processor, str(input_folder), str(output_folder))

        print(f"\n{'='*60}")
        print("✓ All folders processed to alpha masks!")
        print("\nOutput folders created:")
        for folder in sorted(input_folders):
            output_name = folder.name.replace(INPUT_SUFFIX, OUTPUT_SUFFIX)
            print(f"  - {output_name}")

        print(f"\nAlpha masks are pure black/white PNG files:")
        print(f"  - Black (0) = Background")
        print(f"  - White (255) = Person/Foreground")
        print(f"  - Ready for VFX/compositing workflows")

    except Exception as e:
        print(f"Failed to initialize BiRefNet: {e}")
        return

if __name__ == "__main__":
    main()
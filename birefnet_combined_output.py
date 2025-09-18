#!/usr/bin/env python3
"""
BiRefNet Combined Output - Creates both RGBA masks and Alpha masks in one run
Processes *_converted folders → creates both *_mask AND *_alpha_mask folders
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

# Add BiRefNet to path
sys.path.append('/home/kenya/research/repos/BiRefNet')

from models.birefnet import BiRefNet
from utils import check_state_dict

# ============================================================================
# CONFIGURATION - CHANGE THESE VALUES FOR YOUR PROJECT
# ============================================================================

BASE_DIR = "/home/kenya/research/repos/seanalexv2_samples"
MODEL_PATH = "/home/kenya/research/repos/BiRefNet/checkpoints/BiRefNet-general.pth"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
INPUT_SIZE = (1024, 1024)

# Input/Output folder patterns
INPUT_SUFFIX = "_converted"          # Look for folders ending with this
RGBA_OUTPUT_SUFFIX = "_mask"         # RGBA masks folder suffix
ALPHA_OUTPUT_SUFFIX = "_alpha_mask"  # Alpha masks folder suffix

# Alpha mask settings
ALPHA_THRESHOLD = 128                # 0-255, controls mask sensitivity

# ============================================================================
# BIREFNET PROCESSOR
# ============================================================================

class BiRefNetCombinedProcessor:
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

    def postprocess_mask(self, mask, original_size):
        """Postprocess model output to alpha mask"""
        mask = torch.sigmoid(mask)
        mask = F.interpolate(
            mask.unsqueeze(0),
            size=(original_size[1], original_size[0]),
            mode='bilinear',
            align_corners=False
        ).squeeze(0)
        mask = mask.cpu().numpy().squeeze()
        mask = (mask * 255).astype(np.uint8)
        return mask

    @torch.no_grad()
    def process_image(self, image):
        """Process single image with BiRefNet"""
        tensor, orig_size = self.preprocess_image(image)
        batch = tensor.unsqueeze(0).to(DEVICE)
        outputs = self.model(batch)
        if isinstance(outputs, list):
            mask = outputs[-1]
        else:
            mask = outputs
        processed_mask = self.postprocess_mask(mask[0], orig_size)
        return processed_mask

# ============================================================================
# OUTPUT CREATION FUNCTIONS
# ============================================================================

def create_rgba_mask(image, mask):
    """Create RGBA image with transparent background"""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    alpha = Image.fromarray(mask).convert('L')
    image.putalpha(alpha)
    return image

def create_alpha_mask(mask, threshold=ALPHA_THRESHOLD):
    """Create pure black/white alpha mask"""
    alpha_mask = (mask > threshold).astype(np.uint8) * 255
    return Image.fromarray(alpha_mask, mode='L')

def process_folder(processor, input_folder, rgba_output_folder, alpha_output_folder):
    """Process all PNG files in a folder - create both RGBA and alpha masks"""
    print(f"\n--- Processing {Path(input_folder).name} ---")
    print(f"  → RGBA masks: {Path(rgba_output_folder).name}")
    print(f"  → Alpha masks: {Path(alpha_output_folder).name}")

    # Create output directories
    os.makedirs(rgba_output_folder, exist_ok=True)
    os.makedirs(alpha_output_folder, exist_ok=True)

    # Get PNG files
    png_files = [f for f in os.listdir(input_folder) if f.endswith('.png')]

    if not png_files:
        print(f"No PNG files found in {input_folder}")
        return

    print(f"Found {len(png_files)} PNG files")

    for filename in tqdm(png_files, desc="Creating both mask types"):
        try:
            # Load image
            img_path = os.path.join(input_folder, filename)
            image = Image.open(img_path)

            # Generate mask with BiRefNet
            mask = processor.process_image(image)

            # Create RGBA mask (transparent background)
            rgba_result = create_rgba_mask(image, mask)
            rgba_output_file = os.path.join(rgba_output_folder, filename)
            rgba_result.save(rgba_output_file, 'PNG')

            # Create alpha mask (black/white)
            alpha_result = create_alpha_mask(mask)
            alpha_output_file = os.path.join(alpha_output_folder, filename)
            alpha_result.save(alpha_output_file, 'PNG')

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue

    print(f"✓ Completed {Path(input_folder).name}")

def find_input_folders(base_directory, suffix):
    """Find all folders ending with specified suffix"""
    base_path = Path(base_directory)
    if not base_path.exists():
        print(f"Error: Base directory not found: {base_directory}")
        return []

    folders = [d for d in base_path.iterdir()
              if d.is_dir() and d.name.endswith(suffix)]

    # Filter out backup/temp folders
    exclude_keywords = ['backup', 'temp', 'proper']
    folders = [f for f in folders
              if not any(keyword in f.name.lower() for keyword in exclude_keywords)]

    return folders

def main():
    """Main processing function"""
    print("BiRefNet Combined Output - RGBA + Alpha Masks")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Base Directory: {BASE_DIR}")
    print(f"  Input Suffix: '{INPUT_SUFFIX}'")
    print(f"  RGBA Output: '{RGBA_OUTPUT_SUFFIX}'")
    print(f"  Alpha Output: '{ALPHA_OUTPUT_SUFFIX}'")
    print(f"  Alpha Threshold: {ALPHA_THRESHOLD}")
    print(f"  Device: {DEVICE}")
    print("=" * 60)

    # Find all input folders
    input_folders = find_input_folders(BASE_DIR, INPUT_SUFFIX)

    if not input_folders:
        print(f"No folders ending with '{INPUT_SUFFIX}' found in {BASE_DIR}")
        return

    print(f"Found {len(input_folders)} input folders:")
    for folder in sorted(input_folders):
        print(f"  - {folder.name}")

    try:
        # Initialize BiRefNet processor (only once)
        processor = BiRefNetCombinedProcessor()

        # Process each folder
        for input_folder in sorted(input_folders):
            folder_name = input_folder.name

            # Create output folder names
            rgba_folder_name = folder_name.replace(INPUT_SUFFIX, RGBA_OUTPUT_SUFFIX)
            alpha_folder_name = folder_name.replace(INPUT_SUFFIX, ALPHA_OUTPUT_SUFFIX)

            rgba_folder = Path(BASE_DIR) / rgba_folder_name
            alpha_folder = Path(BASE_DIR) / alpha_folder_name

            process_folder(processor, str(input_folder), str(rgba_folder), str(alpha_folder))

        print(f"\n{'='*60}")
        print("✓ All folders processed with combined output!")
        print("\nOutput folders created:")
        for folder in sorted(input_folders):
            rgba_name = folder.name.replace(INPUT_SUFFIX, RGBA_OUTPUT_SUFFIX)
            alpha_name = folder.name.replace(INPUT_SUFFIX, ALPHA_OUTPUT_SUFFIX)
            print(f"  - {rgba_name} (RGBA masks)")
            print(f"  - {alpha_name} (Alpha masks)")

    except Exception as e:
        print(f"Failed to initialize BiRefNet: {e}")
        return

if __name__ == "__main__":
    main()
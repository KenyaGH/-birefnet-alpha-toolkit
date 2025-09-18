#!/usr/bin/env python3
"""
Apply proper BiRefNet to all *_converted folders
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

# Configuration
BASE_DIR = "/home/kenya/research/repos/seanalexv2_samples"
MODEL_PATH = "/home/kenya/research/repos/BiRefNet/checkpoints/BiRefNet-general.pth"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
INPUT_SIZE = (1024, 1024)

class BiRefNetProcessor:
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

def apply_mask_to_image(image, mask):
    """Apply mask to image to create transparent background"""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    alpha = Image.fromarray(mask).convert('L')
    image.putalpha(alpha)
    return image

def process_folder(processor, input_folder, output_folder):
    """Process all PNG files in a folder"""
    print(f"\n--- Processing {Path(input_folder).name} -> {Path(output_folder).name} ---")

    # Create output directory
    os.makedirs(output_folder, exist_ok=True)

    # Get PNG files
    png_files = [f for f in os.listdir(input_folder) if f.endswith('.png')]

    if not png_files:
        print(f"No PNG files found in {input_folder}")
        return

    print(f"Found {len(png_files)} PNG files")

    for filename in tqdm(png_files, desc="BiRefNet masking"):
        try:
            # Load image
            img_path = os.path.join(input_folder, filename)
            image = Image.open(img_path)

            # Generate mask with BiRefNet
            mask = processor.process_image(image)

            # Create transparent PNG
            result = apply_mask_to_image(image, mask)

            # Save result
            output_file = os.path.join(output_folder, filename)
            result.save(output_file, 'PNG')

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue

    print(f"✓ Completed {Path(input_folder).name}")

def main():
    print("BiRefNet Processing - All *_converted Folders")
    print("=" * 50)

    # Find all *_converted folders
    base_path = Path(BASE_DIR)
    converted_folders = [d for d in base_path.iterdir()
                        if d.is_dir() and d.name.endswith('_converted')]

    if not converted_folders:
        print("No *_converted folders found!")
        return

    print(f"Found {len(converted_folders)} converted folders:")
    for folder in converted_folders:
        print(f"  - {folder.name}")

    try:
        # Initialize BiRefNet processor (only once)
        processor = BiRefNetProcessor()
        print("✓ BiRefNet model loaded successfully!")

        # Process each folder
        for converted_folder in converted_folders:
            folder_name = converted_folder.name
            mask_folder_name = folder_name.replace('_converted', '_mask')
            mask_folder = base_path / mask_folder_name

            process_folder(processor, str(converted_folder), str(mask_folder))

        print(f"\n{'='*50}")
        print("✓ All folders processed with BiRefNet!")
        print("\nMask folders created:")
        for folder in converted_folders:
            mask_name = folder.name.replace('_converted', '_mask')
            print(f"  - {mask_name}")

    except Exception as e:
        print(f"Failed to initialize BiRefNet: {e}")
        return

if __name__ == "__main__":
    main()
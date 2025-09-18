#!/usr/bin/env python3
"""
Convert BiRefNet RGBA masks to pure black/white alpha masks
Black = background (0), White = person (255)

USAGE INSTRUCTIONS:
1. Change BASE_DIR to your working directory
2. Change INPUT_SUFFIX to match your input folders (e.g., '_mask', '_converted', etc.)
3. Change OUTPUT_SUFFIX to desired output folder naming (e.g., '_alpha', '_binary', etc.)
4. Adjust ALPHA_THRESHOLD if needed (0-255, higher = stricter person detection)
5. Run the script
"""

import os
import numpy as np
from PIL import Image
from tqdm import tqdm
from pathlib import Path

# ============================================================================
# USER CONFIGURATION - EDIT THESE VALUES FOR YOUR PROJECT
# ============================================================================

# REQUIRED: Set your project directory
BASE_DIR = "/path/to/your/project"  # TODO: Change this to your project directory

# Input folder naming pattern - what suffix to look for
INPUT_SUFFIX = "_mask"  # Look for folders ending with this (e.g., "Cam0_mask")
                       # Common options: "_mask", "_rgba", "_birefnet"

# Output folder naming pattern - what suffix to create
OUTPUT_SUFFIX = "_alpha_mask"  # Create folders with this suffix (e.g., "Cam0_alpha_mask")
                              # Common options: "_alpha", "_alpha_mask", "_binary"

# Alpha threshold for person detection (0-255)
ALPHA_THRESHOLD = 128  # Controls mask sensitivity:
                      # 50 = more inclusive (captures subtle edges)
                      # 128 = balanced (recommended)
                      # 200 = stricter (cleaner masks, may lose details)

# File extensions to process
SUPPORTED_EXTENSIONS = [".png", ".jpg", ".jpeg"]  # Add more formats if needed

# ============================================================================
# CORE FUNCTIONS - Usually don't need to change these
# ============================================================================

def rgba_to_alpha_mask(rgba_image, threshold=ALPHA_THRESHOLD):
    """
    Convert RGBA/RGB image to black/white alpha mask

    Args:
        rgba_image: PIL Image in RGBA or RGB format
        threshold: Alpha threshold for person detection (0-255)

    Returns:
        PIL Image in L (grayscale) format where:
        - Black (0) = background
        - White (255) = person/foreground
    """
    # Convert to numpy array
    rgba_array = np.array(rgba_image)

    # Extract alpha channel or create from image content
    if len(rgba_array.shape) == 3 and rgba_array.shape[2] == 4:  # RGBA
        print("  Processing RGBA image...")
        alpha_channel = rgba_array[:, :, 3]
    elif len(rgba_array.shape) == 3 and rgba_array.shape[2] == 3:  # RGB
        print("  Processing RGB image (no alpha channel)...")
        # If RGB, create alpha from non-black pixels
        gray = np.mean(rgba_array, axis=2)
        alpha_channel = (gray > 10).astype(np.uint8) * 255
    elif len(rgba_array.shape) == 2:  # Grayscale
        print("  Processing grayscale image...")
        alpha_channel = rgba_array
    else:
        raise ValueError(f"Unsupported image format: {rgba_array.shape}")

    # Create black/white mask based on threshold
    # Alpha > threshold = white (person), else black (background)
    alpha_mask = (alpha_channel > threshold).astype(np.uint8) * 255

    # Convert to PIL Image
    return Image.fromarray(alpha_mask, mode='L')

def process_folder(input_folder, output_folder, threshold=ALPHA_THRESHOLD):
    """
    Process all supported image files in folder to create alpha masks

    Args:
        input_folder: Path to input folder
        output_folder: Path to output folder
        threshold: Alpha threshold for processing
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)

    # Create output directory
    output_path.mkdir(exist_ok=True)

    # Get supported image files
    image_files = []
    for ext in SUPPORTED_EXTENSIONS:
        image_files.extend(input_path.glob(f"*{ext}"))
        image_files.extend(input_path.glob(f"*{ext.upper()}"))

    if not image_files:
        print(f"No supported image files found in {input_folder}")
        print(f"Looking for extensions: {SUPPORTED_EXTENSIONS}")
        return

    print(f"Converting {len(image_files)} files to alpha masks...")
    print(f"Using threshold: {threshold}")

    success_count = 0
    for img_path in tqdm(image_files, desc="Creating alpha masks"):
        try:
            # Load image (handles RGBA, RGB, or grayscale)
            image = Image.open(img_path)

            # Convert to alpha mask
            alpha_mask = rgba_to_alpha_mask(image, threshold)

            # Save as grayscale PNG (preserves quality)
            output_file = output_path / f"{img_path.stem}.png"
            alpha_mask.save(output_file, 'PNG')

            success_count += 1

        except Exception as e:
            print(f"Error processing {img_path.name}: {e}")
            continue

    print(f"✓ {success_count}/{len(image_files)} alpha masks saved to {output_folder}")

def process_single_folder(input_folder):
    """
    Process a single input folder and create corresponding output folder

    Args:
        input_folder: Path to folder ending with INPUT_SUFFIX
    """
    folder_name = Path(input_folder).name

    # Create output folder name by replacing suffix
    if folder_name.endswith(INPUT_SUFFIX):
        output_folder_name = folder_name.replace(INPUT_SUFFIX, OUTPUT_SUFFIX)
    else:
        # Fallback: just append output suffix
        output_folder_name = folder_name + OUTPUT_SUFFIX

    output_folder = Path(input_folder).parent / output_folder_name

    print(f"\n--- Converting {folder_name} -> {output_folder_name} ---")
    process_folder(input_folder, str(output_folder))

def find_input_folders(base_directory, suffix):
    """
    Find all folders ending with specified suffix

    Args:
        base_directory: Directory to search in
        suffix: Folder suffix to look for

    Returns:
        List of folder paths
    """
    base_path = Path(base_directory)

    if not base_path.exists():
        print(f"Error: Base directory not found: {base_directory}")
        return []

    folders = [d for d in base_path.iterdir()
              if d.is_dir() and d.name.endswith(suffix)]

    # Filter out any unwanted folders (like backup folders)
    exclude_keywords = ['backup', 'temp', 'proper']  # Add more if needed
    folders = [f for f in folders
              if not any(keyword in f.name.lower() for keyword in exclude_keywords)]

    return folders

def main():
    """
    Main function - processes all input folders to create alpha masks
    """
    print("BiRefNet RGBA to Alpha Mask Converter")
    print("Converts RGBA/RGB images to pure black/white alpha masks")
    print("Black = Background, White = Person/Foreground")
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

    print(f"Configuration:")
    print(f"  Base Directory: {BASE_DIR}")
    print(f"  Input Suffix: '{INPUT_SUFFIX}' (looking for folders like 'Cam0{INPUT_SUFFIX}')")
    print(f"  Output Suffix: '{OUTPUT_SUFFIX}' (will create folders like 'Cam0{OUTPUT_SUFFIX}')")
    print(f"  Alpha Threshold: {ALPHA_THRESHOLD} (lower=more inclusive, higher=stricter)")
    print(f"  Supported Extensions: {SUPPORTED_EXTENSIONS}")
    print("=" * 70)

    # Find all input folders
    input_folders = find_input_folders(BASE_DIR, INPUT_SUFFIX)

    if not input_folders:
        print(f"No folders ending with '{INPUT_SUFFIX}' found in {BASE_DIR}")
        print("\nTo use this script:")
        print(f"1. Create folders ending with '{INPUT_SUFFIX}' (e.g., 'Images{INPUT_SUFFIX}')")
        print("2. Put your RGBA/RGB images in those folders")
        print("3. Run this script again")
        print("\nExample folder structure:")
        print(f"  {BASE_DIR}/")
        print(f"  ├── Camera1{INPUT_SUFFIX}/")
        print(f"  │   ├── person001.png  (RGBA image)")
        print(f"  │   └── person002.png")
        print(f"  └── Camera2{INPUT_SUFFIX}/")
        print(f"      └── person003.png")
        return

    print(f"Found {len(input_folders)} input folders:")
    for folder in sorted(input_folders):
        print(f"  - {folder.name}")

    # Confirm processing
    print(f"\nThis will create {len(input_folders)} new folders with '{OUTPUT_SUFFIX}' suffix")

    # Process each input folder
    for input_folder in sorted(input_folders):
        process_single_folder(str(input_folder))

    print(f"\n{'='*60}")
    print("✓ All alpha masks created successfully!")
    print("\nOutput folders created:")
    for folder in sorted(input_folders):
        output_name = folder.name.replace(INPUT_SUFFIX, OUTPUT_SUFFIX)
        print(f"  - {output_name}")

    print(f"\nAlpha masks are pure black/white PNG files:")
    print(f"  - Black (0) = Background")
    print(f"  - White (255) = Person/Foreground")

if __name__ == "__main__":
    main()
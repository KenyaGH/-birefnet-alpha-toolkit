#!/usr/bin/env python3
"""
Combined pipeline to convert .8ij files directly to PNG format.
Properly handles the .8ij format with JPEG-compressed frames.
"""

import os
import sys
import struct
import argparse
from pathlib import Path
import numpy as np
from PIL import Image

try:
    import imagecodecs
    HAVE_IMAGECODECS = True
except ImportError:
    HAVE_IMAGECODECS = False
    print("Warning: imagecodecs not available, some 12-bit JPEGs may not decode properly")

def decode_12bit_jpeg(jpeg_data):
    """Decode a 12-bit JPEG using imagecodecs."""
    if not HAVE_IMAGECODECS:
        raise ImportError("imagecodecs is required for 12-bit JPEG support")

    try:
        # Decode 12-bit JPEG
        img_array = imagecodecs.jpeg_decode(jpeg_data)
        return img_array
    except Exception as e:
        print(f"    Warning: Failed to decode JPEG: {e}")
        return None

def convert_12bit_to_8bit(img_array, method='linear'):
    """
    Convert 12-bit image data to 8-bit for PNG output.

    Methods:
    - 'linear': Simple linear scaling (keeps original brightness as-is)
    - 'auto': Auto-scale based on actual min/max
    - 'percentile': Scale based on 2-98 percentile range
    """
    if method == 'linear':
        # Linear scaling from 12-bit range (0-4095) to 8-bit (0-255)
        # This preserves original brightness levels as-is
        img_8bit = (img_array.astype(np.float32) * (255.0 / 4095.0)).astype(np.uint8)

    elif method == 'auto':
        # Auto-scale based on actual min/max values
        min_val = np.min(img_array)
        max_val = np.max(img_array)
        if max_val > min_val:
            img_8bit = ((img_array - min_val) * (255.0 / (max_val - min_val))).astype(np.uint8)
        else:
            img_8bit = np.zeros_like(img_array, dtype=np.uint8)

    elif method == 'percentile':
        # Scale based on percentile range (robust to outliers)
        p2 = np.percentile(img_array, 2)
        p98 = np.percentile(img_array, 98)
        if p98 > p2:
            img_8bit = np.clip((img_array - p2) * (255.0 / (p98 - p2)), 0, 255).astype(np.uint8)
        else:
            img_8bit = np.zeros_like(img_array, dtype=np.uint8)

    else:
        raise ValueError(f"Unknown conversion method: {method}")

    return img_8bit

def process_8ij_file(input_path, output_dir, scaling_method='linear', verbose=False):
    """
    Process a single .8ij file and extract all frames as PNG.

    Frame structure in .8ij:
    - 4 bytes: Frame ID "8IJ1"
    - 4 bytes: Frame size (uint32, little-endian)
    - 4 bytes: Frame index (uint32, little-endian)
    - N bytes: Raw JPEG data (12-bit JPEG)
    """
    FRAME_ID = b'8IJ1'
    FRAME_HEADER_SIZE = 12  # 4 + 4 + 4 bytes

    input_path = Path(input_path)
    output_dir = Path(output_dir)

    if not input_path.exists():
        print(f"Error: {input_path} does not exist")
        return False

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Processing: {input_path}")

    try:
        with open(input_path, 'rb') as f:
            file_size = input_path.stat().st_size
            bytes_read = 0
            frames_extracted = 0

            while bytes_read < file_size:
                # Read frame header
                header = f.read(FRAME_HEADER_SIZE)
                if len(header) < FRAME_HEADER_SIZE:
                    break

                bytes_read += FRAME_HEADER_SIZE

                # Parse header
                frame_id = header[0:4]
                if frame_id != FRAME_ID:
                    if verbose:
                        print(f"  Warning: Invalid frame ID at offset {bytes_read - FRAME_HEADER_SIZE}")
                    break

                frame_size = struct.unpack('<I', header[4:8])[0]
                frame_index = struct.unpack('<I', header[8:12])[0]

                if verbose and frames_extracted % 10 == 0:
                    print(f"  Processing frame {frame_index}: {frame_size} bytes")

                # Read JPEG data
                jpeg_data = f.read(frame_size)
                if len(jpeg_data) < frame_size:
                    print(f"  Warning: Incomplete frame {frame_index}")
                    break

                bytes_read += frame_size

                # Decode 12-bit JPEG
                img_array = decode_12bit_jpeg(jpeg_data)
                if img_array is None:
                    continue

                # Convert 12-bit to 8-bit
                img_8bit = convert_12bit_to_8bit(img_array, method=scaling_method)

                # Handle color vs grayscale
                if len(img_8bit.shape) == 2:
                    # Grayscale
                    img = Image.fromarray(img_8bit, mode='L')
                elif len(img_8bit.shape) == 3:
                    # Color (RGB)
                    if img_8bit.shape[2] == 3:
                        img = Image.fromarray(img_8bit, mode='RGB')
                    else:
                        # Convert to RGB if needed
                        img = Image.fromarray(img_8bit)
                else:
                    print(f"  Warning: Unexpected image shape: {img_8bit.shape}")
                    continue

                # Save as PNG
                output_name = f"{input_path.stem}_frame_{frame_index:06d}.png"
                output_path = output_dir / output_name
                img.save(output_path, 'PNG')

                frames_extracted += 1

        print(f"  ✓ Extracted {frames_extracted} frames to {output_dir}")
        return True

    except Exception as e:
        print(f"  ✗ Error processing {input_path}: {e}")
        return False

def process_directory(input_dir, output_dir, scaling_method='linear', preserve_structure=True, verbose=False):
    """Process all .8ij files in a directory."""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    if not input_dir.exists():
        print(f"Error: {input_dir} does not exist")
        return

    # Find all .8ij files
    eij_files = list(input_dir.glob('**/*.8ij'))

    if not eij_files:
        print(f"No .8ij files found in {input_dir}")
        return

    print(f"Found {len(eij_files)} .8ij file(s)")
    print(f"Using {scaling_method} brightness scaling")
    print()

    total_frames = 0
    for eij_file in eij_files:
        # Determine output path
        if preserve_structure:
            # Maintain directory structure
            rel_path = eij_file.relative_to(input_dir)
            file_output_dir = output_dir / rel_path.parent
        else:
            # Flat output
            file_output_dir = output_dir

        # Process the file
        success = process_8ij_file(eij_file, file_output_dir, scaling_method, verbose)

        if success:
            # Count frames in output directory
            png_files = list(file_output_dir.glob(f"{eij_file.stem}_frame_*.png"))
            total_frames += len(png_files)

    print(f"\nTotal frames extracted: {total_frames}")
    print(f"Output saved to: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Convert .8ij files directly to PNG')
    parser.add_argument('input', help='Input .8ij file or directory')
    parser.add_argument('output', help='Output directory for PNG files')
    parser.add_argument('--scaling', choices=['linear', 'auto', 'percentile'],
                       default='linear',
                       help='Brightness scaling method (default: linear, keeps brightness as-is)')
    parser.add_argument('--preserve-structure', action='store_true',
                       help='Preserve directory structure in output')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        # Process single file
        process_8ij_file(input_path, args.output, args.scaling, args.verbose)
    elif input_path.is_dir():
        # Process directory
        process_directory(input_path, args.output, args.scaling,
                        args.preserve_structure, args.verbose)
    else:
        print(f"Error: {input_path} is not a valid file or directory")
        sys.exit(1)

if __name__ == '__main__':
    main()
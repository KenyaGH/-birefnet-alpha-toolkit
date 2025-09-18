#!/usr/bin/env python3
"""
Organize misplaced PNG files into correct directory structure
"""

import os
import shutil
from pathlib import Path
import re

def organize_png_files(base_dir):
    """Move PNG files to correct R*/Cam* directories based on filename"""

    base_path = Path(base_dir)
    moved = 0
    errors = 0

    # Pattern to extract R## and Cam# from filename
    pattern = r'seanalexv2_S01_T01_Cam(\d)_R(\d+)_cam_\d+_frame_\d+\.png'

    print(f"🔍 Scanning for misplaced PNG files in {base_dir}")

    # Find all PNG files in root directory (not in subdirectories)
    png_files = [f for f in base_path.iterdir() if f.is_file() and f.suffix == '.png']

    print(f"📁 Found {len(png_files)} misplaced PNG files")

    for png_file in png_files:
        try:
            # Extract R## and Cam# from filename
            match = re.search(pattern, png_file.name)
            if match:
                cam_num = match.group(1)
                r_num = match.group(2).zfill(2)  # Pad with zero if needed (R1 -> R01)

                # Create target directory path
                target_dir = base_path / f"R{r_num}" / f"Cam{cam_num}"
                target_dir.mkdir(parents=True, exist_ok=True)

                # Move file to correct location
                target_path = target_dir / png_file.name
                shutil.move(str(png_file), str(target_path))
                moved += 1

                if moved % 100 == 0:
                    print(f"  Moved {moved} files...")

            else:
                print(f"⚠️  Cannot parse filename: {png_file.name}")
                errors += 1

        except Exception as e:
            print(f"❌ Error moving {png_file.name}: {e}")
            errors += 1

    print(f"✅ Moved {moved} files to correct directories")
    print(f"❌ Errors: {errors}")
    return moved, errors

if __name__ == "__main__":
    organize_png_files("/home/kenya/alpha_masks/8ij_to_PNGS")
#!/usr/bin/env python3
"""
Docker Entrypoint for Alpha Mask Toolkit
Automatically configures paths for container environment
"""

import os
import sys
import subprocess
from pathlib import Path

def update_script_config(script_path, base_dir, model_path, birefnet_path):
    """Update a Python script's configuration variables"""
    if not os.path.exists(script_path):
        return False

    with open(script_path, 'r') as f:
        content = f.read()

    # Replace configuration variables
    replacements = {
        'BASE_DIR = "/path/to/your/project"': f'BASE_DIR = "{base_dir}"',
        'MODEL_PATH = "./BiRefNet/checkpoints/BiRefNet-general.pth"': f'MODEL_PATH = "{model_path}"',
        'BIREFNET_PATH = "./BiRefNet"': f'BIREFNET_PATH = "{birefnet_path}"'
    }

    for old, new in replacements.items():
        content = content.replace(old, new)

    with open(script_path, 'w') as f:
        f.write(content)

    return True

def main():
    """Main entrypoint function"""
    print("🐳 Alpha Mask Toolkit Docker Container")
    print("=" * 50)

    # Container configuration
    base_dir = os.getenv('BASE_DIR', '/app/input')
    model_path = os.getenv('MODEL_PATH', '/app/BiRefNet/checkpoints/BiRefNet-general.pth')
    birefnet_path = os.getenv('BIREFNET_PATH', '/app/BiRefNet')

    print(f"📁 Input directory: {base_dir}")
    print(f"🤖 Model path: {model_path}")
    print(f"📦 BiRefNet path: {birefnet_path}")

    # Verify model exists
    if not os.path.exists(model_path):
        print(f"❌ ERROR: Model not found at {model_path}")
        sys.exit(1)

    # Verify input directory exists and has content
    if not os.path.exists(base_dir):
        print(f"❌ ERROR: Input directory not found: {base_dir}")
        print("💡 Mount your input directory with: -v /your/images:/app/input")
        sys.exit(1)

    # Check for input folders
    input_folders = [d for d in Path(base_dir).iterdir()
                    if d.is_dir() and d.name.endswith('_converted')]

    if not input_folders:
        print(f"❌ No input folders found ending with '_converted' in {base_dir}")
        print("💡 Create folders like 'Camera1_converted' and put your images there")
        print("\nExample usage:")
        print("1. Create folder: /your/images/Photos_converted/")
        print("2. Add images: /your/images/Photos_converted/photo1.jpg")
        print("3. Run container: docker run -v /your/images:/app/input alpha-mask-toolkit")
        sys.exit(1)

    print(f"✅ Found {len(input_folders)} input folders")

    # Update script configurations
    scripts_to_update = ['birefnet_direct_alpha.py', 'create_alpha_masks.py']
    for script in scripts_to_update:
        if os.path.exists(script):
            update_script_config(script, base_dir, model_path, birefnet_path)
            print(f"✅ Updated configuration in {script}")

    # Determine which script to run based on command line args or environment
    script_to_run = os.getenv('SCRIPT', 'birefnet_direct_alpha.py')

    if len(sys.argv) > 1:
        script_to_run = sys.argv[1]

    if not os.path.exists(script_to_run):
        print(f"❌ ERROR: Script not found: {script_to_run}")
        sys.exit(1)

    print(f"🚀 Running {script_to_run}")
    print("=" * 50)

    # Run the selected script
    try:
        subprocess.run([sys.executable, script_to_run], check=True)
        print("✅ Processing completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Processing failed with exit code {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
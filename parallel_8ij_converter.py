#!/usr/bin/env python3
"""
Parallel .8ij to PNG converter - processes multiple files simultaneously
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse

def process_single_file(args):
    """Process a single .8ij file using the existing pipeline"""
    input_file, output_dir, scaling_method = args

    # Create command for single file processing
    cmd = [
        'python3',
        '/home/kenya/repos/8ij_to_png_pipeline.py',
        str(input_file),
        str(output_dir),
        '--scaling', scaling_method,
        '--preserve-structure'
    ]

    try:
        print(f"[{os.getpid()}] Starting: {Path(input_file).name}")

        # Run the conversion
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

        if result.returncode == 0:
            print(f"[{os.getpid()}] ✅ Completed: {Path(input_file).name}")
            return True, input_file, ""
        else:
            print(f"[{os.getpid()}] ❌ Failed: {Path(input_file).name}")
            return False, input_file, result.stderr

    except subprocess.TimeoutExpired:
        print(f"[{os.getpid()}] ⏰ Timeout: {Path(input_file).name}")
        return False, input_file, "Process timeout"
    except Exception as e:
        print(f"[{os.getpid()}] 💥 Error: {Path(input_file).name} - {e}")
        return False, input_file, str(e)

def find_8ij_files(input_dir):
    """Find all .8ij files in the input directory"""
    input_path = Path(input_dir)
    return list(input_path.glob('**/*.8ij'))

def parallel_convert(input_dir, output_dir, max_workers=6, scaling_method='linear'):
    """Convert all .8ij files using parallel processing"""

    print(f"🔍 Scanning for .8ij files in {input_dir}")
    eij_files = find_8ij_files(input_dir)

    if not eij_files:
        print("❌ No .8ij files found!")
        return

    print(f"📁 Found {len(eij_files)} .8ij files")
    print(f"🚀 Using {max_workers} parallel workers")
    print(f"📊 Scaling method: {scaling_method}")
    print()

    # Prepare arguments for each file
    file_args = []
    for eij_file in eij_files:
        file_args.append((eij_file, output_dir, scaling_method))

    # Track progress
    completed = 0
    failed = 0
    start_time = time.time()

    # Process files in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        future_to_file = {
            executor.submit(process_single_file, args): args[0]
            for args in file_args
        }

        # Process results as they complete
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                success, input_file, error_msg = future.result()
                if success:
                    completed += 1
                else:
                    failed += 1
                    if error_msg:
                        print(f"   Error details: {error_msg}")

                # Progress update
                total_processed = completed + failed
                elapsed = time.time() - start_time
                avg_time = elapsed / total_processed if total_processed > 0 else 0
                remaining = len(eij_files) - total_processed
                eta = remaining * avg_time / max_workers if avg_time > 0 else 0

                print(f"📊 Progress: {total_processed}/{len(eij_files)} ({completed} ✅, {failed} ❌) | "
                      f"ETA: {eta/60:.1f} min")

            except Exception as e:
                failed += 1
                print(f"💥 Exception processing {Path(file_path).name}: {e}")

    # Final summary
    total_time = time.time() - start_time
    print()
    print("=" * 50)
    print(f"🏁 Conversion Complete!")
    print(f"✅ Successful: {completed}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"📈 Average: {total_time/len(eij_files):.1f} seconds per file")
    print("=" * 50)

def main():
    parser = argparse.ArgumentParser(description='Parallel .8ij to PNG converter')
    parser.add_argument('input_dir', help='Input directory containing .8ij files')
    parser.add_argument('output_dir', help='Output directory for PNG files')
    parser.add_argument('--workers', type=int, default=6,
                       help='Number of parallel workers (default: 6)')
    parser.add_argument('--scaling', choices=['linear', 'auto', 'percentile'],
                       default='linear', help='Brightness scaling method')

    args = parser.parse_args()

    # Ensure output directory exists
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    parallel_convert(args.input_dir, args.output_dir, args.workers, args.scaling)

if __name__ == '__main__':
    main()
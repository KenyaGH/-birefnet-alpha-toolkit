#!/usr/bin/env python3
"""
Alpha Mask Toolkit - Automated Test Runner
Comprehensive testing framework for validating toolkit functionality.
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

class AlphaMaskTester:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.test_data_dir = self.base_dir / "test_data"
        self.results = []

    def setup_test_environment(self):
        """Prepare test environment and validate setup."""
        print("🔧 Setting up test environment...")

        # Check if test data exists
        if not self.test_data_dir.exists():
            print("❌ Test data directory not found. Run setup first.")
            return False

        # Check for required scripts
        required_scripts = [
            "birefnet_direct_alpha.py",
            "create_alpha_masks.py",
            "docker_entrypoint.py"
        ]

        for script in required_scripts:
            if not (self.base_dir / script).exists():
                print(f"❌ Required script missing: {script}")
                return False

        print("✅ Test environment ready")
        return True

    def test_docker_availability(self) -> bool:
        """Check if Docker is available and working."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ Docker available: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        print("⚠️  Docker not available - skipping Docker tests")
        return False

    def test_gpu_availability(self) -> bool:
        """Check if GPU/CUDA is available."""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                print(f"✅ GPU available: {gpu_name}")
                return True
            else:
                print("⚠️  GPU not available - using CPU mode")
                return False
        except ImportError:
            print("⚠️  PyTorch not available - cannot test GPU")
            return False

    def create_synthetic_test_images(self):
        """Create simple synthetic test images for validation."""
        print("🎨 Creating synthetic test images...")

        try:
            from PIL import Image, ImageDraw
            import numpy as np
        except ImportError:
            print("⚠️  PIL not available - cannot create synthetic images")
            return False

        # Test image configurations
        test_configs = [
            ("Camera1_converted", [
                ("person001.jpg", (800, 600), "person"),
                ("person002.png", (1024, 768), "person"),
                ("group001.jpg", (1200, 800), "group")
            ]),
            ("Camera2_converted", [
                ("portrait001.jpg", (600, 800), "portrait"),
                ("outdoor001.png", (1920, 1080), "outdoor")
            ]),
            ("EdgeCases_converted", [
                ("very_large.jpg", (3840, 2160), "large"),
                ("very_small.jpg", (320, 240), "small"),
                ("dark_image.jpg", (800, 600), "dark"),
                ("complex_background.jpg", (1024, 768), "complex")
            ])
        ]

        for folder_name, images in test_configs:
            folder_path = self.test_data_dir / "input" / folder_name
            folder_path.mkdir(parents=True, exist_ok=True)

            for img_name, size, img_type in images:
                img_path = folder_path / img_name

                # Create synthetic image based on type
                if img_type == "person":
                    img = self._create_person_image(size)
                elif img_type == "group":
                    img = self._create_group_image(size)
                elif img_type == "portrait":
                    img = self._create_portrait_image(size)
                elif img_type == "large":
                    img = self._create_large_image(size)
                elif img_type == "small":
                    img = self._create_small_image(size)
                elif img_type == "dark":
                    img = self._create_dark_image(size)
                elif img_type == "complex":
                    img = self._create_complex_image(size)
                else:
                    img = self._create_default_image(size)

                # Save with appropriate format
                if img_name.endswith('.png'):
                    img.save(img_path, 'PNG')
                else:
                    img.save(img_path, 'JPEG', quality=90)

                print(f"  ✅ Created {img_name} ({size[0]}x{size[1]})")

        print("🎨 Synthetic test images created successfully")
        return True

    def _create_person_image(self, size: Tuple[int, int]) -> Image.Image:
        """Create synthetic image with person-like shape."""
        img = Image.new('RGB', size, color=(100, 150, 200))  # Blue background
        draw = ImageDraw.Draw(img)

        # Draw person-like shape (head + body)
        center_x, center_y = size[0] // 2, size[1] // 2

        # Head (circle)
        head_radius = min(size) // 8
        draw.ellipse([
            center_x - head_radius, center_y - size[1]//3 - head_radius,
            center_x + head_radius, center_y - size[1]//3 + head_radius
        ], fill=(220, 180, 140))  # Skin color

        # Body (rectangle)
        body_width = min(size) // 4
        body_height = size[1] // 3
        draw.rectangle([
            center_x - body_width//2, center_y - body_height//2,
            center_x + body_width//2, center_y + body_height//2
        ], fill=(50, 50, 150))  # Clothing color

        return img

    def _create_group_image(self, size: Tuple[int, int]) -> Image.Image:
        """Create synthetic image with multiple people."""
        img = Image.new('RGB', size, color=(80, 120, 160))
        draw = ImageDraw.Draw(img)

        # Draw 3 people side by side
        for i in range(3):
            x_offset = (i - 1) * size[0] // 4 + size[0] // 2
            y_center = size[1] // 2

            # Head
            head_radius = min(size) // 12
            draw.ellipse([
                x_offset - head_radius, y_center - size[1]//4 - head_radius,
                x_offset + head_radius, y_center - size[1]//4 + head_radius
            ], fill=(220, 180, 140))

            # Body
            body_width = min(size) // 8
            body_height = size[1] // 5
            draw.rectangle([
                x_offset - body_width//2, y_center - body_height//2,
                x_offset + body_width//2, y_center + body_height//2
            ], fill=(100 + i*30, 50, 150))

        return img

    def _create_portrait_image(self, size: Tuple[int, int]) -> Image.Image:
        """Create portrait-style synthetic image."""
        return self._create_person_image(size)  # Similar to person for now

    def _create_large_image(self, size: Tuple[int, int]) -> Image.Image:
        """Create large resolution test image."""
        return self._create_person_image(size)

    def _create_small_image(self, size: Tuple[int, int]) -> Image.Image:
        """Create small resolution test image."""
        return self._create_person_image(size)

    def _create_dark_image(self, size: Tuple[int, int]) -> Image.Image:
        """Create dark/low contrast image."""
        img = Image.new('RGB', size, color=(20, 20, 30))  # Very dark background
        draw = ImageDraw.Draw(img)

        center_x, center_y = size[0] // 2, size[1] // 2

        # Barely visible person
        head_radius = min(size) // 8
        draw.ellipse([
            center_x - head_radius, center_y - size[1]//3 - head_radius,
            center_x + head_radius, center_y - size[1]//3 + head_radius
        ], fill=(60, 50, 40))  # Dark skin

        body_width = min(size) // 4
        body_height = size[1] // 3
        draw.rectangle([
            center_x - body_width//2, center_y - body_height//2,
            center_x + body_width//2, center_y + body_height//2
        ], fill=(40, 40, 50))  # Dark clothing

        return img

    def _create_complex_image(self, size: Tuple[int, int]) -> Image.Image:
        """Create image with complex background."""
        img = Image.new('RGB', size, color=(150, 200, 100))  # Green base
        draw = ImageDraw.Draw(img)

        # Add complex background elements
        import random
        for _ in range(20):
            x = random.randint(0, size[0])
            y = random.randint(0, size[1])
            w = random.randint(20, 100)
            h = random.randint(20, 100)
            color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            draw.rectangle([x, y, x+w, y+h], fill=color)

        # Add person on top
        center_x, center_y = size[0] // 2, size[1] // 2

        head_radius = min(size) // 8
        draw.ellipse([
            center_x - head_radius, center_y - size[1]//3 - head_radius,
            center_x + head_radius, center_y - size[1]//3 + head_radius
        ], fill=(220, 180, 140))

        body_width = min(size) // 4
        body_height = size[1] // 3
        draw.rectangle([
            center_x - body_width//2, center_y - body_height//2,
            center_x + body_width//2, center_y + body_height//2
        ], fill=(255, 255, 255))  # White clothing to stand out

        return img

    def _create_default_image(self, size: Tuple[int, int]) -> Image.Image:
        """Create default test image."""
        return self._create_person_image(size)

    def test_script_execution(self, script_name: str) -> bool:
        """Test direct script execution."""
        print(f"🐍 Testing script: {script_name}")

        try:
            # Test import first
            result = subprocess.run([
                sys.executable, "-c", f"import {script_name.replace('.py', '')}"
            ], capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                print(f"  ❌ Import failed: {result.stderr}")
                return False

            print(f"  ✅ {script_name} import successful")
            return True

        except subprocess.TimeoutExpired:
            print(f"  ❌ {script_name} test timed out")
            return False
        except Exception as e:
            print(f"  ❌ {script_name} test error: {e}")
            return False

    def test_docker_execution(self) -> bool:
        """Test Docker container execution."""
        print("🐳 Testing Docker container...")

        if not self.test_docker_availability():
            return False

        try:
            # Test basic container functionality
            result = subprocess.run([
                "docker", "run", "--rm",
                "kenyagh/alpha-mask-toolkit:latest",
                "python", "-c", "import torch; print('Container OK')"
            ], capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                print("  ✅ Docker container basic test passed")
                return True
            else:
                print(f"  ❌ Docker test failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("  ❌ Docker test timed out")
            return False
        except Exception as e:
            print(f"  ❌ Docker test error: {e}")
            return False

    def run_performance_tests(self):
        """Run performance benchmarking tests."""
        print("⚡ Running performance tests...")

        # This would measure processing times, memory usage, etc.
        # For now, just placeholder
        print("  📊 Performance testing not yet implemented")
        print("  📝 TODO: Add timing and memory measurements")

    def run_comprehensive_tests(self):
        """Run the full test suite."""
        print("🧪 Running comprehensive Alpha Mask Toolkit tests...\n")

        # Setup
        if not self.setup_test_environment():
            return False

        # Create test data if needed
        self.create_synthetic_test_images()

        # Test availability
        docker_available = self.test_docker_availability()
        gpu_available = self.test_gpu_availability()

        print("\n" + "="*60)
        print("TESTING RESULTS")
        print("="*60)

        # Test scripts
        scripts_to_test = [
            "birefnet_direct_alpha.py",
            "create_alpha_masks.py",
            "docker_entrypoint.py"
        ]

        script_results = []
        for script in scripts_to_test:
            result = self.test_script_execution(script)
            script_results.append(result)

        # Test Docker if available
        docker_result = None
        if docker_available:
            docker_result = self.test_docker_execution()

        # Summary
        print(f"\n📋 Test Summary:")
        print(f"  Scripts tested: {len(scripts_to_test)}")
        print(f"  Scripts passed: {sum(script_results)}")
        print(f"  Docker available: {'Yes' if docker_available else 'No'}")
        print(f"  Docker test passed: {'Yes' if docker_result else 'No' if docker_result is not None else 'Skipped'}")
        print(f"  GPU available: {'Yes' if gpu_available else 'No'}")

        overall_success = all(script_results) and (docker_result is not False)
        print(f"\n🎯 Overall Result: {'✅ PASS' if overall_success else '❌ FAIL'}")

        return overall_success

def main():
    parser = argparse.ArgumentParser(description="Alpha Mask Toolkit Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--edge-cases", action="store_true", help="Run edge case tests")
    parser.add_argument("--setup", action="store_true", help="Setup test environment only")

    args = parser.parse_args()

    tester = AlphaMaskTester()

    if args.setup:
        tester.setup_test_environment()
        tester.create_synthetic_test_images()
    elif args.performance:
        tester.run_performance_tests()
    elif args.all or len(sys.argv) == 1:
        tester.run_comprehensive_tests()
    else:
        print("Use --all, --performance, --edge-cases, or --setup")

if __name__ == "__main__":
    main()
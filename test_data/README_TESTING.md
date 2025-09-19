# Alpha Mask Toolkit - Test Datasets

This directory contains test datasets for validating the Alpha Mask Toolkit functionality.

## Directory Structure

```
test_data/
├── input/                          # Test input images
│   ├── Camera1_converted/          # Sample input folder 1
│   │   ├── person001.jpg
│   │   ├── person002.png
│   │   └── group001.jpg
│   ├── Camera2_converted/          # Sample input folder 2
│   │   ├── portrait001.jpg
│   │   └── outdoor001.png
│   └── EdgeCases_converted/        # Edge case testing
│       ├── very_large.jpg          # High resolution test
│       ├── very_small.jpg          # Low resolution test
│       ├── dark_image.jpg          # Low light conditions
│       └── complex_background.jpg  # Complex background test
├── expected_output/                # Expected alpha mask outputs
│   ├── Camera1_alpha_mask/
│   ├── Camera2_alpha_mask/
│   └── EdgeCases_alpha_mask/
└── temp/                          # Temporary testing files

## Test Cases

### 1. Basic Functionality Tests
- **Standard portraits**: Clear subjects with simple backgrounds
- **Group photos**: Multiple people in frame
- **Different formats**: JPG, PNG support
- **Various resolutions**: 480p to 4K images

### 2. Edge Case Tests
- **High resolution**: 4K+ images (memory/performance test)
- **Low resolution**: <500px images (minimum viable test)
- **Dark images**: Low light/contrast scenarios
- **Complex backgrounds**: Busy/cluttered scenes
- **Partial subjects**: People partially out of frame

### 3. Performance Tests
- **Batch processing**: 50+ images in single folder
- **Large files**: 10MB+ image files
- **Memory stress**: Processing while system memory is limited

### 4. Docker-specific Tests
- **Model download**: First run model acquisition
- **Volume mounting**: Input/output directory mapping
- **GPU acceleration**: CUDA utilization validation
- **Container persistence**: Multiple runs with cached model

## Running Tests

### Local Script Testing
```bash
# Configure script paths
cd /path/to/alpha_masks
cp test_data/input/* ./
python birefnet_direct_alpha.py
```

### Docker Testing
```bash
# Test with Docker
docker run --gpus all \
  -v $(pwd)/test_data/input:/app/input \
  -v $(pwd)/test_data/output:/app/output \
  kenyagh/alpha-mask-toolkit:latest
```

### Automated Testing Script
```bash
# Run comprehensive test suite
python test_runner.py --all
python test_runner.py --performance
python test_runner.py --edge-cases
```

## Expected Results

### Success Criteria
- ✅ All input images processed without errors
- ✅ Alpha masks generated in correct output folders
- ✅ Output images are pure black/white (no gray pixels)
- ✅ Subject boundaries properly detected
- ✅ Processing completes within reasonable time limits

### Quality Metrics
- **Accuracy**: Subject properly separated from background
- **Completeness**: No missing parts of subjects
- **Cleanliness**: Clean edges without artifacts
- **Consistency**: Similar quality across different input types

## Test Image Sources

### Recommended Test Images
1. **Portrait photos**: Clear headshots with simple backgrounds
2. **Full body**: Standing people with visible outlines
3. **Group photos**: 2-5 people in frame
4. **Action shots**: People in motion
5. **Outdoor scenes**: Natural lighting conditions

### Image Requirements
- **Format**: JPG, PNG
- **Size**: 500px - 4000px (width/height)
- **Content**: Contains clearly visible people
- **Quality**: Good lighting, not overly blurred

## Performance Benchmarks

### Expected Processing Times (with GPU)
- **Small images** (500px): 1-2 seconds
- **Medium images** (1080p): 2-5 seconds
- **Large images** (4K): 5-10 seconds
- **Batch processing**: 2-3 seconds per image average

### Memory Usage
- **Base container**: ~2GB RAM
- **Model loading**: +1.5GB RAM
- **Image processing**: +0.5-2GB RAM (depends on image size)
- **Total expected**: 4-6GB RAM for optimal performance

## Troubleshooting Common Issues

### Model Download Failures
- Check internet connectivity
- Verify disk space (1GB+ free)
- Check firewall/proxy settings

### GPU Not Detected
- Verify `nvidia-docker` runtime installed
- Check `--gpus all` flag usage
- Validate CUDA drivers on host

### Out of Memory Errors
- Reduce image sizes or batch sizes
- Increase system RAM allocation
- Use CPU-only mode for testing

### Poor Quality Masks
- Check input image quality
- Verify proper lighting in source images
- Test with simpler backgrounds first
# Photo Post Processing

A Python application for intelligent photo processing that automatically adjusts lighting, orientation, and resizes images to 2K and 4K resolutions.

## Features

- **Automatic Orientation Correction**: Uses EXIF data to fix image rotation
- **Intelligent Lighting Adjustment**: Analyzes and corrects brightness, contrast, and gamma
- **Smart Resizing**: Maintains aspect ratio while targeting specific pixel counts
- **Batch Processing**: Processes multiple images and creates organized output folders
- **Compression**: Automatically creates ZIP files of processed images

## Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)

## Output Resolutions

- **2K**: 2560×1440 equivalent pixel count
- **4K**: 3840×2160 equivalent pixel count

## Requirements

- Python 3.7+
- PIL (Pillow)
- NumPy

## Usage

1. Update the folder path in `process_photos.py`
2. Run the script:
```bash
python src/process_photos.py
```

The script will create two folders and ZIP files:
- `processed_photos_2k/` and `processed_photos_2k.zip`
- `processed_photos_4k/` and `processed_photos_4k.zip`

## How it Works

1. **Orientation Fix**: Reads EXIF data to rotate images to correct orientation
2. **Lighting Analysis**: Analyzes brightness, contrast, and histogram data
3. **Intelligent Adjustments**: Applies brightness, contrast, and gamma corrections
4. **Aspect Ratio Preservation**: Calculates optimal dimensions for target resolutions
5. **Quality Optimization**: Saves with optimal JPEG quality and compression

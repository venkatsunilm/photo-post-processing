"""
📐 NEW RESIZE ONLY MODE ADDED

## WHAT'S NEW:
Added Option 12: "Resize Only" to the photo processing pipeline

## FEATURES:
✅ Resizes images to 4K resolution (3840x2160 pixels)
✅ Converts any format (NEF, PNG, TIFF, etc.) to high-quality JPEG
✅ Maintains original aspect ratio
✅ Uses high-quality Lanczos resampling
✅ Preserves EXIF orientation
❌ NO watermarks added
❌ NO color enhancements
❌ NO adjustments of any kind

## USE CASES:
🎯 Format conversion (NEF → JPEG, PNG → JPEG, etc.)
🎯 Resize large images for web/email
🎯 Batch processing for file size reduction
🎯 Clean conversion without any modifications
🎯 Preparing images for upload to services that don't accept RAW
🎯 Quick standardization of mixed format collections

## OUTPUT:
📁 Folder: processed_photos_4k_resize_only
📝 Filename: [original_name]_res.jpg
📦 ZIP: Created automatically for easy download

## HOW TO USE:
1. Run the main program: python src/process_photos.py
2. Select option 12: "Resize Only"
3. Your images will be processed without any enhancements or watermarks

## COMPARISON WITH OTHER MODES:
- Option 9 (Resize & Watermark): Resizes + adds watermark
- Option 10 (Watermark Only): Keeps original size + adds watermark  
- Option 12 (Resize Only): Resizes only, nothing else added

This mode is perfect when you just need clean, resized JPEGs without any modifications!
"""

print(__doc__)

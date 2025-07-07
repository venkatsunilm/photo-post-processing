"""
Quick test script for the enhanced RAW processing
"""

import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

try:
    from pro_photo_processor.raw.raw_processing_enhanced import (
        load_image_smart_enhanced,
    )

    print("✅ Enhanced RAW processing module loaded successfully")

    # Test with the problematic file
    test_file = r"C:\Users\harit\Documents\temp\Input Photos\VEN_3576.NEF"
    if os.path.exists(test_file):
        print(f"📸 Testing with: {os.path.basename(test_file)}")
        img = load_image_smart_enhanced(test_file)
        print("✅ SUCCESS! Enhanced RAW processing completed!")
        print(f"   Image size: {img.size}")
        print(f"   Mode: {img.mode}")
    else:
        print(f"❌ Test file not found: {test_file}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()

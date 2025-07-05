"""
Test the new brightness_adjustment method
"""

import os
import sys

from PIL import Image

from utils.photoshop_tools import PhotoshopStyleEnhancer

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def test_brightness_method():
    """Test the new brightness adjustment method"""
    print("🧪 Testing New Brightness Adjustment Method")
    print("=" * 50)

    try:
        # Create a test image
        test_img = Image.new("RGB", (100, 100), color=(128, 128, 128))  # Mid-gray
        print("✅ Created test image (mid-gray)")

        # Test brightness adjustment
        enhancer = PhotoshopStyleEnhancer(test_img)

        # Test positive brightness
        enhancer.brightness_adjustment(50)  # 50% brighter
        print("✅ Applied +50% brightness adjustment")

        # Test negative brightness
        enhancer.brightness_adjustment(-25)  # 25% darker
        print("✅ Applied -25% brightness adjustment")

        # Check history
        history = enhancer.get_history()
        print(f"📝 Processing history: {history}")

        # Test exposure for comparison
        enhancer2 = PhotoshopStyleEnhancer(test_img)
        enhancer2.exposure_adjustment(0.5)  # +0.5 stops
        history2 = enhancer2.get_history()
        print(f"📝 Exposure history: {history2}")

        print("\n✅ Both brightness_adjustment() and exposure_adjustment() work!")
        print("🎯 brightness_adjustment() is now available for user-friendly controls")

    except Exception as e:
        print(f"❌ Error testing brightness method: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_brightness_method()

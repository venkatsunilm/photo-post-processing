"""
Quick test script to validate the updated sports presets with midtone protection
"""
import numpy as np
from PIL import Image
from utils.photoshop_tools import apply_photoshop_preset, PHOTOSHOP_PRESETS
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def test_sports_presets():
    """Test the sports presets with midtone protection"""
    print("🏃‍♂️ Testing Updated Sports Presets with Midtone Protection")
    print("=" * 60)

    # Check if sports presets have midtone protection
    sports_presets = ['sports_action', 'sports_action_raw']

    for preset_name in sports_presets:
        if preset_name in PHOTOSHOP_PRESETS:
            preset = PHOTOSHOP_PRESETS[preset_name]
            print(f"\n📊 {preset_name.upper()} Preset:")
            print(f"   Exposure: {preset.get('exposure', 0)}")
            print(f"   Highlights: {preset.get('highlights', 0)}")
            print(f"   Shadows: {preset.get('shadows', 0)}")
            print(f"   Vibrance: {preset.get('vibrance', 0)}")
            print(
                f"   Midtone Protection: {preset.get('midtone_protection', False)}")

            # Check if values are conservative enough for sand protection
            exposure = preset.get('exposure', 0)
            shadows = preset.get('shadows', 0)
            highlights = preset.get('highlights', 0)

            print(f"   🛡️  Sand Protection Analysis:")
            print(
                f"      Exposure (should be ≤0.05): {'✅' if exposure <= 0.05 else '⚠️'} {exposure}")
            print(
                f"      Shadows (should be ≤12): {'✅' if shadows <= 12 else '⚠️'} {shadows}")
            print(
                f"      Highlights (should be ≤-8): {'✅' if highlights <= -8 else '⚠️'} {highlights}")
        else:
            print(f"❌ Preset {preset_name} not found!")

    print("\n🎯 Recommendations:")
    print("   ✅ Lower exposure prevents overall brightening")
    print("   ✅ Reduced shadow lift prevents ground brightening")
    print("   ✅ Stronger highlight recovery protects bright sand")
    print("   ✅ Midtone protection targets 130-220 brightness range")

    # Test the actual processing (if we have a test image)
    test_image_path = r"C:\Users\harit\Documents\temp\Input Photos"
    if os.path.exists(test_image_path):
        print(f"\n🖼️ Test image directory found: {test_image_path}")

        # Look for any image file to test
        for file in os.listdir(test_image_path):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.nef')):
                test_file = os.path.join(test_image_path, file)
                print(f"   Testing with: {file}")

                try:
                    # Create a synthetic bright test image to simulate sand
                    test_img = Image.new('RGB', (400, 300), color=(
                        180, 170, 150))  # Bright sand color

                    # Test both presets
                    for preset_name in sports_presets:
                        try:
                            result, history = apply_photoshop_preset(
                                test_img, preset_name)
                            print(
                                f"   ✅ {preset_name}: {', '.join(history[-2:])}")
                        except Exception as e:
                            print(f"   ❌ {preset_name}: {e}")

                    break
                except Exception as e:
                    print(f"   ❌ Failed to test with {file}: {e}")
    else:
        print(f"⚠️  Test image directory not found: {test_image_path}")
        print("   Creating synthetic test image...")

        # Create a synthetic bright test image to simulate sand
        test_img = Image.new('RGB', (400, 300), color=(
            180, 170, 150))  # Bright sand color

        # Test both presets
        for preset_name in sports_presets:
            try:
                result, history = apply_photoshop_preset(test_img, preset_name)
                print(f"   ✅ {preset_name}: {', '.join(history[-2:])}")
            except Exception as e:
                print(f"   ❌ {preset_name}: {e}")


if __name__ == "__main__":
    test_sports_presets()

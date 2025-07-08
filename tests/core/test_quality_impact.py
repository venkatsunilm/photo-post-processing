"""
Image processing quality and performance test suite.
Tests different enhancement presets and measures their impact.
"""

import os
import sys
import time

from PIL import ImageStat

from pro_photo_processor.config.config import DEFAULT_INPUT_PATH
from pro_photo_processor.presets.photoshop_tools import (
    PHOTOSHOP_PRESETS,
    apply_photoshop_preset,
)
from pro_photo_processor.raw.raw_processing import load_image_smart

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def analyze_image_properties(img, name="Image"):
    """Analyze basic image properties and quality metrics"""

    print(f"📊 {name} Analysis:")
    print(f"   📐 Dimensions: {img.size[0]} x {img.size[1]} pixels")

    # Calculate basic statistics
    stat = ImageStat.Stat(img)

    print(f"   🎨 Brightness (mean RGB): {sum(stat.mean) / 3:.1f}")
    print(f"   📈 Contrast (stddev): {sum(stat.stddev) / 3:.1f}")

    # Color distribution
    r_mean, g_mean, b_mean = stat.mean
    print(f"   🔴 Red channel: {r_mean:.1f} ± {stat.stddev[0]:.1f}")
    print(f"   🟢 Green channel: {g_mean:.1f} ± {stat.stddev[1]:.1f}")
    print(f"   🔵 Blue channel: {b_mean:.1f} ± {stat.stddev[2]:.1f}")

    return {
        "dimensions": img.size,
        "brightness": sum(stat.mean) / 3,
        "contrast": sum(stat.stddev) / 3,
        "color_balance": {"r": r_mean, "g": g_mean, "b": b_mean},
    }


def analyze_preset_impact(img, preset_name):
    """Test the impact of a specific preset on an image"""

    print(f"\n🎨 Testing {preset_name.replace('_', ' ').title()} Preset")
    print("-" * 50)

    # Get original image properties
    original_props = analyze_image_properties(img, "Original")

    # Apply preset
    start_time = time.time()
    try:
        enhanced_img = apply_photoshop_preset(img, preset_name)
        processing_time = time.time() - start_time

        print(f"⏱️ Processing time: {processing_time:.2f} seconds")

        # Get enhanced image properties
        enhanced_props = analyze_image_properties(enhanced_img, "Enhanced")

        # Calculate changes
        brightness_change = enhanced_props["brightness"] - original_props["brightness"]
        contrast_change = enhanced_props["contrast"] - original_props["contrast"]

        print("\n📈 Changes Applied:")
        print(
            f"   💡 Brightness: {brightness_change:+.1f} ({brightness_change / original_props['brightness'] * 100:+.1f}%)"
        )
        print(
            f"   🔄 Contrast: {contrast_change:+.1f} ({contrast_change / original_props['contrast'] * 100:+.1f}%)"
        )

        # Color channel changes
        r_change = (
            enhanced_props["color_balance"]["r"] - original_props["color_balance"]["r"]
        )
        g_change = (
            enhanced_props["color_balance"]["g"] - original_props["color_balance"]["g"]
        )
        b_change = (
            enhanced_props["color_balance"]["b"] - original_props["color_balance"]["b"]
        )

        print("   🎨 Color shifts:")
        print(f"      🔴 Red: {r_change:+.1f}")
        print(f"      🟢 Green: {g_change:+.1f}")
        print(f"      🔵 Blue: {b_change:+.1f}")

        return {
            "success": True,
            "processing_time": processing_time,
            "brightness_change": brightness_change,
            "contrast_change": contrast_change,
            "enhanced_image": enhanced_img,
        }

    except Exception as e:
        processing_time = time.time() - start_time
        print(f"❌ Preset failed after {processing_time:.2f} seconds: {e}")
        return {"success": False, "error": str(e)}


def compare_presets_on_image(image_path):
    """Compare all presets on a single image"""

    print("🔬 PRESET COMPARISON TEST")
    print(f"📷 Test image: {os.path.basename(image_path)}")
    print("=" * 60)

    # Load test image
    try:
        test_img = load_image_smart(image_path)
        print("✅ Test image loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load test image: {e}")
        return

    results = {}

    # Test each preset
    for preset_name in PHOTOSHOP_PRESETS.keys():
        result = analyze_preset_impact(test_img, preset_name)
        results[preset_name] = result

    # Summary comparison
    print("\n📋 PRESET COMPARISON SUMMARY")
    print("=" * 60)

    successful_presets = {k: v for k, v in results.items() if v.get("success", False)}

    if successful_presets:
        # Find extremes
        fastest = min(successful_presets.items(), key=lambda x: x[1]["processing_time"])
        slowest = max(successful_presets.items(), key=lambda x: x[1]["processing_time"])

        brightest = max(
            successful_presets.items(), key=lambda x: x[1]["brightness_change"]
        )
        most_contrast = max(
            successful_presets.items(), key=lambda x: x[1]["contrast_change"]
        )

        print(
            f"⚡ Fastest processing: {fastest[0]} ({fastest[1]['processing_time']:.2f}s)"
        )
        print(
            f"🐌 Slowest processing: {slowest[0]} ({slowest[1]['processing_time']:.2f}s)"
        )
        print(
            f"💡 Most brightening: {brightest[0]} ({brightest[1]['brightness_change']:+.1f})"
        )
        print(
            f"🔄 Most contrast: {most_contrast[0]} ({most_contrast[1]['contrast_change']:+.1f})"
        )

    # Failed presets
    failed_presets = [k for k, v in results.items() if not v.get("success", False)]
    if failed_presets:
        print(f"\n❌ Failed presets: {', '.join(failed_presets)}")


def performance_benchmark():
    """Run performance benchmark on available images"""

    print("🏃‍♂️ PERFORMANCE BENCHMARK")
    print("=" * 40)

    # Find test images
    test_files = []
    if os.path.exists(DEFAULT_INPUT_PATH):
        for file in os.listdir(DEFAULT_INPUT_PATH):
            file_path = os.path.join(DEFAULT_INPUT_PATH, file)
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".nef")):
                test_files.append(file_path)

    if not test_files:
        print("❌ No test images found")
        return

    # Test loading performance
    print(f"📂 Testing {len(test_files)} images")

    total_load_time = 0
    successful_loads = 0

    for file_path in test_files[:5]:  # Test first 5 files
        print(f"\n📷 Testing: {os.path.basename(file_path)}")

        start_time = time.time()
        try:
            img = load_image_smart(file_path)
            load_time = time.time() - start_time
            total_load_time += load_time
            successful_loads += 1

            print(f"   ✅ Loaded in {load_time:.2f}s ({img.size[0]}x{img.size[1]})")

            # Test one preset for processing speed
            preset_start = time.time()
            apply_photoshop_preset(img, "sports_action")  # Test processing speed
            preset_time = time.time() - preset_start

            print(f"   🎨 Sports Action preset: {preset_time:.2f}s")

        except Exception as e:
            load_time = time.time() - start_time
            print(f"   ❌ Failed in {load_time:.2f}s: {e}")

    if successful_loads > 0:
        avg_load_time = total_load_time / successful_loads
        print("\n📊 BENCHMARK RESULTS:")
        print(f"   ✅ Success rate: {successful_loads}/{len(test_files[:5])} files")
        print(f"   ⏱️ Average load time: {avg_load_time:.2f} seconds")
        print(f"   📈 Throughput: {1 / avg_load_time:.1f} images per second")


def main():
    """Run image processing tests"""
    print("🧪 IMAGE PROCESSING QUALITY TEST SUITE")
    print("=" * 50)
    print("1. Test Single Preset on Image")
    print("2. Compare All Presets on Image")
    print("3. Performance Benchmark")
    print("4. Full Quality Analysis")
    print("=" * 50)

    choice = input("Choose test (1-4): ").strip()

    # Find test images
    test_files = []
    if os.path.exists(DEFAULT_INPUT_PATH):
        for file in os.listdir(DEFAULT_INPUT_PATH):
            file_path = os.path.join(DEFAULT_INPUT_PATH, file)
            if file.lower().endswith((".jpg", ".jpeg", ".png", ".nef")):
                test_files.append(file_path)

    if not test_files and choice in ["1", "2", "4"]:
        print("❌ No test images found")
        return

    if choice == "1":
        print("Available presets:", list(PHOTOSHOP_PRESETS.keys()))
        preset = input("Enter preset name: ").strip()
        if preset in PHOTOSHOP_PRESETS:
            img = load_image_smart(test_files[0])
            analyze_preset_impact(img, preset)
        else:
            print("❌ Invalid preset name")

    elif choice == "2":
        compare_presets_on_image(test_files[0])

    elif choice == "3":
        performance_benchmark()

    elif choice == "4":
        compare_presets_on_image(test_files[0])
        print("\n")
        performance_benchmark()

    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()

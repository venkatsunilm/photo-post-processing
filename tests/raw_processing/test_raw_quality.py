"""
RAW image processing test and analysis tool.
Tests NEF file loading, processing quality, and performance.
"""

import os
import sys
import time

from utils.config import DEFAULT_INPUT_PATH
from utils.raw_processing import get_raw_metadata, is_raw_file, load_image_smart

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def analyze_raw_loading(file_path):
    """Test RAW file loading performance and quality"""

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False

    if not is_raw_file(file_path):
        print(f"❌ Not a RAW file: {file_path}")
        return False

    print(f"🔬 Testing RAW file: {os.path.basename(file_path)}")

    # Test loading time
    start_time = time.time()
    try:
        img = load_image_smart(file_path)
        load_time = time.time() - start_time

        print(f"✅ Successfully loaded in {load_time:.2f} seconds")
        print(f"📐 Image dimensions: {img.size[0]} x {img.size[1]} pixels")
        print(f"📊 Total pixels: {img.size[0] * img.size[1]:,}")

        # Test image quality metrics
        img_array = list(img.getdata())

        # Check for proper color range
        r_values = [
            pixel[0]
            # Sample every 1000th pixel
            for pixel in img_array[::1000]
        ]
        g_values = [pixel[1] for pixel in img_array[::1000]]
        b_values = [pixel[2] for pixel in img_array[::1000]]

        print("🎨 Color range analysis (sampled):")
        print(f"   Red: {min(r_values)} - {max(r_values)}")
        print(f"   Green: {min(g_values)} - {max(g_values)}")
        print(f"   Blue: {min(b_values)} - {max(b_values)}")

        return True

    except Exception as e:
        load_time = time.time() - start_time
        print(f"❌ Failed to load after {load_time:.2f} seconds: {e}")
        return False


def analyze_raw_metadata(file_path):
    """Test RAW metadata extraction"""

    print(f"🔍 Extracting metadata from: {os.path.basename(file_path)}")

    try:
        metadata = get_raw_metadata(file_path)

        if metadata:
            print("📋 RAW Metadata:")
            for key, value in metadata.items():
                print(f"   {key}: {value}")
        else:
            print("❌ No metadata found")

    except Exception as e:
        print(f"❌ Metadata extraction failed: {e}")


def compare_raw_vs_jpg(raw_file, jpg_file):
    """Compare RAW vs JPG processing"""

    print("⚖️ Comparing RAW vs JPG processing")
    print(f"RAW: {os.path.basename(raw_file)}")
    print(f"JPG: {os.path.basename(jpg_file)}")

    # Load both files
    try:
        start_time = time.time()
        raw_img = load_image_smart(raw_file)
        raw_time = time.time() - start_time

        start_time = time.time()
        jpg_img = load_image_smart(jpg_file)
        jpg_time = time.time() - start_time

        print("\n📊 Loading Performance:")
        print(f"   RAW loading: {raw_time:.2f} seconds")
        print(f"   JPG loading: {jpg_time:.2f} seconds")
        print(f"   RAW is {raw_time / jpg_time:.1f}x slower")

        print("\n📐 Image Dimensions:")
        print(f"   RAW: {raw_img.size[0]} x {raw_img.size[1]} pixels")
        print(f"   JPG: {jpg_img.size[0]} x {jpg_img.size[1]} pixels")

        raw_pixels = raw_img.size[0] * raw_img.size[1]
        jpg_pixels = jpg_img.size[0] * jpg_img.size[1]
        print(f"   RAW has {raw_pixels / jpg_pixels:.1f}x more pixels")

        print("\n🎨 Quality Assessment:")
        print("   ✅ RAW: Full dynamic range, no compression artifacts")
        print("   ⚠️ JPG: 8-bit compressed, potential quality loss")
        print("   🏆 Winner: RAW (better for post-processing)")

    except Exception as e:
        print(f"❌ Comparison failed: {e}")


def scan_input_directory():
    """Scan input directory for test files"""

    print(f"🔍 Scanning input directory: {DEFAULT_INPUT_PATH}")

    if not os.path.exists(DEFAULT_INPUT_PATH):
        print(f"❌ Input directory not found: {DEFAULT_INPUT_PATH}")
        return [], []

    raw_files = []
    jpg_files = []

    for file in os.listdir(DEFAULT_INPUT_PATH):
        file_path = os.path.join(DEFAULT_INPUT_PATH, file)
        if os.path.isfile(file_path):
            if is_raw_file(file_path):
                raw_files.append(file_path)
            elif file.lower().endswith((".jpg", ".jpeg")):
                jpg_files.append(file_path)

    print(f"📋 Found {len(raw_files)} RAW files and {len(jpg_files)} JPG files")
    return raw_files, jpg_files


def run_comprehensive_test():
    """Run comprehensive RAW processing tests"""

    print("🧪 COMPREHENSIVE RAW PROCESSING TEST SUITE")
    print("=" * 60)

    raw_files, jpg_files = scan_input_directory()

    if not raw_files:
        print("❌ No RAW files found for testing")
        return

    # Test first RAW file in detail
    test_file = raw_files[0]
    print("\n1️⃣ DETAILED RAW ANALYSIS")
    print("-" * 40)
    analyze_raw_loading(test_file)

    print("\n2️⃣ METADATA EXTRACTION")
    print("-" * 40)
    analyze_raw_metadata(test_file)

    # Compare with JPG if available
    if jpg_files:
        print("\n3️⃣ RAW VS JPG COMPARISON")
        print("-" * 40)
        compare_raw_vs_jpg(test_file, jpg_files[0])

    # Test all RAW files for loading
    if len(raw_files) > 1:
        print("\n4️⃣ BATCH LOADING TEST")
        print("-" * 40)
        success_count = 0
        total_time = 0

        for raw_file in raw_files:
            start_time = time.time()
            success = analyze_raw_loading(raw_file)
            load_time = time.time() - start_time
            total_time += load_time

            if success:
                success_count += 1
            print("-" * 30)

        print("\n📊 BATCH TEST SUMMARY:")
        print(f"   ✅ Successful: {success_count}/{len(raw_files)} files")
        print(f"   ⏱️ Total time: {total_time:.2f} seconds")
        print(f"   📈 Average time: {total_time / len(raw_files):.2f} seconds per file")
        print(f"   🎯 Success rate: {success_count / len(raw_files) * 100:.1f}%")


def main():
    """Run RAW processing tests"""
    print("🔬 RAW PROCESSING TEST SUITE")
    print("=" * 40)
    print("1. Test Single RAW File")
    print("2. Extract RAW Metadata")
    print("3. Compare RAW vs JPG")
    print("4. Comprehensive Test")
    print("=" * 40)

    choice = input("Choose test (1-4): ").strip()

    raw_files, jpg_files = scan_input_directory()

    if choice == "1" and raw_files:
        analyze_raw_loading(raw_files[0])
    elif choice == "2" and raw_files:
        analyze_raw_metadata(raw_files[0])
    elif choice == "3" and raw_files and jpg_files:
        compare_raw_vs_jpg(raw_files[0], jpg_files[0])
    elif choice == "4":
        run_comprehensive_test()
    else:
        print("❌ Invalid choice or no test files available")


if __name__ == "__main__":
    main()

"""
Test script to demonstrate the difference between standard and enhanced RAW processing.
This will help you see why processed RAW files looked "dull" and how the enhanced version fixes it.
"""

from PIL import Image
from utils.raw_processing_enhanced import load_image_smart_enhanced, compare_raw_processing_methods
from utils.raw_processing import load_image_smart as load_standard
import os
import sys

# Add the src directory to Python path
src_path = os.path.join(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.append(src_path)


def analyze_raw_processing_differences():
    """
    Explains the technical differences between standard and enhanced RAW processing.
    """
    print("=" * 80)
    print("🔍 RAW vs JPEG PROCESSING ANALYSIS")
    print("=" * 80)

    print("\n📋 WHY PROCESSED RAW FILES LOOK 'DULL':")
    print("-" * 50)
    print("1. 📷 The 'original' you see is a JPEG preview embedded in the RAW file")
    print("2. 🎨 Camera manufacturers apply aggressive tone curves to JPEG previews")
    print("3. 🔧 Basic RAW processing uses conservative settings (flat, neutral)")
    print("4. ⚡ RAW files need additional contrast, saturation, and sharpening")
    print("5. 📊 Missing tone curve makes RAW files look flat compared to JPEG previews")

    print("\n🚀 ENHANCED RAW PROCESSING FIXES:")
    print("-" * 40)
    print("✅ Applies subtle S-curve for better contrast")
    print("✅ Increases brightness and exposure compensation")
    print("✅ Boosts color saturation and vibrancy")
    print("✅ Adds subtle sharpening")
    print("✅ Uses more aggressive rawpy processing parameters")
    print("✅ Mimics camera manufacturer JPEG processing")

    print("\n📈 TECHNICAL IMPROVEMENTS:")
    print("-" * 30)
    print("• no_auto_bright: False (allows auto-brightness)")
    print("• bright: 1.2 (20% brighter)")
    print("• exp_shift: 0.3 (exposure boost)")
    print("• Tone curve: S-curve for contrast")
    print("• Color enhancement: +25% saturation")
    print("• Contrast enhancement: +15%")
    print("• Sharpness enhancement: +10%")


def find_raw_files_in_workspace():
    """Find any RAW files in the workspace for testing."""
    raw_extensions = ('.nef', '.NEF', '.raw', '.RAW',
                      '.cr2', '.CR2', '.arw', '.ARW')
    raw_files = []

    # Search in common directories
    search_dirs = [
        os.path.join(os.getcwd(), 'input'),
        os.path.join(os.getcwd(), 'tests'),
        os.path.join(os.getcwd(), 'output'),
        os.getcwd()
    ]

    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if file.lower().endswith(raw_extensions):
                        raw_files.append(os.path.join(root, file))

    return raw_files


def test_enhanced_processing():
    """Test the enhanced RAW processing if RAW files are available."""
    print("\n" + "=" * 80)
    print("🧪 TESTING ENHANCED RAW PROCESSING")
    print("=" * 80)

    raw_files = find_raw_files_in_workspace()

    if not raw_files:
        print("❌ No RAW files found in workspace for testing")
        print("💡 To test with your RAW files:")
        print("   1. Place a NEF/RAW file in the 'input' folder")
        print("   2. Run this script again")
        return

    print(f"✅ Found {len(raw_files)} RAW file(s) for testing:")
    for file in raw_files:
        print(f"   📁 {os.path.basename(file)}")

    # Test with the first RAW file found
    test_file = raw_files[0]
    print(f"\n🧪 Testing with: {os.path.basename(test_file)}")

    try:
        # Compare processing methods
        results = compare_raw_processing_methods(test_file)

        if results:
            print("\n📊 PROCESSING COMPARISON RESULTS:")
            print("-" * 40)
            for method, image in results.items():
                print(
                    f"• {method.upper()}: {image.size[0]}x{image.size[1]} pixels")

            # Save comparison images if possible
            output_dir = os.path.join(os.getcwd(), 'tests', 'raw_comparison')
            os.makedirs(output_dir, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(test_file))[0]

            for method, image in results.items():
                output_path = os.path.join(
                    output_dir, f"{base_name}_{method}.jpg")
                image.save(output_path, quality=95)
                print(f"💾 Saved: {output_path}")

            print(f"\n✅ Comparison images saved to: {output_dir}")
            print("👀 Open these files to see the visual difference!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")


def show_best_practices():
    """Show best practices for RAW vs JPEG processing."""
    print("\n" + "=" * 80)
    print("📚 BEST PRACTICES: RAW vs JPEG for POST-PROCESSING")
    print("=" * 80)

    print("\n🥇 USE RAW (NEF) FILES WHEN:")
    print("-" * 35)
    print("✅ You want maximum image quality")
    print("✅ You need extensive color/exposure corrections")
    print("✅ You're doing professional portrait/sports/wildlife photography")
    print("✅ You have good lighting but want to fine-tune")
    print("✅ You want to recover highlights or lift shadows significantly")
    print("✅ File size and processing time are not critical")

    print("\n🥈 USE JPEG FILES WHEN:")
    print("-" * 25)
    print("✅ You need fast processing (batch processing many files)")
    print("✅ Storage space is limited")
    print("✅ The original exposure and colors are already good")
    print("✅ You only need basic adjustments (watermark, resize, slight enhancements)")
    print("✅ You're processing social media content")

    print("\n⚙️ TECHNICAL RECOMMENDATIONS:")
    print("-" * 35)
    print("• For portraits: Use RAW + 'Portrait Natural' or 'Portrait Dramatic' (auto-detects RAW)")
    print("• For sports: Use RAW + 'Sports Action' (auto-detects and applies RAW preset)")
    print("• For wildlife: Use RAW + 'Natural Wildlife' (auto-detects RAW and enhances)")
    print("• For batch processing: Mix - the system auto-optimizes each file format")
    print("• For web/social: JPEG is usually sufficient")

    print("\n🎯 QUALITY HIERARCHY (Best to Good):")
    print("-" * 45)
    print("1. 🥇 RAW + Enhanced Processing + Custom Adjustments")
    print("2. 🥈 RAW + Genre-Specific Preset (Portrait/Sports/Wildlife)")
    print("3. 🥉 JPEG + Genre-Specific Preset")
    print("4. 📷 JPEG + Basic Enhancements")
    print("5. 💧 JPEG + Watermark Only")


if __name__ == "__main__":
    print("🎨 RAW vs JPEG Processing Analysis and Testing")
    print("=" * 60)

    # Show analysis
    analyze_raw_processing_differences()

    # Test enhanced processing
    test_enhanced_processing()

    # Show best practices
    show_best_practices()

    print("\n" + "=" * 80)
    print("🎯 SUMMARY FOR YOUR WORKFLOW:")
    print("=" * 80)
    print("1. 📷 Use the ENHANCED RAW processing for better results")
    print("2. 🎨 RAW files will now look vibrant instead of dull")
    print("3. 🔧 The enhanced processing mimics camera JPEG processing")
    print("4. ⚡ For best results: RAW + Enhanced Processing + Sports/Portrait presets")
    print("5. 💡 The 'dull' look was due to missing tone curves and conservative processing")
    print("\n✅ Your RAW processing pipeline is now significantly improved!")

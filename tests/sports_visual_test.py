"""
Visual comparison tool for sports presets - before and after midtone protection
This helps demonstrate the sand/ground brightness improvements
"""

import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from utils.photoshop_tools import apply_photoshop_preset
from utils.raw_processing_enhanced import load_image_smart_enhanced

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def create_comparison_for_sports_images():
    """Create before/after comparisons for sports images"""
    print("🏃‍♂️ Creating Sports Preset Comparison")
    print("=" * 50)

    # Look for test images
    test_dir = r"C:\Users\harit\Documents\temp\Input Photos"
    if not os.path.exists(test_dir):
        print(f"❌ Test directory not found: {test_dir}")
        return

    # Find images to test
    image_files = []
    for file in os.listdir(test_dir):
        if file.lower().endswith((".jpg", ".jpeg", ".png", ".nef")):
            image_files.append(os.path.join(test_dir, file))

    if not image_files:
        print("❌ No image files found for testing")
        return

    print(f"📁 Found {len(image_files)} test images")

    # Create output directory for comparisons
    output_dir = os.path.join(os.path.dirname(__file__), "sports_comparison_output")
    os.makedirs(output_dir, exist_ok=True)

    # Test with first image
    test_file = image_files[0]
    filename = os.path.splitext(os.path.basename(test_file))[0]
    print(f"🖼️ Testing with: {os.path.basename(test_file)}")

    try:
        # Load the original image
        original_img = load_image_smart_enhanced(test_file)

        # Resize for easier viewing (max 800px width)
        if original_img.width > 800:
            ratio = 800 / original_img.width
            new_height = int(original_img.height * ratio)
            original_img = original_img.resize(
                (800, new_height), Image.Resampling.LANCZOS
            )

        print(f"   📐 Resized to: {original_img.width}x{original_img.height}")

        # Apply both sports presets
        sports_result, sports_history = apply_photoshop_preset(
            original_img, "sports_action"
        )
        sports_raw_result, sports_raw_history = apply_photoshop_preset(
            original_img, "sports_action_raw"
        )

        # Create comparison image (side by side)
        total_width = original_img.width * 3 + 40  # 3 images + spacing
        total_height = original_img.height + 60  # Image + text space

        comparison = Image.new(
            "RGB", (total_width, total_height), color=(240, 240, 240)
        )

        # Paste images
        comparison.paste(original_img, (10, 50))
        comparison.paste(sports_result, (original_img.width + 20, 50))
        comparison.paste(sports_raw_result, (original_img.width * 2 + 30, 50))

        # Add labels
        draw = ImageDraw.Draw(comparison)
        try:
            # Try to use a better font
            font = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font = ImageFont.load_default()

        # Labels
        draw.text((10, 10), "Original", fill=(0, 0, 0), font=font)
        draw.text(
            (original_img.width + 20, 10),
            "Sports Action (JPEG)",
            fill=(0, 0, 0),
            font=font,
        )
        draw.text(
            (original_img.width * 2 + 30, 10),
            "Sports Action RAW",
            fill=(0, 0, 0),
            font=font,
        )

        # Add processing details
        draw.text((10, 30), "No processing", fill=(100, 100, 100), font=font)
        draw.text(
            (original_img.width + 20, 30),
            "Exp: +0.04, Shadows: +10, Midtone Protection",
            fill=(100, 100, 100),
            font=font,
        )
        draw.text(
            (original_img.width * 2 + 30, 30),
            "Exp: +0.02, Shadows: +5, Midtone Protection",
            fill=(100, 100, 100),
            font=font,
        )

        # Save comparison
        comparison_path = os.path.join(output_dir, f"{filename}_sports_comparison.jpg")
        comparison.save(comparison_path, "JPEG", quality=90)
        print(f"✅ Comparison saved: {comparison_path}")

        # Analyze brightness in different regions
        analyze_brightness_regions(original_img, sports_result, sports_raw_result)

    except Exception as e:
        print(f"❌ Error processing {test_file}: {e}")
        import traceback

        traceback.print_exc()


def analyze_brightness_regions(original, sports_action, sports_raw):
    """Analyze brightness in different regions to show sand/ground improvement"""
    print("\n📊 Brightness Analysis (sand/ground protection):")

    # Convert to numpy arrays
    orig_array = np.array(original)
    sports_array = np.array(sports_action)
    raw_array = np.array(sports_raw)

    # Analyze bottom third (where sand/ground typically appears)
    height = orig_array.shape[0]
    bottom_third = height * 2 // 3

    # Get bottom region brightness
    orig_bottom = orig_array[bottom_third:, :, :].mean()
    sports_bottom = sports_array[bottom_third:, :, :].mean()
    raw_bottom = raw_array[bottom_third:, :, :].mean()

    print("   🏖️  Bottom Region (sand/ground area):")
    print(f"      Original:     {orig_bottom:.1f}")
    print(
        f"      Sports Action: {sports_bottom:.1f} ({sports_bottom - orig_bottom:+.1f})"
    )
    print(f"      Sports RAW:   {raw_bottom:.1f} ({raw_bottom - orig_bottom:+.1f})")

    # Analyze overall brightness
    orig_overall = orig_array.mean()
    sports_overall = sports_array.mean()
    raw_overall = raw_array.mean()

    print("   🌍 Overall Image:")
    print(f"      Original:     {orig_overall:.1f}")
    print(
        f"      Sports Action: {sports_overall:.1f} ({sports_overall - orig_overall:+.1f})"
    )
    print(f"      Sports RAW:   {raw_overall:.1f} ({raw_overall - orig_overall:+.1f})")

    # Calculate improvement ratio
    sports_ratio = (
        (sports_bottom - orig_bottom) / (sports_overall - orig_overall)
        if sports_overall != orig_overall
        else 0
    )
    raw_ratio = (
        (raw_bottom - orig_bottom) / (raw_overall - orig_overall)
        if raw_overall != orig_overall
        else 0
    )

    print("\n🎯 Sand Protection Effectiveness:")
    print("   Lower values = better sand protection (less brightening in ground areas)")
    print(f"   Sports Action ratio: {sports_ratio:.2f}")
    print(f"   Sports RAW ratio:   {raw_ratio:.2f}")

    if sports_ratio < 1.0 and raw_ratio < 1.0:
        print("   ✅ Good: Ground areas brightened less than overall image")
    else:
        print("   ⚠️  Warning: Ground areas might still be over-brightened")


if __name__ == "__main__":
    create_comparison_for_sports_images()

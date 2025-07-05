"""
Comprehensive JPEG vs NEF processing analysis tool.
Analyzes differences in processing results and provides optimization recommendations.
"""

import os
import sys
import time

import numpy as np
from PIL import Image, ImageStat

from utils.photoshop_tools import PHOTOSHOP_PRESETS, apply_photoshop_preset

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


# Simplified functions for analysis without rawpy dependency

def load_image_smart(filepath):
    """Simplified image loader for analysis"""
    return Image.open(filepath).convert('RGB')


def is_raw_file(filepath):
    """Check if file is a RAW format"""
    raw_extensions = ['.nef', '.cr2', '.arw', '.dng', '.raf', '.orf']
    return any(filepath.lower().endswith(ext) for ext in raw_extensions)


def analyze_image_properties(image, label=""):
    """Analyze key image properties"""

    # Basic stats
    stat = ImageStat.Stat(image)

    # Convert to numpy for detailed analysis
    img_array = np.array(image)

    results = {
        'label': label,
        'dimensions': image.size,
        'mean_brightness': stat.mean,
        'stddev_brightness': stat.stddev,
        'color_range': {
            'red': (img_array[:, :, 0].min(), img_array[:, :, 0].max()),
            'green': (img_array[:, :, 1].min(), img_array[:, :, 1].max()),
            'blue': (img_array[:, :, 2].min(), img_array[:, :, 2].max())
        },
        'histogram_peaks': [],
        'dynamic_range_utilization': 0
    }

    # Calculate dynamic range utilization
    for channel in range(3):
        channel_data = img_array[:, :, channel]
        channel_range = channel_data.max() - channel_data.min()
        results['dynamic_range_utilization'] += channel_range / 255.0

    results['dynamic_range_utilization'] /= 3  # Average across channels

    return results


def compare_format_processing(jpeg_file, nef_file, preset_name='sports_action'):
    """Compare processing results between JPEG and NEF formats"""

    print("🔬 JPEG vs NEF Processing Analysis")
    print(f"📁 JPEG: {os.path.basename(jpeg_file)}")
    print(f"📁 NEF:  {os.path.basename(nef_file)}")
    print(f"🎨 Preset: {preset_name}")
    print("=" * 80)

    try:
        # Load original files
        print("📂 Loading original files...")
        start_time = time.time()
        jpeg_orig = load_image_smart(jpeg_file)
        jpeg_load_time = time.time() - start_time

        start_time = time.time()
        nef_orig = load_image_smart(nef_file)
        nef_load_time = time.time() - start_time

        print(f"⏱️  JPEG loaded in: {jpeg_load_time:.2f}s")
        print(f"⏱️  NEF loaded in:  {nef_load_time:.2f}s")
        print(f"⏱️  NEF is {nef_load_time / jpeg_load_time:.1f}x slower to load")

        # Analyze original properties
        print("\n📊 Original Image Analysis:")
        jpeg_props = analyze_image_properties(jpeg_orig, "JPEG Original")
        nef_props = analyze_image_properties(nef_orig, "NEF Original")

        print_image_comparison(jpeg_props, nef_props)

        # Apply preset processing
        print(f"\n🎨 Applying '{preset_name}' preset...")

        start_time = time.time()
        jpeg_processed, jpeg_history = apply_photoshop_preset(
            jpeg_orig, preset_name)
        jpeg_process_time = time.time() - start_time

        start_time = time.time()
        nef_processed, nef_history = apply_photoshop_preset(
            nef_orig, preset_name)
        nef_process_time = time.time() - start_time

        print(f"⏱️  JPEG processed in: {jpeg_process_time:.2f}s")
        print(f"⏱️  NEF processed in:  {nef_process_time:.2f}s")

        # Analyze processed results
        print("\n📊 Processed Image Analysis:")
        jpeg_processed_props = analyze_image_properties(
            jpeg_processed, "JPEG Processed")
        nef_processed_props = analyze_image_properties(
            nef_processed, "NEF Processed")

        print_image_comparison(jpeg_processed_props, nef_processed_props)

        # Calculate processing impact
        print("\n📈 Processing Impact Analysis:")
        analyze_processing_impact(jpeg_props, jpeg_processed_props, "JPEG")
        analyze_processing_impact(nef_props, nef_processed_props, "NEF")

        # Recommendations
        print("\n💡 Format-Specific Recommendations:")
        provide_format_recommendations(jpeg_props, nef_props, preset_name)

        return {
            'jpeg_original': jpeg_props,
            'nef_original': nef_props,
            'jpeg_processed': jpeg_processed_props,
            'nef_processed': nef_processed_props,
            'preset_used': preset_name,
            'processing_history': {
                'jpeg': jpeg_history,
                'nef': nef_history
            }
        }

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None


def print_image_comparison(props1, props2):
    """Print side-by-side comparison of image properties"""

    print(f"\n{'Property':<25} {'JPEG':<20} {'NEF':<20} {'Difference':<15}")
    print("-" * 80)

    # Dimensions
    print(
        f"{'Dimensions':<25} {str(props1['dimensions']):<20} {str(props2['dimensions']):<20} {'-':<15}")

    # Mean brightness (average across RGB)
    jpeg_brightness = sum(props1['mean_brightness']) / 3
    nef_brightness = sum(props2['mean_brightness']) / 3
    brightness_diff = nef_brightness - jpeg_brightness

    print(f"{'Mean Brightness':<25} {jpeg_brightness:<20.1f} {nef_brightness:<20.1f} {brightness_diff:+.1f}")

    # Dynamic range utilization
    dr_diff = props2['dynamic_range_utilization'] - \
        props1['dynamic_range_utilization']
    print(
        f"{'Dynamic Range Use':<25} {props1['dynamic_range_utilization']:<20.3f} {props2['dynamic_range_utilization']:<20.3f} {dr_diff:+.3f}")

    # Color ranges
    for color, idx in [('Red Range', 0), ('Green Range', 1), ('Blue Range', 2)]:
        jpeg_range = props1['color_range'][color.lower().split()[0]]
        nef_range = props2['color_range'][color.lower().split()[0]]
        jpeg_span = jpeg_range[1] - jpeg_range[0]
        nef_span = nef_range[1] - nef_range[0]
        span_diff = nef_span - jpeg_span

        print(f"{color:<25} {jpeg_span:<20} {nef_span:<20} {span_diff:+}")


def analyze_processing_impact(original_props, processed_props, format_name):
    """Analyze how processing affected the image"""

    print(f"\n🔍 {format_name} Processing Impact:")

    # Brightness change
    orig_brightness = sum(original_props['mean_brightness']) / 3
    proc_brightness = sum(processed_props['mean_brightness']) / 3
    brightness_change = (
        (proc_brightness - orig_brightness) / orig_brightness) * 100

    print(f"   Brightness change: {brightness_change:+.1f}%")

    # Dynamic range change
    dr_change = processed_props['dynamic_range_utilization'] - \
        original_props['dynamic_range_utilization']
    dr_change_percent = (
        dr_change / original_props['dynamic_range_utilization']) * 100

    print(f"   Dynamic range change: {dr_change_percent:+.1f}%")

    # Color range changes
    for color in ['red', 'green', 'blue']:
        orig_range = original_props['color_range'][color]
        proc_range = processed_props['color_range'][color]
        orig_span = orig_range[1] - orig_range[0]
        proc_span = proc_range[1] - proc_range[0]

        if orig_span > 0:
            span_change = ((proc_span - orig_span) / orig_span) * 100
            print(f"   {color.title()} range change: {span_change:+.1f}%")


def provide_format_recommendations(jpeg_props, nef_props, preset_name):
    """Provide recommendations based on format analysis"""

    print("\n💡 Optimization Recommendations:")

    # Dynamic range comparison
    nef_dr = nef_props['dynamic_range_utilization']
    jpeg_dr = jpeg_props['dynamic_range_utilization']

    if nef_dr > jpeg_dr * 1.2:
        print("   🎯 NEF has significantly more dynamic range - use more aggressive presets")
        print("   📈 Consider 'sports_action_raw' instead of 'sports_action' for NEF files")

    # Brightness comparison
    nef_brightness = sum(nef_props['mean_brightness']) / 3
    jpeg_brightness = sum(jpeg_props['mean_brightness']) / 3

    if abs(nef_brightness - jpeg_brightness) > 10:
        if nef_brightness > jpeg_brightness:
            print("   🔆 NEF is brighter - reduce exposure adjustment for NEF")
        else:
            print("   🔅 NEF is darker - increase exposure adjustment for NEF")

    # Color range comparison
    print("\n🎨 Preset Optimization Suggestions:")

    if preset_name == 'sports_action':
        print("   For JPEG files:")
        print("   - Current 'sports_action' preset is well-suited")
        print("   - Focus on clarity and structure for sharpness")

        print("   For NEF files:")
        print("   - Use 'sports_action_raw' for better results")
        print("   - Higher vibrance and structure values work better")
        print("   - More aggressive highlight/shadow recovery is safe")


def test_all_sports_presets():
    """Test all sports-related presets for comparison"""

    print("🏃‍♂️ SPORTS PRESET COMPARISON")
    print("=" * 60)

    sports_presets = ['sports_action', 'sports_action_raw',
                      'portrait_natural', 'natural_wildlife']

    print(f"{'Parameter':<15}", end="")
    for preset in sports_presets:
        print(f"{preset.replace('_', ' ').title()[:12]:<14}", end="")
    print()
    print("-" * 80)

    params = ['exposure', 'highlights', 'shadows',
              'vibrance', 'saturation', 'clarity', 'structure']

    for param in params:
        print(f"{param:<15}", end="")
        for preset in sports_presets:
            value = PHOTOSHOP_PRESETS[preset].get(param, 0)
            print(f"{value:<14}", end="")
        print()

    print("\n💭 Key Differences:")
    print("   🔸 sports_action: Balanced for JPEG sports photos")
    print("   🔸 sports_action_raw: More aggressive for NEF/RAW files")
    print("   🔸 portrait_natural: Good for close-up athlete shots")
    print("   🔸 natural_wildlife: Alternative for outdoor sports")


if __name__ == "__main__":
    # Example usage
    print("📸 JPEG vs NEF Processing Analysis Tool")
    print("=" * 50)

    # Test preset comparison
    test_all_sports_presets()

    # If you have specific files to test, uncomment and modify these lines:
    # jpeg_file = "path/to/your/sports_photo.jpg"
    # nef_file = "path/to/your/sports_photo.NEF"
    # results = compare_format_processing(jpeg_file, nef_file, 'sports_action')

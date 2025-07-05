"""
Optimized preset recommendations based on JPEG vs NEF processing analysis.
"""

import os
import sys

from utils.photoshop_tools import PHOTOSHOP_PRESETS

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def create_optimized_presets():
    """Create format-specific optimized presets"""

    # Enhanced JPEG preset (slightly more conservative)
    jpeg_sports_optimized = {
        "exposure": 0.08,  # Slightly less than RAW
        "highlights": -12,  # Less aggressive than RAW
        "shadows": 18,  # Conservative shadow lift
        "vibrance": 15,  # Good for JPEG color space
        "saturation": 3,  # Minimal saturation boost
        "clarity": 10,  # Good clarity for JPEG
        "structure": 12,  # Appropriate detail enhancement
        "temperature": 2,  # Subtle warmth
        "skin_smoothing": 0,  # No smoothing for sports
    }

    # Enhanced NEF preset (more aggressive)
    nef_sports_optimized = {
        "exposure": 0.15,  # More exposure headroom
        "highlights": -25,  # Much more aggressive recovery
        "shadows": 30,  # Strong shadow lift
        "vibrance": 30,  # Much higher vibrance for RAW
        "saturation": 8,  # More saturation for RAW
        "clarity": 20,  # Higher clarity for RAW sharpness
        "structure": 25,  # Strong detail enhancement
        "temperature": 8,  # More warmth for appealing skin
        "skin_smoothing": 0,  # No smoothing for sports
    }

    return {
        "sports_jpeg_optimized": jpeg_sports_optimized,
        "sports_nef_optimized": nef_sports_optimized,
    }


def analyze_preset_differences():
    """Analyze differences between existing and optimized presets"""

    print("🔬 PRESET OPTIMIZATION ANALYSIS")
    print("=" * 80)

    optimized = create_optimized_presets()
    existing_presets = {
        "sports_action": PHOTOSHOP_PRESETS["sports_action"],
        "sports_action_raw": PHOTOSHOP_PRESETS["sports_action_raw"],
    }

    all_presets = {**existing_presets, **optimized}

    # Display comparison table
    print(f"{'Parameter':<15}", end="")
    for name in all_presets.keys():
        display_name = name.replace("_", " ").title()[:12]
        print(f"{display_name:<15}", end="")
    print()
    print("-" * 95)

    params = [
        "exposure",
        "highlights",
        "shadows",
        "vibrance",
        "saturation",
        "clarity",
        "structure",
        "temperature",
    ]

    for param in params:
        print(f"{param:<15}", end="")
        for preset_name, preset_values in all_presets.items():
            value = preset_values.get(param, 0)
            print(f"{value:<15}", end="")
        print()

    print("\n📊 Key Insights:")
    print("   🔸 JPEG files benefit from moderate adjustments")
    print("   🔸 NEF files can handle much more aggressive processing")
    print("   🔸 RAW files need higher vibrance to match JPEG color richness")
    print("   🔸 Structure/clarity can be pushed higher on RAW without artifacts")

    return optimized


def recommend_processing_strategy():
    """Recommend processing strategy based on file format"""

    print("\n🎯 PROCESSING STRATEGY RECOMMENDATIONS")
    print("=" * 60)

    print("📁 For JPEG Sports Photos:")
    print("   ✅ Use 'sports_action' preset as base")
    print("   ✅ Focus on: Clarity (10-12), Structure (12-15), Vibrance (15-18)")
    print("   ✅ Be conservative with: Exposure (≤0.1), Highlights (≥-15)")
    print("   ✅ Avoid: Over-saturation, excessive clarity")

    print("\n📁 For NEF/RAW Sports Photos:")
    print("   ✅ Use 'sports_action_raw' preset as base")
    print("   ✅ Push harder: Vibrance (25-30), Structure (20-25), Clarity (15-20)")
    print("   ✅ Aggressive recovery: Highlights (-20 to -30), Shadows (+25 to +35)")
    print("   ✅ More exposure headroom: Up to +0.2 safely")

    print("\n🔧 Custom Adjustment Guidelines:")
    print("   📈 If image looks flat after processing:")
    print("      - JPEG: Increase vibrance by 3-5")
    print("      - NEF: Increase vibrance by 5-8 and clarity by 2-3")

    print("   📉 If image looks over-processed:")
    print("      - JPEG: Reduce clarity and structure by 2-3")
    print("      - NEF: Reduce all values by 10-15% and re-evaluate")

    print("   🎨 For better color in sports:")
    print("      - JPEG: Focus on vibrance over saturation")
    print("      - NEF: Use both vibrance and moderate saturation")


def create_format_detection_guide():
    """Create a guide for automatically detecting optimal settings"""

    print("\n🤖 AUTOMATIC FORMAT OPTIMIZATION")
    print("=" * 50)

    print("💡 Implementation Strategy:")
    print("   1. Detect file format (JPEG vs NEF/RAW)")
    print("   2. Choose appropriate base preset")
    print("   3. Apply format-specific multipliers")
    print("   4. Fine-tune based on image analysis")

    print("\n🔧 Preset Selection Logic:")
    print("   if file_extension.lower() in ['.nef', '.cr2', '.arw', '.dng']:")
    print("       use 'sports_action_raw' or custom NEF preset")
    print("   elif file_extension.lower() in ['.jpg', '.jpeg']:")
    print("       use 'sports_action' or custom JPEG preset")

    print("\n⚡ Performance Considerations:")
    print("   📊 NEF files: 2-4x longer processing time")
    print("   📊 Better quality headroom for adjustments")
    print("   📊 More memory usage during processing")
    print("   📊 Larger output file sizes")


if __name__ == "__main__":
    print("🎨 JPEG vs NEF PRESET OPTIMIZATION")
    print("=" * 50)

    # Analyze differences
    optimized_presets = analyze_preset_differences()

    # Provide recommendations
    recommend_processing_strategy()

    # Implementation guide
    create_format_detection_guide()

    print("\n🎯 NEXT STEPS:")
    print("   1. Test current 'sports_action_raw' preset on your NEF files")
    print("   2. Compare results with 'sports_action' on JPEG")
    print("   3. Fine-tune based on your specific images")
    print("   4. Consider implementing automatic format detection")

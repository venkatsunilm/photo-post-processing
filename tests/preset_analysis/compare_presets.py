"""
Comprehensive preset comparison and analysis tool for photo enhancement modes.
Provides detailed comparison of all available presets and their parameters.
"""

import os
import sys

from utils.photoshop_tools import PHOTOSHOP_PRESETS

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def compare_all_presets():
    """Compare all available presets with detailed analysis"""

    print("🎨 COMPLETE PHOTO ENHANCEMENT PRESET COMPARISON")
    print("=" * 100)

    # All parameters
    params = [
        "exposure",
        "highlights",
        "shadows",
        "vibrance",
        "saturation",
        "clarity",
        "structure",
        "temperature",
        "skin_smoothing",
    ]

    # Print header
    print(f"{'Parameter':<15}", end="")
    for preset_name in PHOTOSHOP_PRESETS.keys():
        display_name = preset_name.replace("_", " ").title()[
            :12
        ]  # Truncate for alignment
        print(f"{display_name:<14}", end="")
    print()
    print("-" * 120)

    # Print each parameter
    for param in params:
        print(f"{param:<15}", end="")
        for preset_name, preset_values in PHOTOSHOP_PRESETS.items():
            value = preset_values.get(param, 0)
            print(f"{value:<14}", end="")
        print()

    print("\n" + "=" * 100)


def compare_sports_presets():
    """Detailed comparison for sports photography"""

    sports_relevant = [
        "portrait_subtle",
        "portrait_natural",
        "sports_action",
        "natural_wildlife",
        "landscape",
    ]

    print("🏃‍♂️ SPORTS PHOTOGRAPHY PRESET COMPARISON")
    print("=" * 80)

    presets = {k: v for k, v in PHOTOSHOP_PRESETS.items() if k in sports_relevant}

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

    print(f"{'Parameter':<15}", end="")
    for preset_name in presets.keys():
        display_name = preset_name.replace("_", " ").title()
        print(f"{display_name:<16}", end="")
    print()
    print("-" * 95)

    for param in params:
        print(f"{param:<15}", end="")
        for preset_name, preset_values in presets.items():
            value = preset_values.get(param, 0)
            print(f"{value:<16}", end="")
        print()

    print("\n🎯 SPORTS PHOTOGRAPHY RECOMMENDATIONS:")
    print("• 🥇 BEST: Sports Action - Optimized for dynamic sports photography")
    print("• 🥈 GOOD: Natural Wildlife - For outdoor sports with natural feel")
    print("• 🥉 OK: Portrait Natural - For athlete close-ups and team photos")
    print("• ❌ AVOID: Portrait Subtle - Too gentle for sports action")

    print("\n📸 SPORTS ACTION PRESET BENEFITS:")
    print("✅ High Clarity (12) - Sharp player details and facial expressions")
    print("✅ High Structure (15) - Enhanced equipment, logos, and uniform details")
    print("✅ Strong Vibrance (18) - Vibrant team colors without oversaturation")
    print("✅ Shadow Recovery (20) - See faces under caps and helmets")
    print("✅ Highlight Control (-15) - Handle bright stadium/field lighting")
    print("✅ No Smoothing (0) - Preserve athletic authenticity")


def analyze_preset_purpose():
    """Analyze each preset's intended purpose and use cases"""

    preset_analysis = {
        "portrait_subtle": {
            "purpose": "Minimal enhancement preserving natural look",
            "best_for": "Professional headshots, family portraits, natural beauty",
            "avoid_for": "Action shots, dramatic scenes, sports",
        },
        "portrait_natural": {
            "purpose": "Balanced portrait enhancement",
            "best_for": "General portraits, team photos, social media",
            "avoid_for": "Heavy action, challenging lighting",
        },
        "portrait_dramatic": {
            "purpose": "Enhanced contrast with natural skin tones",
            "best_for": "Fashion, dramatic portraits, artistic shots",
            "avoid_for": "Natural documentary style, subtle work",
        },
        "studio_portrait": {
            "purpose": "Clean, professional studio look",
            "best_for": "Corporate headshots, model portfolios, studio work",
            "avoid_for": "Outdoor photography, natural lighting",
        },
        "sports_action": {
            "purpose": "Dynamic sports photography optimization",
            "best_for": "Sports action, team celebrations, outdoor athletics",
            "avoid_for": "Subtle portraits, indoor formal shots",
        },
        "natural_wildlife": {
            "purpose": "Nature and wildlife enhancement",
            "best_for": "Animals, nature, outdoor photography",
            "avoid_for": "Portraits with skin smoothing needs",
        },
        "overexposed_recovery": {
            "purpose": "Fix bright/washed out photos",
            "best_for": "Overexposed shots, bright outdoor scenes",
            "avoid_for": "Properly exposed photos, dark scenes",
        },
    }

    print("📋 PRESET PURPOSE AND USE CASE ANALYSIS")
    print("=" * 80)

    for preset_name, analysis in preset_analysis.items():
        if preset_name in PHOTOSHOP_PRESETS:
            display_name = preset_name.replace("_", " ").title()
            print(f"\n🎯 {display_name.upper()}")
            print(f"Purpose: {analysis['purpose']}")
            print(f"✅ Best for: {analysis['best_for']}")
            print(f"❌ Avoid for: {analysis['avoid_for']}")


def main():
    """Run all comparison tools"""
    print("🔬 PHOTO PROCESSING PRESET ANALYSIS SUITE")
    print("=" * 60)
    print("1. Compare All Presets")
    print("2. Sports Photography Focus")
    print("3. Preset Purpose Analysis")
    print("4. Run All Tests")
    print("=" * 60)

    choice = input("Choose analysis (1-4): ").strip()

    if choice == "1":
        compare_all_presets()
    elif choice == "2":
        compare_sports_presets()
    elif choice == "3":
        analyze_preset_purpose()
    elif choice == "4":
        compare_all_presets()
        print("\n")
        compare_sports_presets()
        print("\n")
        analyze_preset_purpose()
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()

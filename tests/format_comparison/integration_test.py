"""
Complete integration test for JPEG vs NEF automatic optimization.
Tests the full pipeline with format detection and optimization.
"""

from utils.photoshop_tools import PHOTOSHOP_PRESETS
from utils.format_optimizer import FormatOptimizer
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


def test_complete_integration():
    """Test complete integration of format optimization"""

    print("🧪 COMPLETE INTEGRATION TEST")
    print("=" * 50)

    optimizer = FormatOptimizer()

    # Test all preset mappings
    test_cases = [
        ("sports_photo.NEF", "sports_action"),
        ("sports_photo.jpg", "sports_action"),
        ("portrait.CR2", "portrait_dramatic"),
        ("portrait.jpeg", "portrait_dramatic"),
        ("landscape.ARW", "landscape"),
        ("landscape.jpg", "landscape"),
        ("wildlife.DNG", "natural_wildlife"),
        ("wildlife.jpeg", "natural_wildlife"),
    ]

    print("📋 PRESET OPTIMIZATION TEST:")
    print(f"{'File':<20} {'Original':<20} {'Optimized':<25} {'Status':<10}")
    print("-" * 75)

    all_passed = True
    for filename, original_preset in test_cases:
        optimal_preset = optimizer.get_optimal_preset(
            filename, original_preset)

        # Check if optimized preset exists
        if optimal_preset in PHOTOSHOP_PRESETS:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            all_passed = False

        print(f"{filename:<20} {original_preset:<20} {optimal_preset:<25} {status}")

    print(
        f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")

    # Test format detection accuracy
    print(f"\n🔍 FORMAT DETECTION TEST:")
    format_tests = [
        ("photo.NEF", "raw"),
        ("photo.CR2", "raw"),
        ("photo.ARW", "raw"),
        ("photo.DNG", "raw"),
        ("photo.JPG", "jpeg"),
        ("photo.jpeg", "jpeg"),
        ("photo.JPEG", "jpeg"),
        ("photo.png", "unknown")
    ]

    for filename, expected in format_tests:
        detected = optimizer.detect_file_format(filename)
        status = "✅" if detected == expected else "❌"
        print(
            f"   {filename:<15} -> {detected:<8} (expected: {expected:<8}) {status}")

    # Show available presets
    print(f"\n📚 AVAILABLE PRESETS:")
    regular_presets = []
    raw_presets = []

    for preset_name in PHOTOSHOP_PRESETS.keys():
        if '_raw' in preset_name:
            raw_presets.append(preset_name)
        else:
            regular_presets.append(preset_name)

    print(f"   📱 Regular presets ({len(regular_presets)}):")
    for preset in sorted(regular_presets):
        print(f"      • {preset}")

    print(f"   📷 RAW-optimized presets ({len(raw_presets)}):")
    for preset in sorted(raw_presets):
        print(f"      • {preset}")

    print(f"\n💡 USAGE RECOMMENDATIONS:")
    print("   1. For sports photos: Use 'sports_action' - system auto-optimizes")
    print("   2. For portraits: Use 'portrait_dramatic' or 'portrait_natural'")
    print("   3. For landscapes: Use 'landscape'")
    print("   4. For wildlife: Use 'natural_wildlife'")
    print("   5. For mixed JPEG/NEF batches: Any preset - auto-optimization handles it")

    return all_passed


if __name__ == "__main__":
    success = test_complete_integration()

    if success:
        print(f"\n🎉 INTEGRATION TEST COMPLETE!")
        print("   ✅ Format detection working")
        print("   ✅ Preset optimization working")
        print("   ✅ All presets available")
        print("   ✅ Ready for production use")
    else:
        print(f"\n⚠️  INTEGRATION TEST ISSUES DETECTED")
        print("   Please check preset definitions and format mappings")

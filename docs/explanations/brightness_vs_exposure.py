"""
Demonstration: Exposure vs Brightness Adjustments in Photoshop Tools

This script explains why we use exposure adjustments and when linear brightness might be useful.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


def explain_brightness_vs_exposure():
    """Explain the difference between brightness and exposure adjustments"""
    print("📸 BRIGHTNESS vs EXPOSURE in Photo Processing")
    print("=" * 60)

    print("\n🎛️ CURRENT IMPLEMENTATION:")
    print("✅ exposure_adjustment() - Professional exponential scaling")
    print("✅ brightness_adjustment() - Simple linear scaling (just added)")

    print("\n🔍 KEY DIFFERENCES:")
    print("\n📐 EXPOSURE ADJUSTMENT (Professional):")
    print("   • Formula: factor = 2 ** exposure_value")
    print("   • Range: -2.0 to +2.0 (camera stops)")
    print("   • Examples:")
    print("     - exposure_value = +1.0 → factor = 2.0 (double brightness)")
    print("     - exposure_value = +0.5 → factor = 1.41 (√2 brighter)")
    print("     - exposure_value = -1.0 → factor = 0.5 (half brightness)")
    print("   • Advantage: Mimics real camera behavior")
    print("   • Use case: Professional photo editing")

    print("\n📏 BRIGHTNESS ADJUSTMENT (Simple):")
    print("   • Formula: factor = 1.0 + (brightness_value / 100.0)")
    print("   • Range: -100 to +100 (percentage)")
    print("   • Examples:")
    print("     - brightness_value = +50 → factor = 1.5 (50% brighter)")
    print("     - brightness_value = +100 → factor = 2.0 (double brightness)")
    print("     - brightness_value = -50 → factor = 0.5 (50% darker)")
    print("   • Advantage: Simple, intuitive percentage")
    print("   • Use case: Quick adjustments, basic editing")

    print("\n🎯 WHEN TO USE EACH:")
    print("\n🏆 Use EXPOSURE for:")
    print("   ✅ Professional photo processing")
    print("   ✅ RAW file adjustments")
    print("   ✅ When matching camera/Lightroom behavior")
    print("   ✅ Precise control over dynamic range")

    print("\n⚡ Use BRIGHTNESS for:")
    print("   ✅ Quick, simple adjustments")
    print("   ✅ User-friendly controls (sliders)")
    print("   ✅ When users think in percentages")
    print("   ✅ Basic image correction")

    print("\n🔧 IMPLEMENTATION STATUS:")
    print("   ✅ exposure_adjustment() - Already implemented")
    print("   ✅ brightness_adjustment() - Just added")
    print("   📋 Both methods available in PhotoshopStyleEnhancer class")

    print("\n💡 RECOMMENDATION:")
    print("   • Keep using EXPOSURE for all current presets (professional)")
    print("   • Add BRIGHTNESS option to custom adjustments menu for user-friendly control")
    print("   • This gives users both professional and simple options")


def demonstrate_values():
    """Show numerical examples of the difference"""
    print("\n📊 NUMERICAL COMPARISON:")
    print("=" * 40)
    print("Goal: Make image 50% brighter")
    print()
    print("Method 1 - Exposure:")
    print("   exposure_value = 0.585")  # log2(1.5) ≈ 0.585
    print("   factor = 2^0.585 = 1.5")
    print()
    print("Method 2 - Brightness:")
    print("   brightness_value = 50")
    print("   factor = 1.0 + (50/100) = 1.5")
    print()
    print("Result: Same factor, different input methods!")
    print("✅ Exposure: Professional camera-style input")
    print("✅ Brightness: User-friendly percentage input")


if __name__ == "__main__":
    explain_brightness_vs_exposure()
    demonstrate_values()

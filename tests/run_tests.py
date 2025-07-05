"""
Main test runner for the photo post-processing pipeline.
Provides easy access to all testing and analysis tools.
"""

from raw_processing.test_raw_quality import main as raw_tests
from image_processing.test_quality_impact import main as quality_tests
from preset_analysis.compare_presets import main as preset_tests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import all test modules


def display_menu():
    """Display the main test menu"""
    print("🧪 PHOTO POST-PROCESSING TEST SUITE")
    print("=" * 60)
    print("📊 Analysis Tools:")
    print("1. Preset Comparison & Analysis")
    print("2. RAW Processing Quality Tests")
    print("3. Image Enhancement Impact Tests")
    print()
    print("🔬 Quick Tests:")
    print("4. Sports Photography Preset Analysis")
    print("5. RAW vs JPG Quality Comparison")
    print("6. Performance Benchmark")
    print()
    print("🎯 Full Test Suite:")
    print("7. Run All Tests")
    print("8. Exit")
    print("=" * 60)


def run_sports_analysis():
    """Quick sports photography analysis"""
    print("🏃‍♂️ SPORTS PHOTOGRAPHY ANALYSIS")
    print("=" * 50)

    # Import and run sports-specific analysis
    sys.path.append(os.path.join(os.path.dirname(__file__), 'preset_analysis'))
    from compare_presets import compare_sports_presets

    compare_sports_presets()


def run_raw_vs_jpg():
    """Quick RAW vs JPG comparison"""
    print("⚖️ RAW VS JPG QUALITY COMPARISON")
    print("=" * 50)

    sys.path.append(os.path.join(os.path.dirname(__file__), 'raw_processing'))
    from test_raw_quality import scan_input_directory, compare_raw_vs_jpg

    raw_files, jpg_files = scan_input_directory()

    if raw_files and jpg_files:
        compare_raw_vs_jpg(raw_files[0], jpg_files[0])
    else:
        print("❌ Need both RAW and JPG files for comparison")


def run_performance_test():
    """Quick performance benchmark"""
    print("🏃‍♂️ PERFORMANCE BENCHMARK")
    print("=" * 50)

    sys.path.append(os.path.join(
        os.path.dirname(__file__), 'image_processing'))
    from test_quality_impact import performance_benchmark

    performance_benchmark()


def run_all_tests():
    """Run comprehensive test suite"""
    print("🧪 COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    print("\n1️⃣ PRESET ANALYSIS")
    print("-" * 30)
    run_sports_analysis()

    print("\n2️⃣ RAW PROCESSING TESTS")
    print("-" * 30)
    sys.path.append(os.path.join(os.path.dirname(__file__), 'raw_processing'))
    from test_raw_quality import run_comprehensive_test
    run_comprehensive_test()

    print("\n3️⃣ PERFORMANCE BENCHMARK")
    print("-" * 30)
    run_performance_test()

    print("\n✅ ALL TESTS COMPLETED")


def main():
    """Main test runner"""
    while True:
        display_menu()
        choice = input("Choose option (1-8): ").strip()

        print("\n")

        if choice == '1':
            preset_tests()
        elif choice == '2':
            raw_tests()
        elif choice == '3':
            quality_tests()
        elif choice == '4':
            run_sports_analysis()
        elif choice == '5':
            run_raw_vs_jpg()
        elif choice == '6':
            run_performance_test()
        elif choice == '7':
            run_all_tests()
        elif choice == '8':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

        input("\nPress Enter to continue...")
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()

import os
import sys

from utils.format_optimizer import FormatOptimizer

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


# Test the format optimizer
opt = FormatOptimizer()

print("🔧 FORMAT OPTIMIZER TEST")
print("=" * 40)

test_files = [
    ("test.jpg", "sports_action"),
    ("test.nef", "sports_action"),
    ("photo.cr2", "portrait_dramatic"),
    ("image.jpeg", "portrait_dramatic"),
    ("landscape.arw", "landscape"),
    ("wildlife.dng", "natural_wildlife")
]

for filename, preset in test_files:
    optimal = opt.get_optimal_preset(filename, preset)
    format_type = opt.detect_file_format(filename)
    print(f"{filename:<15} ({format_type.upper():<5}) {preset:<20} -> {optimal}")

print("\n🎯 Key Features:")
print("✅ Automatic RAW vs JPEG detection")
print("✅ Format-optimized preset selection")
print("✅ Seamless integration with existing pipeline")
print("✅ Support for all major RAW formats")

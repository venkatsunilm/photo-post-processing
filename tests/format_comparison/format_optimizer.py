"""
Automatic format detection and preset selection for optimal processing results.
Integrates with the main processing pipeline to choose JPEG vs RAW presets automatically.
"""

import os
from pathlib import Path


class FormatOptimizer:
    """Automatically optimizes processing based on file format"""

    def __init__(self):
        self.raw_extensions = {'.nef', '.cr2', '.arw',
                               '.dng', '.raf', '.orf', '.rw2', '.pef', '.srw'}
        self.jpeg_extensions = {'.jpg', '.jpeg', '.jpe', '.jfif'}

        # Preset mapping for automatic selection
        self.preset_mapping = {
            'sports_action': {
                'raw': 'sports_action_raw',
                'jpeg': 'sports_action'
            },
            'portrait_dramatic': {
                'raw': 'portrait_dramatic',  # Could create a RAW version
                'jpeg': 'portrait_dramatic'
            },
            'portrait_natural': {
                'raw': 'portrait_natural',
                'jpeg': 'portrait_natural'
            },
            'portrait_subtle': {
                'raw': 'portrait_subtle',
                'jpeg': 'portrait_subtle'
            },
            'natural_wildlife': {
                'raw': 'natural_wildlife',
                'jpeg': 'natural_wildlife'
            },
            'landscape': {
                'raw': 'landscape',
                'jpeg': 'landscape'
            }
        }

    def detect_file_format(self, filepath):
        """Detect if file is RAW or JPEG format"""
        file_ext = Path(filepath).suffix.lower()

        if file_ext in self.raw_extensions:
            return 'raw'
        elif file_ext in self.jpeg_extensions:
            return 'jpeg'
        else:
            return 'unknown'

    def get_optimal_preset(self, filepath, requested_preset):
        """Get the optimal preset based on file format"""
        file_format = self.detect_file_format(filepath)

        if file_format == 'unknown':
            print(
                f"⚠️  Unknown format for {os.path.basename(filepath)}, using requested preset: {requested_preset}")
            return requested_preset

        # Check if we have a format-specific version
        if requested_preset in self.preset_mapping:
            optimal_preset = self.preset_mapping[requested_preset][file_format]

            if optimal_preset != requested_preset:
                print(
                    f"🔄 Format optimization: {os.path.basename(filepath)} ({file_format.upper()}) -> {optimal_preset}")

            return optimal_preset
        else:
            # For presets without format-specific versions, return as-is
            return requested_preset

    def analyze_batch_formats(self, file_paths):
        """Analyze file formats in a batch"""
        format_counts = {'raw': 0, 'jpeg': 0, 'unknown': 0}
        format_details = []

        for filepath in file_paths:
            file_format = self.detect_file_format(filepath)
            format_counts[file_format] += 1
            format_details.append({
                'file': os.path.basename(filepath),
                'format': file_format,
                'extension': Path(filepath).suffix.lower()
            })

        return format_counts, format_details

    def recommend_processing_strategy(self, file_paths, preset_name):
        """Recommend processing strategy for a batch of files"""
        format_counts, format_details = self.analyze_batch_formats(file_paths)

        print(f"\n📊 BATCH FORMAT ANALYSIS")
        print(f"=" * 50)
        print(f"📁 Total files: {len(file_paths)}")
        print(f"📷 RAW files: {format_counts['raw']}")
        print(f"🖼️  JPEG files: {format_counts['jpeg']}")
        print(f"❓ Unknown: {format_counts['unknown']}")

        if format_counts['raw'] > 0 and format_counts['jpeg'] > 0:
            print(f"\n💡 MIXED FORMAT STRATEGY:")
            print(
                f"   📷 RAW files will use: {self.get_optimal_preset('dummy.nef', preset_name)}")
            print(
                f"   🖼️  JPEG files will use: {self.get_optimal_preset('dummy.jpg', preset_name)}")
            print(
                f"   ⏱️  Expected processing time: {format_counts['raw'] * 3 + format_counts['jpeg']}x baseline")
        elif format_counts['raw'] > 0:
            print(f"\n💡 RAW-ONLY STRATEGY:")
            print(
                f"   📷 All files will use: {self.get_optimal_preset('dummy.nef', preset_name)}")
            print(f"   ⏱️  Expected processing time: ~3x baseline (RAW processing)")
        elif format_counts['jpeg'] > 0:
            print(f"\n💡 JPEG-ONLY STRATEGY:")
            print(
                f"   🖼️  All files will use: {self.get_optimal_preset('dummy.jpg', preset_name)}")
            print(f"   ⏱️  Expected processing time: ~1x baseline (fast JPEG processing)")

        return format_counts, format_details


def create_enhanced_presets():
    """Create additional format-specific presets for better optimization"""

    enhanced_presets = {
        # Enhanced RAW versions of existing presets
        'portrait_dramatic_raw': {
            'exposure': 0.12,               # More exposure headroom for RAW
            'highlights': -15,              # Stronger highlight recovery
            'shadows': 25,                  # More aggressive shadow lift
            'vibrance': 20,                 # Higher vibrance for RAW
            'saturation': 5,                # Some saturation for drama
            'clarity': 8,                   # Moderate clarity for natural look
            'structure': 12,                # More structure for RAW detail
            'temperature': 8,               # More warmth for appealing look
            'skin_smoothing': 3             # Minimal smoothing
        },

        'landscape_raw': {
            'exposure': 0.05,               # Slight exposure boost
            'highlights': -25,              # Strong highlight recovery for skies
            'shadows': 15,                  # Moderate shadow lift
            'vibrance': 30,                 # High vibrance for landscape colors
            'saturation': 15,               # More saturation for impact
            'clarity': 25,                  # High clarity for landscape detail
            'structure': 20,                # Strong detail enhancement
            'temperature': -3,              # Slightly cooler for landscapes
            'skin_smoothing': 0             # No smoothing for landscapes
        },

        'natural_wildlife_raw': {
            'exposure': 0.08,               # Slight brightness boost
            'highlights': -18,              # Moderate highlight recovery
            'shadows': 20,                  # Good shadow detail
            'vibrance': 18,                 # Enhanced natural colors
            'saturation': 3,                # Minimal artificial saturation
            'clarity': 12,                  # Good fur/feather texture
            'structure': 18,                # Strong natural details
            'temperature': 5,               # Slight warmth for natural look
            'skin_smoothing': 0             # No smoothing - preserve texture
        }
    }

    return enhanced_presets


def integration_example():
    """Example of how to integrate format optimization into the main pipeline"""

    print(f"\n🔧 INTEGRATION EXAMPLE")
    print(f"=" * 40)

    example_code = '''
# In your main processing pipeline:

from utils.format_optimizer import FormatOptimizer

# Initialize optimizer
optimizer = FormatOptimizer()

# During processing
def process_image(filepath, requested_preset):
    # Get optimal preset based on file format
    optimal_preset = optimizer.get_optimal_preset(filepath, requested_preset)
    
    # Load image (your existing smart loader handles RAW vs JPEG)
    image = load_image_smart(filepath)
    
    # Apply the format-optimized preset
    processed_image, history = apply_photoshop_preset(image, optimal_preset)
    
    return processed_image, history

# For batch processing
def process_batch(file_paths, preset_name):
    # Analyze the batch first
    optimizer.recommend_processing_strategy(file_paths, preset_name)
    
    results = []
    for filepath in file_paths:
        result = process_image(filepath, preset_name)
        results.append(result)
    
    return results
'''

    print(example_code)


if __name__ == "__main__":
    print("🎯 AUTOMATIC FORMAT OPTIMIZATION SYSTEM")
    print("="*50)

    # Initialize optimizer
    optimizer = FormatOptimizer()

    # Test format detection
    test_files = [
        "sports_photo.NEF",
        "portrait.CR2",
        "action_shot.jpg",
        "landscape.ARW",
        "team_photo.jpeg"
    ]

    print("🔍 FORMAT DETECTION TEST:")
    for file in test_files:
        format_type = optimizer.detect_file_format(file)
        optimal = optimizer.get_optimal_preset(file, 'sports_action')
        print(f"   📁 {file:<20} -> {format_type.upper():<6} -> {optimal}")

    # Show enhanced presets
    print(f"\n🎨 ENHANCED FORMAT-SPECIFIC PRESETS:")
    enhanced = create_enhanced_presets()
    for name, settings in enhanced.items():
        print(f"   ✨ {name}: Enhanced for RAW processing")

    # Integration example
    integration_example()

    print(f"\n📋 IMPLEMENTATION CHECKLIST:")
    print("   ✅ 1. Add FormatOptimizer to utils/")
    print("   ✅ 2. Update main pipeline to use get_optimal_preset()")
    print("   ✅ 3. Add enhanced RAW presets to photoshop_tools.py")
    print("   ✅ 4. Test with mixed JPEG/NEF batches")
    print("   ✅ 5. Monitor processing time differences")

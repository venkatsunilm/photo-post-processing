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
                'raw': 'portrait_dramatic_raw',
                'jpeg': 'portrait_dramatic'
            },
            'portrait_natural': {
                'raw': 'portrait_natural_raw',
                'jpeg': 'portrait_natural'
            },
            'portrait_subtle': {
                'raw': 'portrait_subtle_raw',
                'jpeg': 'portrait_subtle'
            },
            'natural_wildlife': {
                'raw': 'natural_wildlife_raw',
                'jpeg': 'natural_wildlife'
            },
            'landscape': {
                'raw': 'landscape_raw',
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
            return requested_preset

        # Check if we have a format-specific version
        if requested_preset in self.preset_mapping:
            optimal_preset = self.preset_mapping[requested_preset][file_format]
            return optimal_preset
        else:
            # For presets without format-specific versions, return as-is
            return requested_preset

    def should_use_raw_preset(self, filepath):
        """Check if file should use RAW-optimized processing"""
        return self.detect_file_format(filepath) == 'raw'

    def get_format_info(self, filepath):
        """Get detailed format information for a file"""
        file_format = self.detect_file_format(filepath)
        extension = Path(filepath).suffix.lower()
        filename = os.path.basename(filepath)

        return {
            'filename': filename,
            'format': file_format,
            'extension': extension,
            'is_raw': file_format == 'raw',
            'is_jpeg': file_format == 'jpeg'
        }

"""
Configuration settings for photo post-processing.
Contains resolution settings, file paths, and processing parameters.
"""

# Resolution configurations
RESOLUTIONS = {
    '2k': 2560 * 1440,  # Total pixels for 2K
    '4k': 3840 * 2160   # Total pixels for 4K
}

# File extension configurations
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')
IMAGE_EXTENSIONS_CASE = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')

# Input/Output configuration
DEFAULT_INPUT_PATH = r"C:\Users\harit\Downloads\28_06_Teraskatu 8 4k-20250629T063835Z-1-001.zip"
DEFAULT_OUTPUT_DIR = r"C:\Users\harit\Documents\temp"
DEFAULT_JPEG_QUALITY = 90

# Watermark configuration
DEFAULT_LOGO_PATH = r"assets\photographer_logo_original.png"

# Processing configuration
DEFAULT_COLOR_ENHANCEMENT = 1.05  # Slight color saturation boost

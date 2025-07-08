"""
Configuration settings for photo post-processing.
Contains resolution settings, file paths, and processing parameters.
"""

# Resolution configurations
RESOLUTIONS = {
    # '2k': 2560 * 1440,  # Total pixels for 2K
    "4k": 3840 * 2160  # Total pixels for 4K
}

# File extension configurations
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".nef")
IMAGE_EXTENSIONS_CASE = (
    ".jpg",
    ".jpeg",
    ".png",
    ".JPG",
    ".JPEG",
    ".PNG",
    ".nef",
    ".NEF",
)

# Input/Output configuration
# DEFAULT_INPUT_PATH = r"C:\Users\harit\Downloads\Food-20250629T220226Z-1-001.zip"
# DEFAULT_INPUT_PATH = r"C:\Users\harit\Downloads\Wildlife & Landscapes-20250629T214837Z-1-001\Wildlife & Landscapes"

# WSL path (Linux format for Windows drives)
DEFAULT_INPUT_PATH = r"/mnt/c/Users/harit/Documents/temp/Input Photos"
DEFAULT_OUTPUT_DIR = r"/mnt/c/Users/harit/Documents/temp/output"
DEFAULT_JPEG_QUALITY = 90

# Watermark configuration
DEFAULT_LOGO_PATH = "/mnt/c/Users/harit/Documents/Visual Studio 2022/Demola/photo_post_processing/assets/photographer_logo_original.png"

# Watermark settings
WATERMARK_OPACITY = 0.9  # Watermark opacity (0.0 to 1.0)
# Watermark size relative to image width (0.1 to 0.3)
WATERMARK_SCALE = 0.15

# Processing configuration
# No color saturation boost - preserve natural tones
DEFAULT_COLOR_ENHANCEMENT = 1.00

# Advanced processing options
# Auto-adjust brightness for under/over exposed images - DISABLED for portraits
ENABLE_BRIGHTNESS_AUTO_ADJUST = False
# Auto-adjust contrast for low/high contrast images - DISABLED for portraits
ENABLE_CONTRAST_AUTO_ADJUST = False
# Apply gamma correction for better mid-tones - DISABLED for portraits
ENABLE_GAMMA_CORRECTION = False
ENABLE_WATERMARK = True  # Add watermark to processed images

# Portrait mode settings (for artistic/professional photos)
PORTRAIT_MODE = True  # Enable portrait-friendly processing
PRESERVE_SHADOWS = True  # Don't brighten dark areas automatically
PRESERVE_HIGHLIGHTS = True  # Don't darken bright areas automatically

# Alternative processing modes
MODES = {
    "portrait": {
        "color_enhancement": 1.00,  # No saturation boost
        "brightness_adjust": False,
        "contrast_adjust": False,
        "gamma_correction": False,
        "description": "Preserves artistic lighting and natural tones",
    },
    "natural": {
        "color_enhancement": 1.02,  # Very subtle enhancement
        "brightness_adjust": False,
        "contrast_adjust": False,
        "gamma_correction": False,
        "description": "Minimal processing with slight color boost",
    },
    "enhanced": {
        "color_enhancement": 1.05,  # Noticeable enhancement
        "brightness_adjust": True,
        "contrast_adjust": True,
        "gamma_correction": True,
        "description": "Full enhancement for challenging lighting",
    },
}

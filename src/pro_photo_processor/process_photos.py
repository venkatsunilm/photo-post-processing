"""
Main CLI and pipeline entry point for photo post-processing.
"""

import os
import sys
import logging
import argparse
import types
from typing import Any, Dict, Tuple
from .pipeline import ImageProcessingPipeline
from pro_photo_processor.config import config  # Adjust if config is in a submodule
from pro_photo_processor.io import file_operations
from pro_photo_processor.core import image_processing
from PIL import ExifTags, Image, ImageEnhance, ImageStat
from pro_photo_processor.utils import get_mode_prefix  # noqa: F401
from pro_photo_processor.config.config import DEFAULT_INPUT_PATH
from pro_photo_processor.io.file_operations import (
    cleanup_temp_directory,
    create_output_structure,
    create_zip_archive,
    extract_zip_if_needed,
    get_image_files_from_directory,
)
from pro_photo_processor.core.image_processing import add_watermark  # noqa: F401
from pro_photo_processor.raw.raw_processing_enhanced import (
    load_image_basic,
    load_image_smart_enhanced,
)  # noqa: F401

format_optimizer: types.ModuleType | None
try:
    from pro_photo_processor.presets import format_optimizer
except ImportError:
    format_optimizer = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("pro_photo_processor.process_photos")


def fix_image_orientation(img: Image.Image) -> Image.Image:
    """Fix image orientation based on EXIF data only if needed"""
    try:
        # Get EXIF data
        exif = img.getexif()
        if exif is not None:
            # Find orientation tag
            for tag, value in exif.items():
                if tag in ExifTags.TAGS and ExifTags.TAGS[tag] == "Orientation":
                    # Only apply rotation for specific EXIF values that actually need correction
                    # Value 1 = normal (no rotation needed)
                    # Value 3 = 180° rotation needed
                    # Value 6 = 270° rotation needed
                    # Value 8 = 90° rotation needed

                    # Only rotate if EXIF explicitly says the image is rotated
                    if value == 3:
                        img = img.rotate(180, expand=True)
                    elif value == 6:
                        img = img.rotate(270, expand=True)
                    elif value == 8:
                        img = img.rotate(90, expand=True)
                    # For value 1 (normal) or any other value, do nothing
                    break
    except (AttributeError, KeyError, TypeError):
        # If no EXIF data, leave image as-is
        pass

    return img


def resize_and_crop(img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    img_ratio = img.width / img.height
    target_ratio = target_size[0] / target_size[1]

    if img_ratio > target_ratio:
        # Wider → match height, crop width
        new_height = target_size[1]
        new_width = int(new_height * img_ratio)
    else:
        # Taller or equal → match width, crop height
        new_width = target_size[0]
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Center crop
    left = (img.width - target_size[0]) // 2
    top = (img.height - target_size[1]) // 2
    right = left + target_size[0]
    bottom = top + target_size[1]

    return img.crop((left, top, right, bottom))


def analyze_and_adjust_lighting(img: Image.Image) -> Image.Image:
    """Analyze image lighting and apply intelligent adjustments"""
    from pro_photo_processor.config.config import (
        DEFAULT_COLOR_ENHANCEMENT,
        ENABLE_BRIGHTNESS_AUTO_ADJUST,
        ENABLE_CONTRAST_AUTO_ADJUST,
        ENABLE_GAMMA_CORRECTION,
        PORTRAIT_MODE,
    )

    # In portrait mode, skip aggressive adjustments to preserve artistic intent
    if PORTRAIT_MODE:
        # Only apply very minimal color enhancement if any
        if DEFAULT_COLOR_ENHANCEMENT != 1.0:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(DEFAULT_COLOR_ENHANCEMENT)
        return img

    # Calculate image statistics
    stat = ImageStat.Stat(img)

    # Get mean brightness for each channel (R, G, B)
    mean_brightness = sum(stat.mean) / len(stat.mean)

    # Get standard deviation (contrast indicator)
    std_dev = sum(stat.stddev) / len(stat.stddev)

    # Analyze histogram to detect lighting issues
    histogram = img.histogram()

    # Check for underexposure (too many dark pixels)
    dark_pixels = sum(histogram[0:85])  # Very dark range
    total_pixels = img.width * img.height
    dark_ratio = dark_pixels / total_pixels

    # Check for overexposure (too many bright pixels)
    bright_pixels = sum(histogram[170:256])  # Very bright range
    bright_ratio = bright_pixels / total_pixels

    # Determine adjustments based on analysis
    brightness_factor = 1.0
    contrast_factor = 1.0
    gamma_factor = 1.0

    # Adjust for underexposure
    if mean_brightness < 100:  # Dark image
        brightness_factor = 1.15 + (100 - mean_brightness) / 200

    # Adjust for overexposure
    elif mean_brightness > 180:  # Bright image
        brightness_factor = 0.9 - (mean_brightness - 180) / 300

    # Adjust contrast based on standard deviation
    if std_dev < 40:  # Low contrast
        contrast_factor = 1.2 + (40 - std_dev) / 80
    elif std_dev > 80:  # High contrast
        contrast_factor = 0.95

    # Apply gamma correction for better mid-tone balance
    if dark_ratio > 0.3:  # Too many dark pixels
        gamma_factor = 0.8  # Brighten mid-tones
    elif bright_ratio > 0.2:  # Too many bright pixels
        gamma_factor = 1.2  # Darken mid-tones

    # Apply enhancements based on configuration
    enhanced_img = img

    # Brightness adjustment
    if ENABLE_BRIGHTNESS_AUTO_ADJUST and brightness_factor != 1.0:
        brightness_enhancer = ImageEnhance.Brightness(enhanced_img)
        enhanced_img = brightness_enhancer.enhance(brightness_factor)

    # Contrast adjustment
    if ENABLE_CONTRAST_AUTO_ADJUST and contrast_factor != 1.0:
        contrast_enhancer = ImageEnhance.Contrast(enhanced_img)
        enhanced_img = contrast_enhancer.enhance(contrast_factor)

    # Gamma correction (simulate with curve adjustment)
    if ENABLE_GAMMA_CORRECTION and gamma_factor != 1.0:
        # Create gamma lookup table
        gamma_table = [int(((i / 255.0) ** gamma_factor) * 255) for i in range(256)]
        enhanced_img = enhanced_img.point(gamma_table * 3)  # Apply to R, G, B

    # Final subtle color enhancement
    color_enhancer = ImageEnhance.Color(enhanced_img)
    enhanced_img = color_enhancer.enhance(DEFAULT_COLOR_ENHANCEMENT)

    return enhanced_img


def process_images(input_path: str, mode: str = "full") -> None:
    """
    Process images with different modes:
    - 'full': Complete processing (resize, enhance, watermark)
    - 'resize_watermark': Resize to target resolutions + watermark (no enhancements)
    - 'watermark': Only add watermark to existing images (original size)
    - 'resize_only': Resize to target resolutions only (no watermark, no enhancements)
    """
    from pro_photo_processor.config.config import (
        DEFAULT_OUTPUT_DIR,
        ENABLE_WATERMARK,
        RESOLUTIONS,
        WATERMARK_OPACITY,
        WATERMARK_SCALE,
    )

    logger.info(f"🎨 Starting processing in {mode} mode...")

    # Handle ZIP extraction if needed
    working_folder, is_temp = extract_zip_if_needed(input_path)
    if working_folder is None:
        logger.error("❌ Failed to process input. Please check the file/folder path.")
        return

    try:
        # Create organized output structure
        project_output_dir = create_output_structure(
            input_path, DEFAULT_OUTPUT_DIR, is_temp
        )

        # Get all image files from directory (including subdirectories)
        image_files = get_image_files_from_directory(working_folder)

        if not image_files:
            logger.error("❌ No image files found in the input!")
            return

        logger.info(f"📁 Found {len(image_files)} image files to process")

        for label, total_pixels in RESOLUTIONS.items():
            # Add mode suffix to directory name for proper separation
            mode_suffix = get_mode_prefix(mode)
            output_folder = os.path.join(
                project_output_dir, f"processed_photos_{label}_{mode_suffix}"
            )
            os.makedirs(output_folder, exist_ok=True)

            logger.info(f"\nProcessing {label.upper()} images...")

            for idx, (full_path, rel_path) in enumerate(image_files, 1):
                try:
                    # Use basic loading for watermark modes, enhanced for full mode
                    if (
                        mode == "watermark"
                        or mode == "resize_watermark"
                        or mode == "resize_only"
                    ):
                        img = load_image_basic(full_path)
                    else:
                        img = load_image_smart_enhanced(full_path)

                    # Apply EXIF rotation to get the visual orientation you see in file explorer
                    img = fix_image_orientation(img)

                    if mode == "full":
                        # Intelligent lighting analysis and adjustment
                        img = analyze_and_adjust_lighting(img)

                        # Calculate target size maintaining original aspect ratio
                        original_ratio = img.width / img.height

                        # Calculate dimensions to match target pixel count while preserving ratio
                        target_width = int((total_pixels * original_ratio) ** 0.5)
                        target_height = int(total_pixels / target_width)

                        target_size = (target_width, target_height)

                        # Resize to exact target size
                        final_img = img.resize(target_size, Image.Resampling.LANCZOS)
                    elif mode == "resize_watermark":
                        # Resize without any enhancements
                        original_ratio = img.width / img.height

                        # Calculate dimensions to match target pixel count while preserving ratio
                        target_width = int((total_pixels * original_ratio) ** 0.5)
                        target_height = int(total_pixels / target_width)

                        target_size = (target_width, target_height)

                        # Resize to exact target size
                        final_img = img.resize(target_size, Image.Resampling.LANCZOS)
                    elif mode == "resize_only":
                        # Resize only without any enhancements or watermark
                        original_ratio = img.width / img.height

                        # Calculate dimensions to match target pixel count while preserving ratio
                        target_width = int((total_pixels * original_ratio) ** 0.5)
                        target_height = int(total_pixels / target_width)

                        target_size = (target_width, target_height)

                        # Resize to exact target size
                        final_img = img.resize(target_size, Image.Resampling.LANCZOS)
                    else:
                        # Watermark-only mode: keep original size
                        final_img = img

                    # Add watermark to the processed image (skip for resize_only mode)
                    if ENABLE_WATERMARK and mode != "resize_only":
                        final_img = add_watermark(
                            final_img,
                            watermark_opacity=WATERMARK_OPACITY,
                            scale_factor=WATERMARK_SCALE,
                        )
                        logger.info(
                            f"   💧 Added watermark to {os.path.basename(full_path)}"
                        )
                    elif mode == "resize_only":
                        logger.info(
                            f"   📐 Resize only (no watermark) for {os.path.basename(full_path)}"
                        )
                    else:
                        logger.warning(
                            f"   ⚠️ Watermark disabled in config for {os.path.basename(full_path)}"
                        )

                    # Save with original filename prefix + mode prefix
                    original_name = os.path.splitext(os.path.basename(full_path))[0]
                    mode_prefix = get_mode_prefix(mode)
                    new_filename = f"{original_name}_{mode_prefix}.jpg"
                    output_path = os.path.join(output_folder, new_filename)
                    final_img.save(output_path, "JPEG", quality=90, optimize=True)
                except Exception as e:
                    logger.error(
                        f"❌ Failed to process {os.path.basename(full_path)}: {e}"
                    )

            # Create ZIP archive with mode suffix
            zip_path = create_zip_archive(
                output_folder, project_output_dir, f"{label}_{mode_suffix}"
            )
            logger.info(f"✅ Finished {label.upper()} folder zipped at:\n{zip_path}")

    finally:
        # Clean up temporary directory if needed
        if is_temp:
            cleanup_temp_directory(working_folder)


def process_images_with_photoshop_preset(input_path: str, preset_name: str) -> None:
    """Process images using Photoshop-style presets with automatic format optimization"""
    from pro_photo_processor.config.config import (
        DEFAULT_OUTPUT_DIR,
        ENABLE_WATERMARK,
        RESOLUTIONS,
        WATERMARK_OPACITY,
        WATERMARK_SCALE,
    )
    from pro_photo_processor.presets.format_optimizer import FormatOptimizer
    from pro_photo_processor.presets.photoshop_tools import apply_photoshop_preset

    logger.info(f"🎨 Starting processing with {preset_name} preset...")

    # Initialize format optimizer
    optimizer = FormatOptimizer()

    # Handle ZIP extraction if needed
    working_folder, is_temp = extract_zip_if_needed(input_path)
    if working_folder is None:
        logger.error("❌ Failed to process input. Please check the file/folder path.")
        return

    try:
        # Create organized output structure
        project_output_dir = create_output_structure(
            input_path, DEFAULT_OUTPUT_DIR, is_temp
        )

        # Get all image files from directory (including subdirectories)
        image_files = get_image_files_from_directory(working_folder)

        if not image_files:
            logger.error("❌ No image files found in the input!")
            return

        logger.info(f"📁 Found {len(image_files)} image files to process")

        # Analyze formats in the batch
        file_paths = [full_path for full_path, _ in image_files]
        format_counts = {"raw": 0, "jpeg": 0, "unknown": 0}
        for file_path in file_paths:
            format_type = optimizer.detect_file_format(file_path)
            format_counts[format_type] += 1

        if format_counts["raw"] > 0 or format_counts["jpeg"] > 0:
            logger.info(
                f"📊 Format analysis: {format_counts['raw']} RAW, {format_counts['jpeg']} JPEG, {format_counts['unknown']} other"
            )
            if format_counts["raw"] > 0 and format_counts["jpeg"] > 0:
                logger.info(
                    "🔄 Mixed formats detected - automatic optimization will choose:"
                )
                logger.info(
                    f"   📷 RAW files -> {optimizer.get_optimal_preset('dummy.nef', preset_name)}"
                )
                logger.info(
                    f"   🖼️  JPEG files -> {optimizer.get_optimal_preset('dummy.jpg', preset_name)}"
                )

        for label, total_pixels in RESOLUTIONS.items():
            output_folder = os.path.join(
                project_output_dir, f"processed_photos_{label}_{preset_name}"
            )
            os.makedirs(output_folder, exist_ok=True)

            logger.info(
                f"\nProcessing {label.upper()} images with {preset_name} preset..."
            )

            for idx, (full_path, rel_path) in enumerate(image_files, 1):
                try:
                    img = load_image_smart_enhanced(full_path)

                    # Apply EXIF rotation
                    img = fix_image_orientation(img)

                    # Get format-optimized preset
                    optimal_preset = optimizer.get_optimal_preset(
                        full_path, preset_name
                    )
                    format_info = optimizer.get_format_info(full_path)

                    # Show format optimization info if different preset was chosen
                    if optimal_preset != preset_name:
                        logger.info(
                            f"   🔄 {format_info['filename']} ({format_info['format'].upper()}) -> using {optimal_preset}"
                        )

                    # Apply Photoshop-style preset
                    enhanced_img, history = apply_photoshop_preset(img, optimal_preset)

                    # Show last 3 adjustments
                    logger.info(
                        f"   📝 {os.path.basename(full_path)}: {', '.join(history[-3:])}"
                    )

                    # Calculate target size maintaining original aspect ratio
                    original_ratio = enhanced_img.width / enhanced_img.height
                    target_width = int((total_pixels * original_ratio) ** 0.5)
                    target_height = int(total_pixels / target_width)
                    target_size = (target_width, target_height)

                    # Resize to exact target size
                    final_img = enhanced_img.resize(
                        target_size, Image.Resampling.LANCZOS
                    )

                    # Add watermark
                    if ENABLE_WATERMARK:
                        final_img = add_watermark(
                            final_img,
                            watermark_opacity=WATERMARK_OPACITY,
                            scale_factor=WATERMARK_SCALE,
                        )

                    # Save with original filename prefix + mode prefix
                    original_name = os.path.splitext(os.path.basename(full_path))[0]
                    mode_prefix = get_mode_prefix(preset_name)
                    new_filename = f"{original_name}_{mode_prefix}.jpg"
                    output_path = os.path.join(output_folder, new_filename)
                    final_img.save(output_path, "JPEG", quality=90, optimize=True)

                except Exception as e:
                    logger.error(
                        f"❌ Failed to process {os.path.basename(full_path)}: {e}"
                    )

            # Create ZIP archive
            zip_path = create_zip_archive(
                output_folder, project_output_dir, f"{label}_{preset_name}"
            )
            logger.info(f"✅ Finished {label.upper()} folder zipped at:\n{zip_path}")

    finally:
        # Clean up temporary directory if needed
        if is_temp:
            cleanup_temp_directory(working_folder)


def custom_adjustments_mode() -> None:
    """Interactive mode for custom Photoshop-style adjustments"""
    logger.info("\n🛠️ CUSTOM PHOTOSHOP-STYLE ADJUSTMENTS")
    logger.info("=" * 50)
    logger.info("Available adjustments:")
    logger.info("• Exposure (-2.0 to +2.0) - Professional camera-style")
    logger.info("• Brightness (-100 to +100) - Simple percentage adjustment")
    logger.info("• Highlights (-100 to 0)")
    logger.info("• Shadows (0 to +100)")
    logger.info("• Vibrance (-100 to +100)")
    logger.info("• Saturation (-100 to +100)")
    logger.info("• Clarity (-100 to +100)")
    logger.info("• Structure (-100 to +100)")
    logger.info("• Temperature (-100 to +100)")
    logger.info("• Skin Smoothing (0 to 100)")
    logger.info("=" * 50)
    logger.info("💡 Note: Use either Exposure OR Brightness, not both")
    logger.info("   • Exposure: Professional (0.5 = one camera stop brighter)")
    logger.info("   • Brightness: User-friendly (50 = 50% brighter)")
    logger.info("=" * 50)

    try:
        exposure = float(input("Exposure (-2.0 to +2.0, 0=no change): ") or "0")
        brightness = int(input("Brightness (-100 to +100, 0=no change): ") or "0")
        highlights = int(input("Highlights (-100 to 0, 0=no change): ") or "0")
        shadows = int(input("Shadows (0 to +100, 0=no change): ") or "0")
        vibrance = int(input("Vibrance (-100 to +100, 0=no change): ") or "0")
        saturation = int(input("Saturation (-100 to +100, 0=no change): ") or "0")
        clarity = int(input("Clarity (-100 to +100, 0=no change): ") or "0")
        structure = int(input("Structure (-100 to +100, 0=no change): ") or "0")
        temperature = int(input("Temperature (-100 to +100, 0=no change): ") or "0")
        skin_smoothing = int(input("Skin Smoothing (0 to 100, 0=no change): ") or "0")

        # Create custom preset
        custom_preset = {
            "exposure": exposure,
            "brightness": brightness,
            "highlights": highlights,
            "shadows": shadows,
            "vibrance": vibrance,
            "saturation": saturation,
            "clarity": clarity,
            "structure": structure,
            "temperature": temperature,
            "skin_smoothing": skin_smoothing,
        }

        logger.info("\n🎨 Applying custom adjustments...")
        process_images_with_custom_preset(DEFAULT_INPUT_PATH, custom_preset)

    except ValueError:
        logger.error("❌ Invalid input. Please enter numbers only.")
        custom_adjustments_mode()


def process_images_with_custom_preset(
    input_path: str, custom_preset: Dict[str, float]
) -> None:
    """Process images with custom user-defined adjustments"""
    from pro_photo_processor.config.config import (
        DEFAULT_OUTPUT_DIR,
        ENABLE_WATERMARK,
        RESOLUTIONS,
        WATERMARK_OPACITY,
        WATERMARK_SCALE,
    )
    from pro_photo_processor.presets.photoshop_tools import PhotoshopStyleEnhancer

    logger.info("🎨 Starting processing with custom settings...")

    # Handle ZIP extraction if needed
    working_folder, is_temp = extract_zip_if_needed(input_path)
    if working_folder is None:
        logger.error("❌ Failed to process input. Please check the file/folder path.")
        return

    try:
        # Create organized output structure
        project_output_dir = create_output_structure(
            input_path, DEFAULT_OUTPUT_DIR, is_temp
        )

        # Get all image files from directory (including subdirectories)
        image_files = get_image_files_from_directory(working_folder)

        if not image_files:
            logger.error("❌ No image files found in the input!")
            return

        logger.info(f"📁 Found {len(image_files)} image files to process")

        for label, total_pixels in RESOLUTIONS.items():
            output_folder = os.path.join(
                project_output_dir, f"processed_photos_{label}_custom"
            )
            os.makedirs(output_folder, exist_ok=True)

            logger.info(f"\nProcessing {label.upper()} images with custom settings...")

            for idx, (full_path, rel_path) in enumerate(image_files, 1):
                try:
                    img = load_image_smart_enhanced(full_path)
                    img = fix_image_orientation(img)

                    # Apply custom adjustments
                    enhancer = PhotoshopStyleEnhancer(img)

                    # Apply either exposure or brightness (exposure takes priority)
                    if custom_preset.get("exposure", 0) != 0:
                        enhancer.exposure_adjustment(custom_preset.get("exposure", 0))
                    elif custom_preset.get("brightness", 0) != 0:
                        enhancer.brightness_adjustment(
                            custom_preset.get("brightness", 0)
                        )

                    enhancer.highlights_shadows(
                        highlights=custom_preset.get("highlights", 0),
                        shadows=custom_preset.get("shadows", 0),
                    )
                    enhancer.vibrance_saturation(
                        vibrance=custom_preset.get("vibrance", 0),
                        saturation=custom_preset.get("saturation", 0),
                    )
                    enhancer.clarity_structure(
                        clarity=custom_preset.get("clarity", 0),
                        structure=custom_preset.get("structure", 0),
                    )
                    enhancer.color_temperature(
                        temperature=custom_preset.get("temperature", 0)
                    )
                    enhancer.portrait_enhancements(
                        skin_smoothing=custom_preset.get("skin_smoothing", 0)
                    )

                    enhanced_img = enhancer.get_result()

                    # Resize
                    original_ratio = enhanced_img.width / enhanced_img.height
                    target_width = int((total_pixels * original_ratio) ** 0.5)
                    target_height = int(total_pixels / target_width)
                    target_size = (target_width, target_height)
                    final_img = enhanced_img.resize(
                        target_size, Image.Resampling.LANCZOS
                    )

                    # Add watermark
                    if ENABLE_WATERMARK:
                        final_img = add_watermark(
                            final_img,
                            watermark_opacity=WATERMARK_OPACITY,
                            scale_factor=WATERMARK_SCALE,
                        )

                    # Save with original filename prefix + mode prefix
                    original_name = os.path.splitext(os.path.basename(full_path))[0]
                    mode_prefix = get_mode_prefix("custom")
                    new_filename = f"{original_name}_{mode_prefix}.jpg"
                    output_path = os.path.join(output_folder, new_filename)
                    final_img.save(output_path, "JPEG", quality=90, optimize=True)

                except Exception as e:
                    logger.error(
                        f"❌ Failed to process {os.path.basename(full_path)}: {e}"
                    )

            # Create ZIP archive
            zip_path = create_zip_archive(
                output_folder, project_output_dir, f"{label}_custom"
            )
            logger.info(
                f"✅ Finished {label.upper()} custom folder zipped at:\n{zip_path}"
            )

    finally:
        # Clean up temporary directory if needed
        if is_temp:
            cleanup_temp_directory(working_folder)


def apply_processing_mode(mode_name: str) -> None:
    """Apply a specific processing mode configuration"""
    from typing import cast

    import pro_photo_processor.config.config as config
    from pro_photo_processor.config.config import MODES

    if mode_name in MODES:
        mode_settings: Dict[str, Any] = MODES[mode_name]
        # Use cast to tell mypy what type these values should be
        config.DEFAULT_COLOR_ENHANCEMENT = cast(
            float, mode_settings["color_enhancement"]
        )
        config.ENABLE_BRIGHTNESS_AUTO_ADJUST = cast(
            bool, mode_settings["brightness_adjust"]
        )
        config.ENABLE_CONTRAST_AUTO_ADJUST = cast(
            bool, mode_settings["contrast_adjust"]
        )
        config.ENABLE_GAMMA_CORRECTION = cast(bool, mode_settings["gamma_correction"])
        config.PORTRAIT_MODE = mode_name == "portrait"

        logger.info(f"📋 Mode: {mode_settings['description']}")
    else:
        logger.warning(f"⚠️ Unknown mode: {mode_name}")


def cli_main() -> None:
    parser = argparse.ArgumentParser(description="Photo Post-Processing Pipeline CLI")
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List all available enhancement presets and exit.",
    )
    parser.add_argument(
        "--list-presets-format",
        type=str,
        choices=["plain", "table", "json"],
        default="plain",
        help="Format for listing presets: plain, table, or json (default: plain)",
    )
    parser.add_argument(
        "--list-modes",
        action="store_true",
        help="List all available utility processing modes and exit.",
    )
    parser.add_argument(
        "--input",
        dest="input_path",
        type=str,
        default=None,
        help="Path to input image or folder (or ZIP). Default: ./input",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        type=str,
        default=None,
        help="Path to output directory. Default: ./output",
    )
    parser.add_argument(
        "--type",
        type=str,
        required=False,
        help="Processing type: either a preset name (e.g. portrait_subtle, sports_action) for enhancement, or a utility mode (resize_only, resize_watermark, watermark). Only one is allowed. If not provided, an interactive menu will be shown.",
    )
    parser.add_argument(
        "--custom",
        type=str,
        default=None,
        help="Custom preset as JSON string (optional)",
    )

    args = parser.parse_args()

    # Preset and mode lists
    presets = [
        "portrait_subtle",
        "portrait_natural",
        "portrait_dramatic",
        "studio_portrait",
        "overexposed_recovery",
        "natural_wildlife",
        "sports_action",
        "enhanced_mode",
    ]
    utility_modes = ["resize_only", "resize_watermark", "watermark"]

    # List presets or modes and exit
    if args.list_presets:
        preset_descriptions = {
            "portrait_subtle": "Subtle portrait enhancement",
            "portrait_natural": "Natural look for portraits",
            "portrait_dramatic": "Dramatic lighting for portraits",
            "studio_portrait": "Studio-style portrait finish",
            "overexposed_recovery": "Recover details from overexposed images",
            "natural_wildlife": "Enhance wildlife/nature shots",
            "sports_action": "Sharpen and brighten action shots",
            "enhanced_mode": "General enhancement for all photos",
        }
        if args.list_presets_format == "json":
            import json

            logger.info(
                json.dumps(
                    [
                        {"name": k, "description": v}
                        for k, v in preset_descriptions.items()
                    ],
                    indent=2,
                )
            )
        elif args.list_presets_format == "table":
            try:
                from tabulate import tabulate

                table = [(k, v) for k, v in preset_descriptions.items()]
                logger.info("\n" + tabulate(table, headers=["Preset", "Description"]))
            except ImportError:
                # Fallback to simple table
                logger.info("\nPreset               | Description")
                logger.info(
                    "---------------------|------------------------------------------"
                )
                for k, v in preset_descriptions.items():
                    logger.info(f"{k:<20} | {v}")
        else:
            logger.info("Available enhancement presets:")
            for k, v in preset_descriptions.items():
                logger.info(f"  - {k}: {v}")
        sys.exit(0)
    if args.list_modes:
        logger.info("Available utility processing modes:")
        for m in utility_modes:
            logger.info(f"  - {m}")
        sys.exit(0)

    # Use config defaults if not provided
    input_path = args.input_path or getattr(
        config,
        "DEFAULT_INPUT_PATH",
        os.path.abspath(os.path.join(os.getcwd(), "input")),
    )
    output_path = args.output_path or getattr(
        config,
        "DEFAULT_OUTPUT_DIR",
        os.path.abspath(os.path.join(os.getcwd(), "output")),
    )

    logger.info(f"📥 Input path: {input_path}")
    logger.info(f"📤 Output path: {output_path}")

    # Dependency injection
    preset_manager = format_optimizer if format_optimizer is not None else None

    # Patch config to use output_path if provided
    config.DEFAULT_OUTPUT_DIR = output_path

    pipeline = ImageProcessingPipeline(
        config=config,
        file_ops=file_operations,
        image_processor=image_processing,
        preset_manager=preset_manager,
    )

    selected_type = args.type
    if not selected_type:
        logger.info("\nSelect a processing type:")
        options = presets + utility_modes
        # Prepare descriptions for presets and utility modes
        preset_descriptions = {
            "portrait_subtle": "Subtle portrait enhancement",
            "portrait_natural": "Natural look for portraits",
            "portrait_dramatic": "Dramatic lighting for portraits",
            "studio_portrait": "Studio-style portrait finish",
            "overexposed_recovery": "Recover details from overexposed images",
            "natural_wildlife": "Enhance wildlife/nature shots",
            "sports_action": "Sharpen and brighten action shots",
            "enhanced_mode": "General enhancement for all photos",
        }
        utility_descriptions = {
            "resize_only": "Resize to target resolutions only",
            "resize_watermark": "Resize and add watermark",
            "watermark": "Add watermark only",
        }
        # Build table rows for the interactive menu
        menu_table = []
        for idx, name in enumerate(options, 1):
            if name in preset_descriptions:
                desc = preset_descriptions[name]
                kind = "Preset"
            else:
                desc = utility_descriptions.get(name, "Utility mode")
                kind = "Utility"
            menu_table.append((idx, name, kind, desc))
        # Print table
        try:
            from tabulate import tabulate

            logger.info(
                "\n"
                + tabulate(menu_table, headers=["No.", "Name", "Type", "Description"])
            )
        except ImportError:
            logger.info(f"{'No.':<4} {'Name':<20} {'Type':<10} Description")
            logger.info(f"{'-' * 4} {'-' * 20} {'-' * 10} {'-' * 40}")
            for row in menu_table:
                logger.info(f"{row[0]:<4} {row[1]:<20} {row[2]:<10} {row[3]}")
        # Prompt for input
        while True:
            try:
                choice = int(input("Enter a number: ").strip())
                if 1 <= choice <= len(options):
                    selected_type = options[choice - 1]
                    break
                else:
                    logger.warning(
                        f"Please enter a number between 1 and {len(options)}."
                    )
            except ValueError:
                logger.warning("Invalid input. Please enter a number.")

    if args.custom:
        import json

        try:
            custom_preset = json.loads(args.custom)
            if not isinstance(custom_preset, dict):
                raise ValueError("Custom preset must be a JSON object.")
        except Exception as e:
            logger.error(f"❌ Invalid custom preset JSON: {e}")
            sys.exit(1)
        pipeline.process_with_custom_preset(input_path, custom_preset)
    elif selected_type in utility_modes:
        pipeline.process_images(input_path, mode=selected_type)
    else:
        pipeline.process_with_preset(input_path, selected_type)


if __name__ == "__main__":
    cli_main()

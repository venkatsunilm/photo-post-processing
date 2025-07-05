from utils.config import DEFAULT_INPUT_PATH
import os
from PIL import Image, ImageEnhance, ExifTags, ImageStat
import zipfile
import numpy as np
from utils.image_processing import add_watermark
from utils.file_operations import extract_zip_if_needed, cleanup_temp_directory, get_image_files_from_directory, create_output_structure, create_zip_archive
from utils.raw_processing_enhanced import load_image_smart_enhanced, load_image_basic, is_raw_file


def fix_image_orientation(img):
    """Fix image orientation based on EXIF data only if needed"""
    try:
        # Get EXIF data
        exif = img._getexif()
        if exif is not None:
            # Find orientation tag
            for tag, value in exif.items():
                if tag in ExifTags.TAGS and ExifTags.TAGS[tag] == 'Orientation':
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


def resize_and_crop(img, target_size):
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


def analyze_and_adjust_lighting(img):
    """Analyze image lighting and apply intelligent adjustments"""
    from utils.config import (ENABLE_BRIGHTNESS_AUTO_ADJUST, ENABLE_CONTRAST_AUTO_ADJUST,
                              ENABLE_GAMMA_CORRECTION, DEFAULT_COLOR_ENHANCEMENT, PORTRAIT_MODE)

    # In portrait mode, skip aggressive adjustments to preserve artistic intent
    if PORTRAIT_MODE:
        # Only apply very minimal color enhancement if any
        if DEFAULT_COLOR_ENHANCEMENT != 1.0:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(DEFAULT_COLOR_ENHANCEMENT)
        return img

    # Convert to numpy array for analysis
    img_array = np.array(img)

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
        enhancer = ImageEnhance.Brightness(enhanced_img)
        enhanced_img = enhancer.enhance(brightness_factor)

    # Contrast adjustment
    if ENABLE_CONTRAST_AUTO_ADJUST and contrast_factor != 1.0:
        enhancer = ImageEnhance.Contrast(enhanced_img)
        enhanced_img = enhancer.enhance(contrast_factor)

    # Gamma correction (simulate with curve adjustment)
    if ENABLE_GAMMA_CORRECTION and gamma_factor != 1.0:
        # Create gamma lookup table
        gamma_table = [int(((i / 255.0) ** gamma_factor) * 255)
                       for i in range(256)]
        enhanced_img = enhanced_img.point(gamma_table * 3)  # Apply to R, G, B

    # Final subtle color enhancement
    enhancer = ImageEnhance.Color(enhanced_img)
    enhanced_img = enhancer.enhance(DEFAULT_COLOR_ENHANCEMENT)

    return enhanced_img


def process_images(input_path, mode='full'):
    """
    Process images with different modes:
    - 'full': Complete processing (resize, enhance, watermark)
    - 'resize_watermark': Resize to target resolutions + watermark (no enhancements)
    - 'watermark': Only add watermark to existing images (original size)
    - 'resize_only': Resize to target resolutions only (no watermark, no enhancements)
    """
    from utils.config import RESOLUTIONS, DEFAULT_OUTPUT_DIR, ENABLE_WATERMARK, WATERMARK_OPACITY, WATERMARK_SCALE

    print(f"🎨 Starting processing in {mode} mode...")

    # Handle ZIP extraction if needed
    working_folder, is_temp = extract_zip_if_needed(input_path)
    if working_folder is None:
        print("❌ Failed to process input. Please check the file/folder path.")
        return

    try:
        # Create organized output structure
        project_output_dir = create_output_structure(
            input_path, DEFAULT_OUTPUT_DIR, is_temp)

        # Get all image files from directory (including subdirectories)
        image_files = get_image_files_from_directory(working_folder)

        if not image_files:
            print("❌ No image files found in the input!")
            return

        print(f"📁 Found {len(image_files)} image files to process")

        for label, total_pixels in RESOLUTIONS.items():
            # Add mode suffix to directory name for proper separation
            mode_suffix = get_mode_prefix(mode)
            output_folder = os.path.join(
                project_output_dir, f'processed_photos_{label}_{mode_suffix}')
            os.makedirs(output_folder, exist_ok=True)

            print(f"\nProcessing {label.upper()} images...")

            for idx, (full_path, rel_path) in enumerate(image_files, 1):
                try:
                    # Use basic loading for watermark modes, enhanced for full mode
                    if mode == 'watermark' or mode == 'resize_watermark' or mode == 'resize_only':
                        img = load_image_basic(full_path)
                    else:
                        img = load_image_smart_enhanced(full_path)

                    # Apply EXIF rotation to get the visual orientation you see in file explorer
                    img = fix_image_orientation(img)

                    if mode == 'full':
                        # Intelligent lighting analysis and adjustment
                        img = analyze_and_adjust_lighting(img)

                        # Calculate target size maintaining original aspect ratio
                        original_ratio = img.width / img.height

                        # Calculate dimensions to match target pixel count while preserving ratio
                        target_width = int(
                            (total_pixels * original_ratio) ** 0.5)
                        target_height = int(total_pixels / target_width)

                        target_size = (target_width, target_height)

                        # Resize to exact target size
                        final_img = img.resize(
                            target_size, Image.Resampling.LANCZOS)
                    elif mode == 'resize_watermark':
                        # Resize without any enhancements
                        original_ratio = img.width / img.height

                        # Calculate dimensions to match target pixel count while preserving ratio
                        target_width = int(
                            (total_pixels * original_ratio) ** 0.5)
                        target_height = int(total_pixels / target_width)

                        target_size = (target_width, target_height)

                        # Resize to exact target size
                        final_img = img.resize(
                            target_size, Image.Resampling.LANCZOS)
                    elif mode == 'resize_only':
                        # Resize only without any enhancements or watermark
                        original_ratio = img.width / img.height

                        # Calculate dimensions to match target pixel count while preserving ratio
                        target_width = int(
                            (total_pixels * original_ratio) ** 0.5)
                        target_height = int(total_pixels / target_width)

                        target_size = (target_width, target_height)

                        # Resize to exact target size
                        final_img = img.resize(
                            target_size, Image.Resampling.LANCZOS)
                    else:
                        # Watermark-only mode: keep original size
                        final_img = img

                    # Add watermark to the processed image (skip for resize_only mode)
                    if ENABLE_WATERMARK and mode != 'resize_only':
                        final_img = add_watermark(
                            final_img, watermark_opacity=WATERMARK_OPACITY, scale_factor=WATERMARK_SCALE)
                        print(
                            f"   💧 Added watermark to {os.path.basename(full_path)}")
                    elif mode == 'resize_only':
                        print(
                            f"   📐 Resize only (no watermark) for {os.path.basename(full_path)}")
                    else:
                        print(
                            f"   ⚠️ Watermark disabled in config for {os.path.basename(full_path)}")

                    # Save with original filename prefix + mode prefix
                    original_name = os.path.splitext(
                        os.path.basename(full_path))[0]
                    mode_prefix = get_mode_prefix(mode)
                    new_filename = f'{original_name}_{mode_prefix}.jpg'
                    output_path = os.path.join(output_folder, new_filename)
                    final_img.save(output_path, 'JPEG',
                                   quality=90, optimize=True)
                except Exception as e:
                    print(
                        f"❌ Failed to process {os.path.basename(full_path)}: {e}")

            # Create ZIP archive with mode suffix
            zip_path = create_zip_archive(
                output_folder, project_output_dir, f'{label}_{mode_suffix}')
            print(f"✅ Finished {label.upper()} folder zipped at:\n{zip_path}")

    finally:
        # Clean up temporary directory if needed
        if is_temp:
            cleanup_temp_directory(working_folder)


def main():
    """Main function with menu system"""
    print("🎨 Photo Post-Processing Pipeline")
    print("=" * 70)
    print("📸 Processing Modes:")
    print("1. Portrait Subtle    → Very gentle enhancement (closest to original)")
    print("2. Portrait Natural   → Natural portrait enhancement (recommended)")
    print("3. Portrait Dramatic  → Enhanced contrast (toned down for natural look)")
    print("4. Studio Portrait    → Clean, professional studio look")
    print("5. Bright Photo Balance → Gentle fix for bright/washed out photos")
    print("6. Natural Wildlife   → Perfect for animal/nature photos")
    print("7. Sports Action      → Optimized for sports photography (auto-detect RAW/JPEG)")
    print("8. Enhanced Mode      → Full enhancement for challenging lighting")
    print("9. Resize & Watermark → Resize to target resolutions + watermark (no enhancements)")
    print("10. Watermark Only    → Add watermark to existing photos (original size)")
    print("11. Custom Adjustments → Manual Photoshop-style controls")
    print("12. Resize Only       → Resize to target resolutions (no watermark, no enhancements)")
    print("13. Exit")
    print("=" * 70)
    print("💡 Smart Tips:")
    print("   🤖 Options 1-7: Auto-detect RAW vs JPEG for optimal results")
    print("   📸 RAW files get enhanced processing automatically")
    print("   🏃‍♂️ Sports Action intelligently chooses best preset per file")
    print("   📏 Option 9: Perfect for preparing images for web/print (no color changes)")
    print("   📐 Option 12: Clean resize for format conversion (NEF→JPG, PNG→JPG, etc.)")
    print("=" * 70)

    choice = input("Choose an option (1-13): ").strip()

    if choice == '1':
        print("\n🎭 Starting Portrait Subtle Mode...")
        process_images_with_photoshop_preset(
            DEFAULT_INPUT_PATH, 'portrait_subtle')
    elif choice == '2':
        print("\n🎭 Starting Portrait Natural Mode...")
        process_images_with_photoshop_preset(
            DEFAULT_INPUT_PATH, 'portrait_natural')
    elif choice == '3':
        print("\n🎭 Starting Portrait Dramatic Mode...")
        process_images_with_photoshop_preset(
            DEFAULT_INPUT_PATH, 'portrait_dramatic')
    elif choice == '4':
        print("\n📸 Starting Studio Portrait Mode...")
        process_images_with_photoshop_preset(
            DEFAULT_INPUT_PATH, 'studio_portrait')
    elif choice == '5':
        print("\n🌞 Starting Bright Photo Balance Mode...")
        process_images_with_photoshop_preset(
            DEFAULT_INPUT_PATH, 'overexposed_recovery')
    elif choice == '6':
        print("\n🦌 Starting Natural Wildlife Mode...")
        process_images_with_photoshop_preset(
            DEFAULT_INPUT_PATH, 'natural_wildlife')
    elif choice == '7':
        print("\n🏃‍♂️ Starting Sports Action Mode...")
        process_images_with_photoshop_preset(
            DEFAULT_INPUT_PATH, 'sports_action')
    elif choice == '8':
        print("\n✨ Starting Enhanced Mode (full processing)...")
        apply_processing_mode('enhanced')
        process_images(DEFAULT_INPUT_PATH, mode='full')
    elif choice == '9':
        print("\n📏 Starting Resize & Watermark Mode...")
        process_images(DEFAULT_INPUT_PATH, mode='resize_watermark')
    elif choice == '10':
        print("\n💧 Adding watermarks only...")
        process_images(DEFAULT_INPUT_PATH, mode='watermark')
    elif choice == '11':
        print("\n🛠️ Custom Adjustments Mode...")
        custom_adjustments_mode()
    elif choice == '12':
        print("\n📐 Starting Resize Only Mode...")
        process_images(DEFAULT_INPUT_PATH, mode='resize_only')
    elif choice == '13':
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice. Please try again.")
        main()


def process_images_with_photoshop_preset(input_path, preset_name):
    """Process images using Photoshop-style presets with automatic format optimization"""
    from utils.photoshop_tools import apply_photoshop_preset
    from utils.format_optimizer import FormatOptimizer
    from utils.config import RESOLUTIONS, DEFAULT_OUTPUT_DIR, ENABLE_WATERMARK, WATERMARK_OPACITY, WATERMARK_SCALE

    print(f"🎨 Starting processing with {preset_name} preset...")

    # Initialize format optimizer
    optimizer = FormatOptimizer()

    # Handle ZIP extraction if needed
    working_folder, is_temp = extract_zip_if_needed(input_path)
    if working_folder is None:
        print("❌ Failed to process input. Please check the file/folder path.")
        return

    try:
        # Create organized output structure
        project_output_dir = create_output_structure(
            input_path, DEFAULT_OUTPUT_DIR, is_temp)

        # Get all image files from directory (including subdirectories)
        image_files = get_image_files_from_directory(working_folder)

        if not image_files:
            print("❌ No image files found in the input!")
            return

        print(f"📁 Found {len(image_files)} image files to process")

        # Analyze formats in the batch
        file_paths = [full_path for full_path, _ in image_files]
        format_counts = {'raw': 0, 'jpeg': 0, 'unknown': 0}
        for file_path in file_paths:
            format_type = optimizer.detect_file_format(file_path)
            format_counts[format_type] += 1

        if format_counts['raw'] > 0 or format_counts['jpeg'] > 0:
            print(
                f"📊 Format analysis: {format_counts['raw']} RAW, {format_counts['jpeg']} JPEG, {format_counts['unknown']} other")
            if format_counts['raw'] > 0 and format_counts['jpeg'] > 0:
                print(f"🔄 Mixed formats detected - automatic optimization will choose:")
                print(
                    f"   📷 RAW files -> {optimizer.get_optimal_preset('dummy.nef', preset_name)}")
                print(
                    f"   🖼️  JPEG files -> {optimizer.get_optimal_preset('dummy.jpg', preset_name)}")

        for label, total_pixels in RESOLUTIONS.items():
            output_folder = os.path.join(
                project_output_dir, f'processed_photos_{label}_{preset_name}')
            os.makedirs(output_folder, exist_ok=True)

            print(
                f"\nProcessing {label.upper()} images with {preset_name} preset...")

            for idx, (full_path, rel_path) in enumerate(image_files, 1):
                try:
                    img = load_image_smart_enhanced(full_path)

                    # Apply EXIF rotation
                    img = fix_image_orientation(img)

                    # Get format-optimized preset
                    optimal_preset = optimizer.get_optimal_preset(
                        full_path, preset_name)
                    format_info = optimizer.get_format_info(full_path)

                    # Show format optimization info if different preset was chosen
                    if optimal_preset != preset_name:
                        print(
                            f"   🔄 {format_info['filename']} ({format_info['format'].upper()}) -> using {optimal_preset}")

                    # Apply Photoshop-style preset
                    enhanced_img, history = apply_photoshop_preset(
                        img, optimal_preset)

                    # Show last 3 adjustments
                    print(
                        f"   📝 {os.path.basename(full_path)}: {', '.join(history[-3:])}")

                    # Calculate target size maintaining original aspect ratio
                    original_ratio = enhanced_img.width / enhanced_img.height
                    target_width = int((total_pixels * original_ratio) ** 0.5)
                    target_height = int(total_pixels / target_width)
                    target_size = (target_width, target_height)

                    # Resize to exact target size
                    final_img = enhanced_img.resize(
                        target_size, Image.Resampling.LANCZOS)

                    # Add watermark
                    if ENABLE_WATERMARK:
                        final_img = add_watermark(
                            final_img, watermark_opacity=WATERMARK_OPACITY, scale_factor=WATERMARK_SCALE)

                    # Save with original filename prefix + mode prefix
                    original_name = os.path.splitext(
                        os.path.basename(full_path))[0]
                    mode_prefix = get_mode_prefix(preset_name)
                    new_filename = f'{original_name}_{mode_prefix}.jpg'
                    output_path = os.path.join(output_folder, new_filename)
                    final_img.save(output_path, 'JPEG',
                                   quality=90, optimize=True)

                except Exception as e:
                    print(
                        f"❌ Failed to process {os.path.basename(full_path)}: {e}")

            # Create ZIP archive
            zip_path = create_zip_archive(
                output_folder, project_output_dir, f'{label}_{preset_name}')
            print(f"✅ Finished {label.upper()} folder zipped at:\n{zip_path}")

    finally:
        # Clean up temporary directory if needed
        if is_temp:
            cleanup_temp_directory(working_folder)


def custom_adjustments_mode():
    """Interactive mode for custom Photoshop-style adjustments"""
    print("\n🛠️ CUSTOM PHOTOSHOP-STYLE ADJUSTMENTS")
    print("=" * 50)
    print("Available adjustments:")
    print("• Exposure (-2.0 to +2.0) - Professional camera-style")
    print("• Brightness (-100 to +100) - Simple percentage adjustment")
    print("• Highlights (-100 to 0)")
    print("• Shadows (0 to +100)")
    print("• Vibrance (-100 to +100)")
    print("• Saturation (-100 to +100)")
    print("• Clarity (-100 to +100)")
    print("• Structure (-100 to +100)")
    print("• Temperature (-100 to +100)")
    print("• Skin Smoothing (0 to 100)")
    print("=" * 50)
    print("💡 Note: Use either Exposure OR Brightness, not both")
    print("   • Exposure: Professional (0.5 = one camera stop brighter)")
    print("   • Brightness: User-friendly (50 = 50% brighter)")
    print("=" * 50)

    try:
        exposure = float(
            input("Exposure (-2.0 to +2.0, 0=no change): ") or "0")
        brightness = int(
            input("Brightness (-100 to +100, 0=no change): ") or "0")
        highlights = int(input("Highlights (-100 to 0, 0=no change): ") or "0")
        shadows = int(input("Shadows (0 to +100, 0=no change): ") or "0")
        vibrance = int(input("Vibrance (-100 to +100, 0=no change): ") or "0")
        saturation = int(
            input("Saturation (-100 to +100, 0=no change): ") or "0")
        clarity = int(input("Clarity (-100 to +100, 0=no change): ") or "0")
        structure = int(
            input("Structure (-100 to +100, 0=no change): ") or "0")
        temperature = int(
            input("Temperature (-100 to +100, 0=no change): ") or "0")
        skin_smoothing = int(
            input("Skin Smoothing (0 to 100, 0=no change): ") or "0")

        # Create custom preset
        custom_preset = {
            'exposure': exposure,
            'brightness': brightness,
            'highlights': highlights,
            'shadows': shadows,
            'vibrance': vibrance,
            'saturation': saturation,
            'clarity': clarity,
            'structure': structure,
            'temperature': temperature,
            'skin_smoothing': skin_smoothing
        }

        print(f"\n🎨 Applying custom adjustments...")
        process_images_with_custom_preset(DEFAULT_INPUT_PATH, custom_preset)

    except ValueError:
        print("❌ Invalid input. Please enter numbers only.")
        custom_adjustments_mode()


def process_images_with_custom_preset(input_path, custom_preset):
    """Process images with custom user-defined adjustments"""
    from utils.photoshop_tools import PhotoshopStyleEnhancer
    from utils.config import RESOLUTIONS, DEFAULT_OUTPUT_DIR, ENABLE_WATERMARK, WATERMARK_OPACITY, WATERMARK_SCALE

    print("🎨 Starting processing with custom settings...")

    # Handle ZIP extraction if needed
    working_folder, is_temp = extract_zip_if_needed(input_path)
    if working_folder is None:
        print("❌ Failed to process input. Please check the file/folder path.")
        return

    try:
        # Create organized output structure
        project_output_dir = create_output_structure(
            input_path, DEFAULT_OUTPUT_DIR, is_temp)

        # Get all image files from directory (including subdirectories)
        image_files = get_image_files_from_directory(working_folder)

        if not image_files:
            print("❌ No image files found in the input!")
            return

        print(f"📁 Found {len(image_files)} image files to process")

        for label, total_pixels in RESOLUTIONS.items():
            output_folder = os.path.join(
                project_output_dir, f'processed_photos_{label}_custom')
            os.makedirs(output_folder, exist_ok=True)

            print(
                f"\nProcessing {label.upper()} images with custom settings...")

            for idx, (full_path, rel_path) in enumerate(image_files, 1):
                try:
                    img = load_image_smart_enhanced(full_path)
                    img = fix_image_orientation(img)

                    # Apply custom adjustments
                    enhancer = PhotoshopStyleEnhancer(img)

                    # Apply either exposure or brightness (exposure takes priority)
                    if custom_preset.get('exposure', 0) != 0:
                        enhancer.exposure_adjustment(
                            custom_preset.get('exposure', 0))
                    elif custom_preset.get('brightness', 0) != 0:
                        enhancer.brightness_adjustment(
                            custom_preset.get('brightness', 0))

                    enhancer.highlights_shadows(
                        highlights=custom_preset.get('highlights', 0),
                        shadows=custom_preset.get('shadows', 0)
                    )
                    enhancer.vibrance_saturation(
                        vibrance=custom_preset.get('vibrance', 0),
                        saturation=custom_preset.get('saturation', 0)
                    )
                    enhancer.clarity_structure(
                        clarity=custom_preset.get('clarity', 0),
                        structure=custom_preset.get('structure', 0)
                    )
                    enhancer.color_temperature(
                        temperature=custom_preset.get('temperature', 0)
                    )
                    enhancer.portrait_enhancements(
                        skin_smoothing=custom_preset.get('skin_smoothing', 0)
                    )

                    enhanced_img = enhancer.get_result()

                    # Resize
                    original_ratio = enhanced_img.width / enhanced_img.height
                    target_width = int((total_pixels * original_ratio) ** 0.5)
                    target_height = int(total_pixels / target_width)
                    target_size = (target_width, target_height)
                    final_img = enhanced_img.resize(
                        target_size, Image.Resampling.LANCZOS)

                    # Add watermark
                    if ENABLE_WATERMARK:
                        final_img = add_watermark(
                            final_img, watermark_opacity=WATERMARK_OPACITY, scale_factor=WATERMARK_SCALE)

                    # Save with original filename prefix + mode prefix
                    original_name = os.path.splitext(
                        os.path.basename(full_path))[0]
                    mode_prefix = get_mode_prefix('custom')
                    new_filename = f'{original_name}_{mode_prefix}.jpg'
                    output_path = os.path.join(output_folder, new_filename)
                    final_img.save(output_path, 'JPEG',
                                   quality=90, optimize=True)

                except Exception as e:
                    print(
                        f"❌ Failed to process {os.path.basename(full_path)}: {e}")

            # Create ZIP archive
            zip_path = create_zip_archive(
                output_folder, project_output_dir, f'{label}_custom')
            print(
                f"✅ Finished {label.upper()} custom folder zipped at:\n{zip_path}")

    finally:
        # Clean up temporary directory if needed
        if is_temp:
            cleanup_temp_directory(working_folder)


def apply_processing_mode(mode_name):
    """Apply a specific processing mode configuration"""
    from utils.config import MODES
    import utils.config as config

    if mode_name in MODES:
        mode_settings = MODES[mode_name]
        config.DEFAULT_COLOR_ENHANCEMENT = mode_settings['color_enhancement']
        config.ENABLE_BRIGHTNESS_AUTO_ADJUST = mode_settings['brightness_adjust']
        config.ENABLE_CONTRAST_AUTO_ADJUST = mode_settings['contrast_adjust']
        config.ENABLE_GAMMA_CORRECTION = mode_settings['gamma_correction']
        config.PORTRAIT_MODE = (mode_name == 'portrait')

        print(f"📋 Mode: {mode_settings['description']}")
    else:
        print(f"⚠️ Unknown mode: {mode_name}")


def get_mode_prefix(preset_name):
    """Generate 3-letter prefix from preset name"""
    mode_prefixes = {
        'portrait_subtle': 'sub',
        'portrait_natural': 'nat',
        'portrait_dramatic': 'drm',
        'studio_portrait': 'std',
        'overexposed_recovery': 'ovr',
        'natural_wildlife': 'wld',
        'enhanced': 'enh',
        'resize_watermark': 'rsz',
        'watermark': 'wtm',
        'resize_only': 'res',
        'custom': 'cst'
    }
    # Default to 'prc' for process
    return mode_prefixes.get(preset_name, 'prc')


if __name__ == "__main__":
    # Uncomment the line below to run with menu
    main()

    # Direct execution (comment out when using menu)
    # process_images(DEFAULT_INPUT_PATH)

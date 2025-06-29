from utils.config import RESOLUTIONS, DEFAULT_INPUT_PATH, DEFAULT_JPEG_QUALITY, DEFAULT_OUTPUT_DIR
from utils.file_operations import extract_zip_if_needed, cleanup_temp_directory, get_image_files_from_directory, create_output_structure, create_zip_archive
from utils.image_processing import add_watermark
import os
import sys
from PIL import Image, ImageEnhance, ExifTags, ImageStat
import zipfile
import numpy as np

# Add the utils directory to the path so we can import config
utils_path = os.path.join(os.path.dirname(__file__), 'utils')
sys.path.insert(0, utils_path)


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

    # Apply enhancements
    enhanced_img = img

    # Brightness adjustment
    if brightness_factor != 1.0:
        enhancer = ImageEnhance.Brightness(enhanced_img)
        enhanced_img = enhancer.enhance(brightness_factor)

    # Contrast adjustment
    if contrast_factor != 1.0:
        enhancer = ImageEnhance.Contrast(enhanced_img)
        enhanced_img = enhancer.enhance(contrast_factor)

    # Gamma correction (simulate with curve adjustment)
    if gamma_factor != 1.0:
        # Create gamma lookup table
        gamma_table = [int(((i / 255.0) ** gamma_factor) * 255)
                       for i in range(256)]
        enhanced_img = enhanced_img.point(gamma_table * 3)  # Apply to R, G, B

    # Final subtle color enhancement
    enhancer = ImageEnhance.Color(enhanced_img)
    enhanced_img = enhancer.enhance(1.05)  # Slight color saturation boost

    return enhanced_img


def process_images(input_path):
    """Process images from a folder or ZIP file"""
    print(f"🎯 Starting photo processing from: {input_path}")

    # Handle ZIP files or folders automatically
    working_folder, is_temp = extract_zip_if_needed(input_path)
    if working_folder is None:
        print("❌ Failed to process input path")
        return

    try:
        # Create output structure
        project_folder = create_output_structure(
            input_path, DEFAULT_OUTPUT_DIR, is_temp)

        # Get all image files recursively
        image_files = get_image_files_from_directory(working_folder)

        if not image_files:
            print("⚠️ No image files found in the input directory")
            return

        print(f"📸 Found {len(image_files)} images to process")

        # Process each resolution
        for label, total_pixels in RESOLUTIONS.items():
            print(
                f"\n🔄 Processing {label.upper()} resolution ({total_pixels:,} pixels)...")

            # Create output folder for this resolution
            output_folder = os.path.join(
                project_folder, f'processed_photos_{label}')
            os.makedirs(output_folder, exist_ok=True)

            processed_count = 0

            for full_path, rel_path in image_files:
                try:
                    img = Image.open(full_path).convert('RGB')

                    # Apply EXIF rotation
                    img = fix_image_orientation(img)

                    # Intelligent lighting analysis and adjustment
                    img = analyze_and_adjust_lighting(img)

                    # Calculate target size maintaining original aspect ratio
                    original_ratio = img.width / img.height

                    # Calculate dimensions to match target pixel count while preserving ratio
                    target_width = int((total_pixels * original_ratio) ** 0.5)
                    target_height = int(total_pixels / target_width)

                    target_size = (target_width, target_height)

                    # Resize to exact target size
                    final_img = img.resize(
                        target_size, Image.Resampling.LANCZOS)

                    # Add watermark to bottom left corner with better visibility
                    final_img = add_watermark(
                        final_img, watermark_opacity=0.9, scale_factor=0.15)

                    # Save with sequential naming
                    processed_count += 1
                    new_filename = f'process_{processed_count:03d}.jpg'
                    output_path = os.path.join(output_folder, new_filename)
                    final_img.save(output_path, 'JPEG',
                                   quality=DEFAULT_JPEG_QUALITY, optimize=True)

                except Exception as e:
                    print(f"❌ Failed to process {rel_path}: {e}")

            # Create ZIP archive for this resolution
            if processed_count > 0:
                zip_path = create_zip_archive(
                    output_folder, project_folder, label)
                print(
                    f"✅ Processed {processed_count} images for {label.upper()}")
                print(f"📦 Created archive: {zip_path}")
            else:
                print(f"⚠️ No images processed for {label.upper()}")

    finally:
        # Clean up temporary directory if it was created
        if is_temp:
            cleanup_temp_directory(working_folder)


# Example usage:
# process_images(r"C:\Users\harit\Documents\temp\26 June photoshoot")

if __name__ == "__main__":
    # Use default input path from config, or allow command line override
    import sys
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = DEFAULT_INPUT_PATH

    print(f"Processing photos from: {input_path}")
    process_images(input_path)

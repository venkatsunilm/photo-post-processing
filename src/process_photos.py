import os
from PIL import Image, ImageEnhance, ExifTags, ImageStat
import zipfile
import numpy as np


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


def process_images(input_folder):
    # Define base resolutions
    resolutions = {
        '2k': 2560 * 1440,  # Total pixels
        '4k': 3840 * 2160   # Total pixels
    }

    for label, total_pixels in resolutions.items():
        output_folder = os.path.join(input_folder, f'processed_photos_{label}')
        os.makedirs(output_folder, exist_ok=True)

        image_files = [f for f in os.listdir(
            input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        image_files.sort()

        print(f"\nProcessing {label.upper()} images...")

        for idx, file_name in enumerate(image_files, 1):
            img_path = os.path.join(input_folder, file_name)
            try:
                img = Image.open(img_path).convert('RGB')

                # Apply EXIF rotation to get the visual orientation you see in file explorer
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
                final_img = img.resize(target_size, Image.Resampling.LANCZOS)

                # Save
                new_filename = f'process_{idx:03d}.jpg'
                output_path = os.path.join(output_folder, new_filename)
                final_img.save(output_path, 'JPEG', quality=90, optimize=True)
            except Exception as e:
                print(f"❌ Failed to process {file_name}: {e}")

        # Zip output folder
        zip_path = os.path.join(input_folder, f'processed_photos_{label}.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(output_folder):
                full_path = os.path.join(output_folder, file)
                zipf.write(full_path, arcname=os.path.join(
                    f'processed_photos_{label}', file))

        print(f"✅ Finished {label.upper()} folder zipped at:\n{zip_path}")


# Example usage:
# process_images(r"C:\Users\harit\Documents\temp\26 June photoshoot")
process_images(r"C:\Users\harit\Documents\temp\Test Photoshoot")

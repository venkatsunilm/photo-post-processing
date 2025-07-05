"""
Image processing utilities for photo post-processing.
Handles image transformations, lighting adjustments, and watermarking.
"""

from typing import Tuple

from PIL import ExifTags, Image, ImageEnhance, ImageStat


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
    """Resize image to target size while maintaining aspect ratio, then crop"""
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


def add_watermark(
    img: Image.Image, watermark_opacity: float = 0.9, scale_factor: float = 0.15
) -> Image.Image:
    """Add image watermark to the bottom left corner of the image with enhanced visibility

    Args:
        img: PIL Image object
        watermark_opacity: Opacity of the watermark (0.0 to 1.0)
        scale_factor: Size of watermark relative to image width (0.1 to 0.3)
    """
    import os

    from .config import DEFAULT_LOGO_PATH

    # Create a copy to avoid modifying the original
    watermarked_img = img.copy()

    # Load watermark image using config path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    watermark_path = os.path.join(project_root, DEFAULT_LOGO_PATH)

    try:
        watermark = Image.open(watermark_path).convert("RGBA")
    except (FileNotFoundError, IOError) as e:
        print(f"Warning: Could not load watermark image from {watermark_path}: {e}")
        return watermarked_img

    # Calculate watermark size based on image dimensions
    img_width, img_height = watermarked_img.size
    watermark_width = int(img_width * scale_factor)

    # Maintain aspect ratio
    aspect_ratio = watermark.height / watermark.width
    watermark_height = int(watermark_width * aspect_ratio)

    # Resize watermark
    watermark = watermark.resize(
        (watermark_width, watermark_height), Image.Resampling.LANCZOS
    )

    # Position watermark in bottom LEFT corner with padding
    padding = 20
    x = padding  # Left side
    y = img_height - watermark_height - padding

    # Convert main image to RGBA if needed
    if watermarked_img.mode != "RGBA":
        watermarked_img = watermarked_img.convert("RGBA")

    # Create a semi-transparent background for better visibility
    bg_padding = 10
    bg_width = watermark_width + (bg_padding * 2)
    bg_height = watermark_height + (bg_padding * 2)

    # Create a subtle background (white with low opacity)
    background = Image.new("RGBA", (bg_width, bg_height), (255, 255, 255, 2))

    # Position background
    bg_x = x - bg_padding
    bg_y = y - bg_padding

    # Ensure background doesn't go outside image bounds
    bg_x = max(0, bg_x)
    bg_y = max(0, bg_y)

    # Paste background first
    watermarked_img.paste(background, (bg_x, bg_y), background)

    # Enhance watermark contrast and opacity
    if watermark_opacity < 1.0:
        # Create a new image with adjusted opacity but higher visibility
        watermark_data = []
        for pixel in watermark.getdata():  # type: ignore[attr-defined]
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
                if a > 0:  # Only modify non-transparent pixels
                    # Enhance contrast and apply opacity
                    new_alpha = min(255, int(a * watermark_opacity * 1.2))
                    watermark_data.append((r, g, b, new_alpha))
                else:
                    watermark_data.append((r, g, b, a))
            else:  # RGB, add alpha
                r, g, b = pixel
                new_alpha = int(255 * watermark_opacity)
                watermark_data.append((r, g, b, new_alpha))

        watermark.putdata(watermark_data)

    # Paste watermark onto image
    watermarked_img.paste(watermark, (x, y), watermark)

    # Convert back to RGB
    rgb_img = Image.new("RGB", watermarked_img.size, (255, 255, 255))
    rgb_img.paste(watermarked_img, mask=watermarked_img.split()[-1])

    return rgb_img


def analyze_and_adjust_lighting(img: Image.Image) -> Image.Image:
    """Analyze image lighting and apply intelligent adjustments"""
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
        brightness_enhancer = ImageEnhance.Brightness(enhanced_img)
        enhanced_img = brightness_enhancer.enhance(brightness_factor)

    # Contrast adjustment
    if contrast_factor != 1.0:
        contrast_enhancer = ImageEnhance.Contrast(enhanced_img)
        enhanced_img = contrast_enhancer.enhance(contrast_factor)

    # Gamma correction (simulate with curve adjustment)
    if gamma_factor != 1.0:
        # Create gamma lookup table
        gamma_table = [int(((i / 255.0) ** gamma_factor) * 255) for i in range(256)]
        enhanced_img = enhanced_img.point(gamma_table * 3)  # Apply to R, G, B

    # Final subtle color enhancement
    color_enhancer = ImageEnhance.Color(enhanced_img)
    enhanced_img = color_enhancer.enhance(1.05)  # Slight color saturation boost

    return enhanced_img


def calculate_target_size(total_pixels: int, original_ratio: float) -> Tuple[int, int]:
    """Calculate target dimensions based on total pixels and aspect ratio"""
    target_width = int((total_pixels * original_ratio) ** 0.5)
    target_height = int(total_pixels / target_width)
    return (target_width, target_height)

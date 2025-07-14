"""
Image processing utility functions for photo post-processing pipeline.
"""

from PIL import ExifTags, Image, ImageEnhance, ImageStat
from typing import Tuple


def fix_image_orientation(img: Image.Image) -> Image.Image:
    """Fix image orientation based on EXIF data only if needed"""
    try:
        exif = img.getexif()
        if exif is not None:
            for tag, value in exif.items():
                if tag in ExifTags.TAGS and ExifTags.TAGS[tag] == "Orientation":
                    if value == 3:
                        img = img.rotate(180, expand=True)
                    elif value == 6:
                        img = img.rotate(270, expand=True)
                    elif value == 8:
                        img = img.rotate(90, expand=True)
                    break
    except (AttributeError, KeyError, TypeError):
        pass
    return img


def resize_and_crop(img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    img_ratio = img.width / img.height
    target_ratio = target_size[0] / target_size[1]
    if img_ratio > target_ratio:
        new_height = target_size[1]
        new_width = int(new_height * img_ratio)
    else:
        new_width = target_size[0]
        new_height = int(new_width / img_ratio)
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
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

    if PORTRAIT_MODE:
        if DEFAULT_COLOR_ENHANCEMENT != 1.0:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(DEFAULT_COLOR_ENHANCEMENT)
        return img
    stat = ImageStat.Stat(img)
    mean_brightness = sum(stat.mean) / len(stat.mean)
    std_dev = sum(stat.stddev) / len(stat.stddev)
    histogram = img.histogram()
    dark_pixels = sum(histogram[0:85])
    total_pixels = img.width * img.height
    dark_ratio = dark_pixels / total_pixels
    bright_pixels = sum(histogram[170:256])
    bright_ratio = bright_pixels / total_pixels
    brightness_factor = 1.0
    contrast_factor = 1.0
    gamma_factor = 1.0
    if mean_brightness < 100:
        brightness_factor = 1.15 + (100 - mean_brightness) / 200
    elif mean_brightness > 180:
        brightness_factor = 0.9 - (mean_brightness - 180) / 300
    if std_dev < 40:
        contrast_factor = 1.2 + (40 - std_dev) / 80
    elif std_dev > 80:
        contrast_factor = 0.95
    if dark_ratio > 0.3:
        gamma_factor = 0.8
    elif bright_ratio > 0.2:
        gamma_factor = 1.2
    enhanced_img = img
    if ENABLE_BRIGHTNESS_AUTO_ADJUST and brightness_factor != 1.0:
        brightness_enhancer = ImageEnhance.Brightness(enhanced_img)
        enhanced_img = brightness_enhancer.enhance(brightness_factor)
    if ENABLE_CONTRAST_AUTO_ADJUST and contrast_factor != 1.0:
        contrast_enhancer = ImageEnhance.Contrast(enhanced_img)
        enhanced_img = contrast_enhancer.enhance(contrast_factor)
    if ENABLE_GAMMA_CORRECTION and gamma_factor != 1.0:
        gamma_table = [int(((i / 255.0) ** gamma_factor) * 255) for i in range(256)]
        enhanced_img = enhanced_img.point(gamma_table * 3)
    color_enhancer = ImageEnhance.Color(enhanced_img)
    enhanced_img = color_enhancer.enhance(DEFAULT_COLOR_ENHANCEMENT)
    return enhanced_img

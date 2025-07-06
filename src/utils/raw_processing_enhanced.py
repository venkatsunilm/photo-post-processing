"""
Enhanced RAW image processing utilities with aggressive tone mapping and vibrance.
Addresses the "dull RAW" problem by applying proper tone curves and enhanced processing.
"""

import os
from typing import Any, Dict, Optional

import numpy as np
import rawpy
from PIL import Image, ImageEnhance


def is_raw_file(file_path: str) -> bool:
    """Check if file is a RAW format that needs special handling"""
    raw_extensions = (
        ".nef",
        ".NEF",
        ".raw",
        ".RAW",
        ".cr2",
        ".CR2",
        ".arw",
        ".ARW",
        ".dng",
        ".DNG",
        ".orf",
        ".ORF",
    )
    return file_path.lower().endswith(raw_extensions)


def apply_tone_curve(img_array: np.ndarray) -> np.ndarray:
    """
    Apply a more aggressive S-curve to enhance contrast and vibrancy.
    This mimics what camera manufacturers do in their JPEG processing.

    Args:
        img_array (np.ndarray): Input image array

    Returns:
        np.ndarray: Contrast-enhanced image array
    """
    # Create a more pronounced S-curve for better contrast
    x = np.linspace(0, 255, 256)
    # More aggressive S-curve formula
    curve = 255 * ((x / 255) ** 0.85)  # More pronounced curve
    curve = np.clip(curve, 0, 255).astype(np.uint8)

    # Apply curve to each channel based on image dimensions
    num_dims = len(img_array.shape)
    if num_dims == 2:
        # 2D grayscale image
        img_array = curve[img_array]
    elif num_dims == 3:
        # 3D image - apply curve to each channel
        for channel in range(img_array.shape[2]):
            img_array[:, :, channel] = curve[img_array[:, :, channel]]

    return img_array


def enhance_raw_vibrancy(image: Image.Image) -> Image.Image:
    """
    Apply additional vibrancy and clarity specifically for RAW files.
    This compensates for the flat look that RAW files often have.

    Args:
        image (Image.Image): Input RAW image

    Returns:
        Image.Image: Vibrancy-enhanced image
    """
    # 1. Increase contrast more aggressively
    contrast_enhancer = ImageEnhance.Contrast(image)
    image = contrast_enhancer.enhance(1.25)  # 25% more contrast

    # 2. Boost color saturation more significantly
    color_enhancer = ImageEnhance.Color(image)
    image = color_enhancer.enhance(1.35)  # 35% more saturation

    # 3. Increase sharpness more noticeably
    sharpness_enhancer = ImageEnhance.Sharpness(image)
    image = sharpness_enhancer.enhance(1.15)  # 15% more sharpness

    # 4. Add more brightness boost to compensate for missing exposure parameters
    brightness_enhancer = ImageEnhance.Brightness(image)
    image = brightness_enhancer.enhance(1.08)  # 8% brighter (increased)

    print("🎨 Applied aggressive vibrancy enhancement for RAW file")
    return image


def load_raw_image_enhanced(
    file_path: str, apply_enhancements: bool = True
) -> Image.Image:
    """
    Load a RAW image file with enhanced processing to avoid the "dull" look.

    Args:
        file_path (str): Path to the RAW image file
        apply_enhancements (bool): Whether to apply additional enhancements

    Returns:
        PIL.Image: Enhanced RGB image that looks vibrant and sharp
    """
    try:
        print(
            f"📸 Loading RAW file with enhanced processing: {os.path.basename(file_path)}"
        )

        with rawpy.imread(file_path) as raw:
            # Use compatible processing parameters for maximum enhancement
            rgb_array = raw.postprocess(
                output_bps=8,  # 8-bit output
                # Allow auto-brightness (helps with exposure)
                no_auto_bright=False,
                use_camera_wb=True,  # Use camera white balance
                half_size=False,  # Full resolution
                four_color_rgb=False,  # Standard 3-color processing
                bright=1.4,  # 40% brighter (increased from 1.3)
                # Positive exposure shift (increased from 0.3)
                exp_shift=0.4,
                auto_bright_thr=0.005,  # Lower threshold for more aggressive auto-brightness
                dcb_enhance=True,  # Enhanced demosaicing for better detail
            )

        # Apply tone curve for better contrast
        if apply_enhancements:
            rgb_array = apply_tone_curve(rgb_array)

        # Ensure proper data type
        if rgb_array.dtype != np.uint8:
            # Normalize to 0-255 range if needed
            rgb_array = np.clip(rgb_array, 0, 255).astype(np.uint8)

        # Convert to PIL Image
        img = Image.fromarray(rgb_array)

        # Apply additional vibrancy enhancements for RAW files
        if apply_enhancements:
            img = enhance_raw_vibrancy(img)

        print(f"✅ Enhanced RAW file loaded: {img.size[0]}x{img.size[1]} pixels")
        return img

    except Exception as e:
        print(f"❌ Error loading RAW file {file_path}: {e}")
        print("💡 Falling back to standard RAW processing...")
        # Fallback to standard processing
        return load_raw_image_standard(file_path)


def load_raw_image_standard(file_path: str) -> Image.Image:
    """
    Standard RAW processing (your original method) as fallback.

    Args:
        file_path (str): Path to the RAW image file

    Returns:
        PIL.Image: Standard processed RGB image
    """
    try:
        with rawpy.imread(file_path) as raw:
            rgb_array = raw.postprocess(
                output_bps=8,
                no_auto_bright=True,
                use_camera_wb=True,
                half_size=False,
                four_color_rgb=False,
            )

        if rgb_array.dtype != np.uint8:
            rgb_array = ((rgb_array / rgb_array.max()) * 255).astype(np.uint8)

        img = Image.fromarray(rgb_array)
        return img

    except Exception as e:
        print(f"❌ Standard RAW processing also failed: {e}")
        # Final fallback to PIL
        try:
            return Image.open(file_path).convert("RGB")
        except Exception as pil_error:
            print(f"❌ PIL fallback also failed: {pil_error}")
            raise


def load_image_smart_enhanced(file_path: str) -> Image.Image:
    """
    Smart image loading with enhanced RAW processing.

    Args:
        file_path (str): Path to the image file

    Returns:
        PIL.Image: Loaded image in RGB format (enhanced if RAW)
    """
    if is_raw_file(file_path):
        return load_raw_image_enhanced(file_path, apply_enhancements=True)
    else:
        # Use PIL for standard formats (JPG, PNG, etc.)
        return Image.open(file_path).convert("RGB")


def load_image_basic(file_path: str) -> Image.Image:
    """
    Basic image loading with minimal RAW processing for watermark-only mode.
    Preserves the original camera look as much as possible.

    Args:
        file_path (str): Path to the image file

    Returns:
        PIL.Image: Loaded image in RGB format (minimal processing if RAW)
    """
    if is_raw_file(file_path):
        return load_raw_image_standard(file_path)  # Use standard, not enhanced
    else:
        # Use PIL for standard formats (JPG, PNG, etc.)
        return Image.open(file_path).convert("RGB")


def compare_raw_processing_methods(file_path: str) -> Optional[Dict[str, Image.Image]]:
    """
    Compare different RAW processing methods for debugging.

    Args:
        file_path (str): Path to RAW file

    Returns:
        dict: Dictionary with different processed versions
    """
    if not is_raw_file(file_path):
        print("❌ File is not a RAW format")
        return None

    print(f"🔍 Comparing RAW processing methods for: {os.path.basename(file_path)}")

    results = {}

    try:
        # Method 1: Conservative (original)
        results["conservative"] = load_raw_image_standard(file_path)
        print("✅ Conservative processing completed")

        # Method 2: Enhanced (new)
        results["enhanced"] = load_raw_image_enhanced(
            file_path, apply_enhancements=True
        )
        print("✅ Enhanced processing completed")

        # Method 3: Enhanced without post-processing
        results["enhanced_no_post"] = load_raw_image_enhanced(
            file_path, apply_enhancements=False
        )
        print("✅ Enhanced (no post) processing completed")

    except Exception as e:
        print(f"❌ Error in comparison: {e}")
        return None

    return results


def get_raw_metadata(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract metadata from RAW file for debugging purposes.

    Args:
        file_path (str): Path to the RAW file

    Returns:
        Optional[Dict[str, Any]]: Metadata dictionary or None if error
    """
    try:
        with rawpy.imread(file_path) as raw:
            metadata = {
                "camera_make": getattr(raw, "camera_make", "Unknown"),
                "camera_model": getattr(raw, "camera_model", "Unknown"),
                "raw_size": getattr(raw, "raw_image_visible", None),
                "color_desc": getattr(raw, "color_desc", None),
                "num_colors": getattr(raw, "num_colors", None),
                "white_balance": getattr(raw, "camera_whitebalance", None),
                "iso_speed": getattr(raw, "other", {}).get("iso_speed", "Unknown"),
            }
            return metadata
    except Exception as e:
        print(f"❌ Error reading RAW metadata: {e}")
        return None

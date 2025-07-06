"""
RAW image processing utilities for handling NEF and other RAW formats.
Provides proper RAW file loading with high-quality conversion to RGB.
"""

import os

import numpy as np
import rawpy
from PIL import Image


def is_raw_file(file_path: str) -> bool:
    """Check if file is a RAW format that needs special handling"""
    raw_extensions = (".nef", ".NEF", ".raw", ".RAW", ".cr2", ".CR2", ".arw", ".ARW")
    return file_path.lower().endswith(raw_extensions)


def load_raw_image(file_path: str) -> Image.Image:
    """
    Load a RAW image file and convert it to a high-quality PIL Image.

    Args:
        file_path (str): Path to the RAW image file

    Returns:
        PIL.Image: High-quality RGB image
    """
    try:
        # print(f"📸 Loading RAW file: {os.path.basename(file_path)}")

        with rawpy.imread(file_path) as raw:
            # Use simple, reliable processing parameters
            rgb_array = raw.postprocess(
                output_bps=8,  # 8-bit output
                no_auto_bright=True,  # Preserve original exposure
                use_camera_wb=True,  # Use camera white balance
                half_size=False,  # Full resolution
                four_color_rgb=False,  # Standard 3-color processing
            )

        # Convert numpy array to PIL Image
        if rgb_array.dtype != np.uint8:
            # Normalize to 0-255 range if needed
            rgb_array = ((rgb_array / rgb_array.max()) * 255).astype(np.uint8)

        img = Image.fromarray(rgb_array)
        # print(
        #     f"✅ RAW file loaded successfully: {img.size[0]}x{img.size[1]} pixels")
        return img

    except Exception as e:
        print(f"❌ Error loading RAW file {file_path}: {e}")
        print(f"💡 Falling back to PIL for {os.path.basename(file_path)}")
        # Fallback to PIL if RAW processing fails
        try:
            return Image.open(file_path).convert("RGB")
        except Exception as pil_error:
            print(f"❌ PIL fallback also failed: {pil_error}")
            raise


def load_image_smart(file_path: str) -> Image.Image:
    """
    Smart image loading that uses appropriate method based on file type.

    Args:
        file_path (str): Path to the image file

    Returns:
        PIL.Image: Loaded image in RGB format
    """
    if is_raw_file(file_path):
        return load_raw_image(file_path)
    else:
        # Use PIL for standard formats (JPG, PNG, etc.)
        return Image.open(file_path).convert("RGB")


def get_raw_metadata(file_path: str) -> dict:
    """
    Extract metadata from RAW file for debugging purposes.

    Args:
        file_path (str): Path to the RAW file

    Returns:
        dict: RAW file metadata
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
        return {}

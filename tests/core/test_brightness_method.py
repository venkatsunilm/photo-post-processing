"""
Unit tests for the brightness_adjustment method in PhotoshopStyleEnhancer.
"""

from PIL import Image
from pro_photo_processor.presets.photoshop_tools import PhotoshopStyleEnhancer


def test_brightness_adjustment_increases_brightness():
    """Test that brightness_adjustment increases image brightness."""
    test_img = Image.new("RGB", (10, 10), color=(100, 100, 100))
    enhancer = PhotoshopStyleEnhancer(test_img)
    enhancer.brightness_adjustment(50)  # 50% brighter
    result_img = enhancer.get_result()
    assert isinstance(result_img, Image.Image)
    # The result should be brighter than the original
    orig_pixel = test_img.getpixel((0, 0))[0]
    new_pixel = result_img.getpixel((0, 0))[0]
    assert new_pixel > orig_pixel


def test_brightness_adjustment_decreases_brightness():
    """Test that brightness_adjustment decreases image brightness."""
    test_img = Image.new("RGB", (10, 10), color=(200, 200, 200))
    enhancer = PhotoshopStyleEnhancer(test_img)
    enhancer.brightness_adjustment(-50)  # 50% darker
    result_img = enhancer.get_result()
    assert isinstance(result_img, Image.Image)
    orig_pixel = test_img.getpixel((0, 0))[0]
    new_pixel = result_img.getpixel((0, 0))[0]
    assert new_pixel < orig_pixel


def test_brightness_adjustment_history():
    """Test that brightness_adjustment records history."""
    test_img = Image.new("RGB", (10, 10), color=(128, 128, 128))
    enhancer = PhotoshopStyleEnhancer(test_img)
    enhancer.brightness_adjustment(10)
    enhancer.brightness_adjustment(-10)
    history = enhancer.get_history()
    assert any("Brightness:" in h for h in history)

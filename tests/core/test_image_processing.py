# Standard library imports
from PIL import Image
from pro_photo_processor.core import image_processing


def test_fix_image_orientation_identity():
    # Minimal test for coverage. Full EXIF-based tests can be added later.
    img = Image.new("RGB", (10, 10), color="red")
    result = image_processing.fix_image_orientation(img)
    assert isinstance(result, Image.Image)
    assert result.size == (10, 10)


def test_resize_and_crop():
    img = Image.new("RGB", (100, 50), color="blue")
    target_size = (40, 40)
    result = image_processing.resize_and_crop(img, target_size)
    assert result.size == target_size


def test_add_watermark_runs(monkeypatch):
    # Patch watermark path and Image.open to avoid file IO
    import pro_photo_processor.config.config as config_mod

    monkeypatch.setattr(config_mod, "DEFAULT_LOGO_PATH", "fake_logo.png")
    import os.path as ospath

    monkeypatch.setattr(ospath, "join", lambda *a: "fake_logo.png")
    monkeypatch.setattr(
        image_processing.Image,
        "open",
        lambda path: Image.new("RGBA", (10, 10), (255, 255, 255, 128)),
    )
    img = Image.new("RGB", (100, 100), color="green")
    result = image_processing.add_watermark(img, watermark_opacity=0.5)
    assert isinstance(result, Image.Image)
    assert result.size == (100, 100)


def test_analyze_and_adjust_lighting():
    img = Image.new("RGB", (50, 50), color=(50, 50, 50))  # Dark image
    result = image_processing.analyze_and_adjust_lighting(img)
    assert isinstance(result, Image.Image)
    assert result.size == (50, 50)


def test_calculate_target_size():
    total_pixels = 40000
    aspect_ratio = 1.0
    width, height = image_processing.calculate_target_size(total_pixels, aspect_ratio)
    assert width * height <= total_pixels + width  # Allow rounding
    assert abs(width / height - aspect_ratio) < 0.1

from PIL import Image
from pro_photo_processor.core.image_processing import fix_image_orientation


def test_fix_image_orientation_identity():
    # NOTE: This is a minimal test to increase coverage. Full EXIF-based tests will be added in future updates.
    img = Image.new("RGB", (10, 10), color="red")
    result = fix_image_orientation(img)
    assert isinstance(result, Image.Image)
    assert result.size == (10, 10)

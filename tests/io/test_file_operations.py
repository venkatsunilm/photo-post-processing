import os
import pytest
from pro_photo_processor.io import file_operations


# --- Fixtures ---
@pytest.fixture
def input_output_dirs(tmp_path):
    """Fixture to create input and output directories for tests."""
    input_path = tmp_path / "input"
    input_path.mkdir()
    output_dir = tmp_path / "output"
    yield str(input_path), str(output_dir)
    # Cleanup handled by tmp_path


@pytest.fixture
def sample_image_file(tmp_path):
    """Fixture to create a sample image file in tmp_path."""
    img_file = tmp_path / "test.jpg"
    img_file.write_bytes(b"fake image data")
    return str(img_file)


def test_create_output_structure(input_output_dirs):
    """Test that create_output_structure creates the output directory as expected."""
    input_path, output_dir = input_output_dirs
    result = file_operations.create_output_structure(input_path, output_dir, False)
    assert os.path.exists(result), "Output directory was not created."


def test_get_image_files_from_directory(tmp_path, sample_image_file):
    """Test that get_image_files_from_directory returns a list of image files."""
    files = file_operations.get_image_files_from_directory(str(tmp_path))
    assert isinstance(files, list), "Returned value is not a list."
    assert any("test.jpg" in f for f in files), "Image file not found in returned list."

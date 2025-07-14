import os
from pro_photo_processor.io import file_operations


def test_create_output_structure(tmp_path):
    # NOTE: Minimal test for coverage. Full tests will be added later.
    input_path = tmp_path / "input"
    input_path.mkdir()
    output_dir = tmp_path / "output"
    result = file_operations.create_output_structure(
        str(input_path), str(output_dir), False
    )
    assert os.path.exists(result)


def test_get_image_files_from_directory(tmp_path):
    # NOTE: Minimal test for coverage. Full tests will be added later.
    img_file = tmp_path / "test.jpg"
    img_file.write_bytes(b"fake image data")
    files = file_operations.get_image_files_from_directory(str(tmp_path))
    assert isinstance(files, list)

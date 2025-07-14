# Standard library imports
import os
import sys
import zipfile

# Third-party imports
import pytest

# Local imports
from pro_photo_processor.io import file_operations


def test_prompt_to_open_folder_yes(monkeypatch, tmp_path):
    """
    Test prompt_to_open_folder with 'yes' input. Should attempt to open folder (mocked).
    """
    folder = tmp_path
    # Simulate user input 'y'
    monkeypatch.setattr("builtins.input", lambda _: "y")
    # Mock os.startfile, subprocess.run to avoid side effects
    called = {}
    if sys.platform == "win32":
        monkeypatch.setattr(
            os, "startfile", lambda path: called.setdefault("startfile", path)
        )
    else:
        monkeypatch.setattr(
            "subprocess.run", lambda args: called.setdefault("run", args)
        )
    file_operations.prompt_to_open_folder(str(folder))
    # Check that the open function was called
    assert called, "No open function was called."


def test_prompt_to_open_folder_no(monkeypatch, tmp_path):
    """
    Test prompt_to_open_folder with 'no' input. Should not attempt to open folder.
    """
    folder = tmp_path
    monkeypatch.setattr("builtins.input", lambda _: "n")
    # Patch os.startfile and subprocess.run to raise if called
    if sys.platform == "win32":
        monkeypatch.setattr(
            os,
            "startfile",
            lambda path: (_ for _ in ()).throw(AssertionError("Should not be called")),
        )
    else:
        monkeypatch.setattr(
            "subprocess.run",
            lambda args: (_ for _ in ()).throw(AssertionError("Should not be called")),
        )
    file_operations.prompt_to_open_folder(str(folder))


# --- Fixtures ---
@pytest.fixture
def input_output_dirs(tmp_path):
    """Create and return input and output directories for tests."""
    input_path = tmp_path / "input"
    input_path.mkdir()
    output_dir = tmp_path / "output"
    yield str(input_path), str(output_dir)


@pytest.fixture
def sample_image_file(tmp_path):
    """Create and return a sample image file in tmp_path."""
    img_file = tmp_path / "test.jpg"
    img_file.write_bytes(b"fake image data")
    return str(img_file)


def test_create_output_structure(input_output_dirs):
    """
    Test that create_output_structure creates the output directory as expected.
    """
    input_path, output_dir = input_output_dirs
    result = file_operations.create_output_structure(input_path, output_dir, False)
    assert os.path.exists(result), "Output directory was not created."


def test_get_image_files_from_directory(tmp_path, sample_image_file):
    """
    Test that get_image_files_from_directory returns a list of image files.
    """
    files = file_operations.get_image_files_from_directory(str(tmp_path))
    assert isinstance(files, list), "Returned value is not a list."
    assert any("test.jpg" in f for f in files), "Image file not found in returned list."


# --- TODO: Add more robust and meaningful tests for each public function ---


def test_extract_zip_if_needed_with_zip(tmp_path):
    """
    Test extract_zip_if_needed extracts images from a zip file and returns temp dir.
    """
    # Create a zip file with a fake image
    img_name = "test.jpg"
    img_path = tmp_path / img_name
    img_path.write_bytes(b"fake image data")
    zip_path = tmp_path / "images.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(img_path, arcname=img_name)
    temp_dir, is_temp = file_operations.extract_zip_if_needed(str(zip_path))
    assert is_temp is True
    assert temp_dir is not None
    extracted = os.listdir(temp_dir)
    assert img_name in extracted or any(img_name in f for f in extracted), (
        "Image not extracted from zip."
    )
    # Cleanup
    file_operations.cleanup_temp_directory(temp_dir)


def test_extract_zip_if_needed_with_folder(tmp_path):
    """
    Test extract_zip_if_needed returns folder path and False for non-zip input.
    """
    folder = tmp_path / "input_folder"
    folder.mkdir()
    result_path, is_temp = file_operations.extract_zip_if_needed(str(folder))
    assert result_path == str(folder)
    assert is_temp is False


def test_cleanup_temp_directory_removes_dir(tmp_path):
    """
    Test cleanup_temp_directory removes the specified directory.
    """
    temp_dir = tmp_path / "toremove"
    temp_dir.mkdir()
    file_path = temp_dir / "file.txt"
    file_path.write_text("data")
    assert os.path.exists(temp_dir)
    file_operations.cleanup_temp_directory(str(temp_dir))
    assert not os.path.exists(temp_dir), "Temp directory was not removed."


def test_create_zip_archive(tmp_path, sample_image_file):
    """
    Test create_zip_archive creates a zip file containing processed images.
    """
    # Setup output and project folders
    output_folder = tmp_path / "output"
    output_folder.mkdir()
    # Copy sample image to output_folder
    img_name = os.path.basename(sample_image_file)
    dest_img = output_folder / img_name
    with open(sample_image_file, "rb") as src, open(dest_img, "wb") as dst:
        dst.write(src.read())
    project_folder = tmp_path / "project"
    project_folder.mkdir()
    label = "unit"
    zip_path = file_operations.create_zip_archive(
        str(output_folder), str(project_folder), label
    )
    assert os.path.exists(zip_path), "Zip archive was not created."
    with zipfile.ZipFile(zip_path, "r") as zf:
        assert any(img_name in f for f in zf.namelist()), (
            "Image not found in zip archive."
        )

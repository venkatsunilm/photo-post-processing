"""
Tests for copy_or_cut_files module, specifically the create_backup_zip function.
"""

import os
import tempfile
import zipfile
from datetime import datetime
from typing import List, Tuple
from unittest.mock import patch

from pro_photo_processor.io.others.file_copy_move import create_backup_zip


class TestCreateBackupZip:
    """Test cases for create_backup_zip function."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.temp_files: List[str] = []

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        # Clean up created files
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except OSError:
                pass

        # Clean up test directory
        try:
            if os.path.exists(self.test_dir):
                import shutil

                shutil.rmtree(self.test_dir)
        except OSError:
            pass

    def test_create_backup_zip_empty_input(self) -> None:
        """Test create_backup_zip with empty file list."""
        result = create_backup_zip(self.test_dir, [])
        assert result == ""

    def test_create_backup_zip_normal_backup(self) -> None:
        """Test create_backup_zip with normal file list."""
        # Create test files in the destination directory
        test_file1 = os.path.join(self.test_dir, "test1.jpg")
        test_file2 = os.path.join(self.test_dir, "test2.jpg")

        with open(test_file1, "w") as f:
            f.write("test content 1")
        with open(test_file2, "w") as f:
            f.write("test content 2")

        self.temp_files.extend([test_file1, test_file2])

        # Create file list in the format expected by the function
        files: List[Tuple[str, str, int]] = [
            (test_file1, "test1.jpg", 100),
            (test_file2, "test2.jpg", 200),
        ]

        # Call the function
        result = create_backup_zip(self.test_dir, files)

        # Verify result
        assert result != ""
        assert os.path.exists(result)
        assert result.endswith(".zip")

        # Verify the ZIP contains the expected structure
        with zipfile.ZipFile(result, "r") as zipf:
            zip_contents = zipf.namelist()
            assert "test1.jpg" in zip_contents
            assert "test2.jpg" in zip_contents

        # Clean up the ZIP file
        if os.path.exists(result):
            os.remove(result)

    def test_create_backup_zip_filename_format(self) -> None:
        """Test that backup ZIP has correct filename format."""
        # Create a test file
        test_file = os.path.join(self.test_dir, "IMG_001.jpg")
        with open(test_file, "w") as f:
            f.write("test content")

        self.temp_files.append(test_file)

        files: List[Tuple[str, str, int]] = [(test_file, "IMG_001.jpg", 100)]

        result = create_backup_zip(self.test_dir, files)

        # Verify filename format: backup_YYYY-MM-DD_firstfile_to_lastfile.zip
        expected_date = datetime.now().strftime("%Y-%m-%d")
        assert expected_date in result
        assert "backup_" in result
        assert "IMG_001_to_IMG_001.zip" in result

        # Clean up
        if os.path.exists(result):
            os.remove(result)

    def test_create_backup_zip_multiple_files_naming(self) -> None:
        """Test backup ZIP naming with multiple files (first to last)."""
        # Create test files with specific names for sorting
        test_file1 = os.path.join(self.test_dir, "IMG_001.jpg")
        test_file2 = os.path.join(self.test_dir, "IMG_999.jpg")

        with open(test_file1, "w") as f:
            f.write("content1")
        with open(test_file2, "w") as f:
            f.write("content2")

        self.temp_files.extend([test_file1, test_file2])

        files: List[Tuple[str, str, int]] = [
            (test_file2, "IMG_999.jpg", 200),  # Note: order doesn't matter
            (test_file1, "IMG_001.jpg", 100),
        ]

        result = create_backup_zip(self.test_dir, files)

        # Should be sorted: IMG_001 to IMG_999
        assert "IMG_001_to_IMG_999.zip" in result

        # Clean up
        if os.path.exists(result):
            os.remove(result)

    @patch("builtins.print")
    def test_create_backup_zip_error_handling(self, mock_print) -> None:
        """Test create_backup_zip error handling with invalid directory."""
        # Use a non-existent directory that should cause an error
        invalid_dir = "/nonexistent/directory/that/should/not/exist"

        files: List[Tuple[str, str, int]] = [("dummy.jpg", "dummy.jpg", 100)]

        result = create_backup_zip(invalid_dir, files)

        # Should return empty string on error
        assert result == ""

        # Should have printed an error message
        mock_print.assert_called()
        error_calls = [
            call
            for call in mock_print.call_args_list
            if "❌ Error creating backup ZIP:" in str(call)
        ]
        assert len(error_calls) > 0

    def test_create_backup_zip_subdirectory_structure(self) -> None:
        """Test that backup ZIP preserves subdirectory structure."""
        # Create subdirectory structure
        subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(subdir, exist_ok=True)

        test_file1 = os.path.join(self.test_dir, "root.jpg")
        test_file2 = os.path.join(subdir, "sub.jpg")

        with open(test_file1, "w") as f:
            f.write("root content")
        with open(test_file2, "w") as f:
            f.write("sub content")

        self.temp_files.extend([test_file1, test_file2])

        files: List[Tuple[str, str, int]] = [
            (test_file1, "root.jpg", 100),
            (test_file2, "subdir/sub.jpg", 100),
        ]

        result = create_backup_zip(self.test_dir, files)

        # Verify ZIP structure
        with zipfile.ZipFile(result, "r") as zipf:
            zip_contents = zipf.namelist()
            assert "root.jpg" in zip_contents
            assert "subdir/sub.jpg" in zip_contents

        # Clean up
        if os.path.exists(result):
            os.remove(result)

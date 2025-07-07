"""
File system utilities for photo post-processing.
Handles ZIP extraction, directory operations, and file management.
"""

import datetime
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from typing import List, Optional, Tuple

from pro_photo_processor.config.config import IMAGE_EXTENSIONS_CASE


def prompt_to_open_folder(folder_path: str) -> None:
    """Prompt user to open the extracted folder"""
    try:
        response = (
            input(
                f"\n📂 Would you like to open the extracted folder?\n   {folder_path}\n   (y/n): "
            )
            .strip()
            .lower()
        )

        if response in ["y", "yes"]:
            print("🚀 Opening folder...")

            # Platform-specific folder opening
            if sys.platform == "win32":
                os.startfile(folder_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", folder_path])

            print("✅ Folder opened successfully!")
        else:
            print("📁 Folder location noted. You can open it manually if needed.")

    except Exception as e:
        print(f"⚠️ Could not open folder automatically: {e}")
        print(f"📁 You can manually open: {folder_path}")


def extract_zip_if_needed(input_path: str) -> Tuple[Optional[str], bool]:
    """Extract ZIP file to temporary directory if input is a ZIP file"""
    if input_path.lower().endswith(".zip") and zipfile.is_zipfile(input_path):
        print(f"📦 Detected ZIP file: {os.path.basename(input_path)}")
        print("🔧 Extracting images to temporary directory...")

        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="photo_processing_")

        try:
            with zipfile.ZipFile(input_path, "r") as zip_ref:
                # Extract image files including NEF
                extracted_count = 0

                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith(IMAGE_EXTENSIONS_CASE):
                        zip_ref.extract(file_info, temp_dir)
                        extracted_count += 1

                print(f"✅ Extracted {extracted_count} image files")
                return temp_dir, True  # Return temp_dir and is_temp flag

        except Exception as e:
            print(f"❌ Failed to extract ZIP file: {e}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None, False
    else:
        # It's a regular folder
        return input_path, False


def cleanup_temp_directory(temp_dir: str) -> None:
    """Clean up temporary directory"""
    try:
        shutil.rmtree(temp_dir)
        print("🧹 Cleaned up temporary directory")
    except Exception as e:
        print(f"⚠️ Warning: Could not clean up temp directory: {e}")


def get_image_files_from_directory(directory: str) -> List[Tuple[str, str]]:
    """Get all image files from a directory, including subdirectories"""
    image_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(IMAGE_EXTENSIONS_CASE):
                full_path = os.path.join(root, file)
                # Get relative path for better organization
                rel_path = os.path.relpath(full_path, directory)
                image_files.append((full_path, rel_path))

    return image_files


def create_output_structure(
    input_path: str, base_output_dir: str, is_temp: bool
) -> str:
    """Create organized output directory structure using current date"""
    os.makedirs(base_output_dir, exist_ok=True)

    # Create a folder with current date instead of source name
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Create main project folder with current date
    project_folder = os.path.join(base_output_dir, current_date)
    os.makedirs(project_folder, exist_ok=True)

    return project_folder


def create_zip_archive(output_folder: str, project_folder: str, label: str) -> str:
    """Create ZIP archive of processed images"""
    zip_name = f"processed_photos_{label}.zip"
    zip_path = os.path.join(project_folder, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(output_folder):
            full_path = os.path.join(output_folder, file)
            zipf.write(
                full_path, arcname=os.path.join(f"processed_photos_{label}", file)
            )

    return zip_path

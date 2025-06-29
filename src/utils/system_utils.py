"""
System utilities for photo post-processing.
Handles cross-platform operations and user interactions.
"""

import subprocess
import platform
import os


def open_folder_in_explorer(folder_path):
    """Open folder in Windows Explorer (or equivalent on other platforms)"""
    try:
        if platform.system() == "Windows":
            subprocess.run(f'explorer "{folder_path}"', shell=True)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", folder_path])
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", folder_path])
        else:
            print(f"📁 Output folder: {folder_path}")
    except Exception as e:
        print(f"⚠️ Could not open folder: {e}")
        print(f"📁 Manual path: {folder_path}")


def get_user_input_path(default_path=None):
    """Get input path from user with smart default handling"""
    if default_path and os.path.exists(default_path):
        print(f"📁 Using default path: {default_path}")
        return default_path
    else:
        # Ask user for input if default path doesn't exist
        if default_path:
            print(f"⚠️ Default path not found: {default_path}")

        input_path = input(
            "📁 Enter folder path or ZIP file path: ").strip().strip('"')

        if not input_path:
            print("❌ No input provided. Exiting...")
            exit()

        return input_path


def prompt_open_folder(project_folder):
    """Prompt user to open output folder and handle the response"""
    print("\n" + "=" * 60)
    try:
        choice = input(
            "🚀 Open output folder in Explorer? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            print("📂 Opening folder in Explorer...")
            open_folder_in_explorer(project_folder)
        else:
            print("📋 You can manually navigate to:")
            print(f"   {project_folder}")
    except KeyboardInterrupt:
        print("\n📋 Output saved to:")
        print(f"   {project_folder}")


def print_header():
    """Print application header with features"""
    print("=" * 60)
    print("📸 PHOTO POST-PROCESSING SCRIPT")
    print("=" * 60)
    print("✨ Features:")
    print("   • Intelligent lighting adjustments")
    print("   • 2K & 4K resolution processing")
    print("   • Watermark: @venkatminchala")
    print("   • Supports folders and ZIP files")
    print("=" * 60)


def print_processing_header():
    """Print processing utility header"""
    print("=" * 60)
    print("📸 PHOTO PROCESSING UTILITY")
    print("=" * 60)

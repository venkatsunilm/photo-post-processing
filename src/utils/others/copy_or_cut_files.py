import os
import shutil
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple


def list_media_files(source_dir: str) -> List[Tuple[str, str, int]]:
    """List all media files including .NEF in the source directory with progress"""
    print("🔍 Scanning external drive for files... (this may take a moment)")
    start_time = time.time()

    try:
        files = []
        file_count = 0

        for root, dirs, filenames in os.walk(source_dir):
            for filename in filenames:
                file_count += 1
                if file_count % 100 == 0:  # Progress indicator
                    print(f"   📂 Scanned {file_count} files...")

                if filename.lower().endswith(
                    (
                        ".jpg",
                        ".jpeg",
                        ".png",
                        ".mp4",
                        ".mov",
                        ".avi",
                        ".raw",
                        ".cr2",
                        ".nef",
                    )
                ):
                    full_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(full_path, source_dir)
                    file_size = os.path.getsize(full_path)
                    files.append((full_path, relative_path, file_size))

        scan_time = time.time() - start_time
        print(
            f"✅ Scan complete! Found {len(files)} media files in {scan_time:.1f} seconds"
        )
        return files
    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return []


def copy_single_file(
    file_info: Tuple[str, str, int],
    dest_dir: str,
    progress_lock: threading.Lock,
    copied_count: List[int],
    skipped_count: List[int],
    total_files: int,
) -> Tuple[bool, str, str]:
    """Copy a single file with progress tracking and resume capability"""
    full_path, relative_path, file_size = file_info

    try:
        dest_path = os.path.join(dest_dir, relative_path)
        dest_folder = os.path.dirname(dest_path)
        os.makedirs(dest_folder, exist_ok=True)

        # Check if file already exists and has the same size (resume functionality)
        if os.path.exists(dest_path):
            existing_size = os.path.getsize(dest_path)
            if existing_size == file_size:
                with progress_lock:
                    skipped_count[0] += 1
                    size_mb = file_size / (1024 * 1024)
                    print(
                        f"⏭️  [{copied_count[0] + skipped_count[0]}/{total_files}] Skipped (exists): {relative_path} ({size_mb:.1f} MB)"
                    )
                return True, relative_path, "skipped"
            else:
                with progress_lock:
                    print(f"🔄 Size mismatch for {relative_path}, re-copying...")

        # Use high-performance copy with buffering
        shutil.copy2(full_path, dest_path)

        # Verify the copy was successful
        if os.path.exists(dest_path) and os.path.getsize(dest_path) == file_size:
            with progress_lock:
                copied_count[0] += 1
                size_mb = file_size / (1024 * 1024)
                print(
                    f"✅ [{copied_count[0] + skipped_count[0]}/{total_files}] Copied: {relative_path} ({size_mb:.1f} MB)"
                )
            return True, relative_path, "copied"
        else:
            raise Exception("File copy verification failed")

    except Exception as e:
        with progress_lock:
            print(f"❌ Failed to copy {relative_path}: {e}")
        return False, relative_path, "failed"


def delete_all_files(source_dir: str) -> None:
    """Delete ALL files from source directory"""
    print("\n🗑️ Scanning for ALL files to delete...")
    try:
        files_to_delete = []
        for root, dirs, filenames in os.walk(source_dir):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                relative_path = os.path.relpath(full_path, source_dir)
                files_to_delete.append((full_path, relative_path))

        if not files_to_delete:
            print("❌ No files found to delete")
            return

        print(f"📊 Found {len(files_to_delete)} total files to delete")
        deleted_count = 0

        for full_path, relative_path in files_to_delete:
            try:
                os.remove(full_path)
                deleted_count += 1
                print(
                    f"🗑️ [{deleted_count}/{len(files_to_delete)}] Deleted: {relative_path}"
                )
            except Exception as e:
                print(f"❌ Failed to delete {relative_path}: {e}")

        print(
            f"\n🎉 Successfully deleted {deleted_count} out of {len(files_to_delete)} files"
        )

        # Clean up empty directories
        cleanup_empty_dirs(source_dir)

    except Exception as e:
        print(f"❌ Error during deletion: {e}")


def cleanup_empty_dirs(directory: str) -> None:
    """Remove empty directories recursively"""
    try:
        for root, dirs, files in os.walk(directory, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # Directory is empty
                        os.rmdir(dir_path)
                        print(
                            f"🗑️ Removed empty directory: {os.path.relpath(dir_path, directory)}"
                        )
                except OSError:
                    pass  # Directory not empty or permission denied
    except Exception as e:
        print(f"❌ Error cleaning up directories: {e}")


def copy_files(source_dir: str, dest_dir: str) -> bool:
    """Copy all media files from source to destination with multi-threading and resume capability"""
    files = list_media_files(source_dir)

    if not files:
        print("❌ No media files found in source directory")
        return False

    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Calculate total size
    total_size = sum(file_info[2] for file_info in files)
    total_size_gb = total_size / (1024 * 1024 * 1024)

    print(f"\n📋 Found {len(files)} media files to copy ({total_size_gb:.2f} GB)")
    print("🔍 Checking for existing files (resume capability)...")
    print("🚀 Starting multi-threaded copy operation...")

    # Progress tracking
    progress_lock = threading.Lock()
    copied_count = [0]  # Use list for mutable reference
    skipped_count = [0]  # Track skipped files
    start_time = time.time()

    # Use ThreadPoolExecutor for concurrent copying
    # Limit threads to avoid overwhelming external drive
    max_workers = min(4, len(files))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all copy tasks
        future_to_file = {
            executor.submit(
                copy_single_file,
                file_info,
                dest_dir,
                progress_lock,
                copied_count,
                skipped_count,
                len(files),
            ): file_info
            for file_info in files
        }

        # Process completed tasks
        successful_copies = 0
        for future in as_completed(future_to_file):
            success, relative_path, status = future.result()
            if success:
                successful_copies += 1

    # Final summary
    end_time = time.time()
    duration = end_time - start_time

    print("\n🎉 Copy operation completed!")
    print(f"✅ Successfully copied: {copied_count[0]} files")
    print(f"⏭️  Skipped (already exist): {skipped_count[0]} files")
    print(f"📊 Total processed: {successful_copies}/{len(files)} files")
    print(f"⏱️ Total time: {duration:.1f} seconds")

    if copied_count[0] > 0:
        copied_size = sum(
            file_info[2]
            for file_info in files
            if file_info
            not in [f for f in files if os.path.exists(os.path.join(dest_dir, f[1]))]
        )
        avg_speed = copied_size / duration / (1024 * 1024) if duration > 0 else 0
        print(f"📈 Average speed: {avg_speed:.1f} MB/s")

    # Return success status for deletion prompt
    return successful_copies == len(files)


def main() -> None:
    source_dir = r"D:\DCIM"
    dest_dir = r"C:\Users\harit\Documents\temp\From Camera"

    print("=" * 60)
    print("📁 HIGH-PERFORMANCE FILE COPY UTILITY")
    print("=" * 60)
    print(f"Source: {source_dir} (External Drive)")
    print(f"Destination: {dest_dir}")
    print("=" * 60)
    print("🔄 RESUME CAPABILITY:")
    print("  • Automatically skips files that already exist with correct size")
    print("  • Safe to restart after interruption")
    print("  • Only copies missing or corrupted files")
    print("=" * 60)

    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"❌ Source directory does not exist: {source_dir}")
        return

    # Ask about deletion preference BEFORE starting copy
    print("🤔 WORKFLOW CONFIGURATION")
    print("=" * 60)
    print("After copying all media files, do you want to:")
    print("1. Keep all files on external drive (safe)")
    print("2. Delete ALL files from external drive")
    print("=" * 60)

    delete_after_copy = False
    while True:
        try:
            choice = input("\nEnter your choice (1 or 2): ").strip()

            if choice == "1":
                print("✅ Will keep all files on external drive after copying")
                delete_after_copy = False
                break
            elif choice == "2":
                print("⚠️ Will DELETE ALL files from external drive after copying")
                print("⚠️ This CANNOT be undone!")
                confirm = input("Are you sure? Type 'YES' to confirm: ").strip()
                if confirm.upper() == "YES":
                    print("✅ Confirmed: Will delete all files after successful copy")
                    delete_after_copy = True
                    break
                else:
                    print("❌ Not confirmed. Will keep files on external drive.")
                    delete_after_copy = False
                    break
            else:
                print("❌ Please enter 1 or 2")
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
            return

    print("\n" + "=" * 60)
    print("⚡ Optimizations enabled:")
    print("  • Multi-threaded copying (4 concurrent threads)")
    print("  • Progress tracking with file sizes")
    print("  • Speed monitoring")
    print("  • Includes all media files (JPG, PNG, MP4, RAW, NEF)")
    print("  • Resume capability (skips existing files)")
    print("  • File integrity verification")
    print("")

    # Copy files first
    copy_successful = copy_files(source_dir, dest_dir)

    # Delete files if user chose to and copy was successful
    if copy_successful and delete_after_copy:
        print("\n" + "=" * 60)
        print("🗑️ AUTO-DELETING ALL FILES FROM SOURCE")
        print("=" * 60)
        print("✅ Copy operation was successful!")
        print("🚀 Proceeding to delete ALL files from external drive as requested...")
        print("=" * 60)

        delete_all_files(source_dir)
    elif copy_successful and not delete_after_copy:
        print("\n✅ Copy completed! Files kept on external drive as requested.")
    elif not copy_successful:
        print("\n❌ Copy operation had errors. Deletion skipped for safety.")
        if delete_after_copy:
            print("💡 You can manually delete files after reviewing the errors.")


if __name__ == "__main__":
    main()

import os
from typing import Any, Dict, Optional
from PIL import Image


class ImageProcessingPipeline:
    def __init__(
        self,
        config: Any,
        file_ops: Any,
        image_processor: Any,
        preset_manager: Optional[Any] = None,
    ):
        """
        Initialize the pipeline with dependencies.
        :param config: Configuration object or module
        :param file_ops: File operations module or class
        :param image_processor: Image processing utilities
        :param preset_manager: Preset/format optimizer (optional)
        """
        self.config = config
        self.file_ops = file_ops
        self.image_processor = image_processor
        self.preset_manager = preset_manager

    def process_images(self, input_path: str, mode: str = "full") -> None:
        """
        Main entry point for processing images in different modes.
        :param input_path: Path to input images or folder
        :param mode: Processing mode (e.g., 'full', 'resize_only', etc.)
        """
        print(f"🎨 Starting processing in {mode} mode...")

        # Handle ZIP extraction if needed
        working_folder, is_temp = self.file_ops.extract_zip_if_needed(input_path)
        if working_folder is None:
            print("❌ Failed to process input. Please check the file/folder path.")
            return

        try:
            # Create organized output structure
            project_output_dir = self.file_ops.create_output_structure(
                input_path, self.config.DEFAULT_OUTPUT_DIR, is_temp
            )

            # Get all image files from directory (including subdirectories)
            image_files = self.file_ops.get_image_files_from_directory(working_folder)

            if not image_files:
                print("❌ No image files found in the input!")
                return

            print(f"📁 Found {len(image_files)} image files to process")

            from pro_photo_processor.utils import get_mode_prefix

            for label, total_pixels in self.config.RESOLUTIONS.items():
                # Add mode suffix to directory name for proper separation
                mode_suffix = get_mode_prefix(mode)
                output_folder = os.path.join(
                    project_output_dir, f"processed_photos_{label}_{mode_suffix}"
                )
                os.makedirs(output_folder, exist_ok=True)

                print(f"\nProcessing {label.upper()} images...")

                for idx, (full_path, rel_path) in enumerate(image_files, 1):
                    try:
                        # Use basic loading for watermark modes, enhanced for full mode
                        if (
                            mode == "watermark"
                            or mode == "resize_watermark"
                            or mode == "resize_only"
                        ):
                            img = self.image_processor.load_image_basic(full_path)
                        else:
                            img = self.image_processor.load_image_smart_enhanced(
                                full_path
                            )

                        # Apply EXIF rotation to get the visual orientation you see in file explorer
                        img = self.image_processor.fix_image_orientation(img)

                        if mode == "full":
                            # Intelligent lighting analysis and adjustment
                            img = self.image_processor.analyze_and_adjust_lighting(img)

                            # Calculate target size maintaining original aspect ratio
                            original_ratio = img.width / img.height

                            # Calculate dimensions to match target pixel count while preserving ratio
                            target_width = int((total_pixels * original_ratio) ** 0.5)
                            target_height = int(total_pixels / target_width)

                            target_size = (target_width, target_height)

                            # Resize to exact target size
                            final_img = img.resize(
                                target_size, Image.Resampling.LANCZOS
                            )
                        elif mode == "resize_watermark":
                            # Resize without any enhancements
                            original_ratio = img.width / img.height

                            # Calculate dimensions to match target pixel count while preserving ratio
                            target_width = int((total_pixels * original_ratio) ** 0.5)
                            target_height = int(total_pixels / target_width)

                            target_size = (target_width, target_height)

                            # Resize to exact target size
                            final_img = img.resize(
                                target_size, Image.Resampling.LANCZOS
                            )
                        elif mode == "resize_only":
                            # Resize only without any enhancements or watermark
                            original_ratio = img.width / img.height

                            # Calculate dimensions to match target pixel count while preserving ratio
                            target_width = int((total_pixels * original_ratio) ** 0.5)
                            target_height = int(total_pixels / target_width)

                            target_size = (target_width, target_height)

                            # Resize to exact target size
                            final_img = img.resize(
                                target_size, Image.Resampling.LANCZOS
                            )
                        else:
                            # Watermark-only mode: keep original size
                            final_img = img

                        # Add watermark to the processed image (skip for resize_only mode)
                        if self.config.ENABLE_WATERMARK and mode != "resize_only":
                            final_img = self.image_processor.add_watermark(
                                final_img,
                                watermark_opacity=self.config.WATERMARK_OPACITY,
                                scale_factor=self.config.WATERMARK_SCALE,
                            )
                            print(
                                f"   💧 Added watermark to {os.path.basename(full_path)}"
                            )
                        elif mode == "resize_only":
                            print(
                                f"   📐 Resize only (no watermark) for {os.path.basename(full_path)}"
                            )
                        else:
                            print(
                                f"   ⚠️ Watermark disabled in config for {os.path.basename(full_path)}"
                            )

                        # Save with original filename prefix + mode prefix
                        original_name = os.path.splitext(os.path.basename(full_path))[0]
                        mode_prefix = self.image_processor.get_mode_prefix(mode)
                        new_filename = f"{original_name}_{mode_prefix}.jpg"
                        output_path = os.path.join(output_folder, new_filename)
                        final_img.save(output_path, "JPEG", quality=90, optimize=True)
                    except Exception as e:
                        print(
                            f"❌ Failed to process {os.path.basename(full_path)}: {e}"
                        )

                # Create ZIP archive with mode suffix
                zip_path = self.file_ops.create_zip_archive(
                    output_folder, project_output_dir, f"{label}_{mode_suffix}"
                )
                print(f"✅ Finished {label.upper()} folder zipped at:\n{zip_path}")

        finally:
            # Clean up temporary directory if needed
            if is_temp:
                self.file_ops.cleanup_temp_directory(working_folder)

    def process_with_preset(self, input_path: str, preset_name: str) -> None:
        """
        Process images using a Photoshop-style preset.
        :param input_path: Path to input images or folder
        :param preset_name: Name of the preset to use
        """
        print(f"🎨 Starting processing with {preset_name} preset...")

        # Always instantiate FormatOptimizer if available
        try:
            from pro_photo_processor.presets.format_optimizer import FormatOptimizer

            optimizer = FormatOptimizer()
        except ImportError:
            optimizer = None

        # Handle ZIP extraction if needed
        working_folder, is_temp = self.file_ops.extract_zip_if_needed(input_path)
        if working_folder is None:
            print("❌ Failed to process input. Please check the file/folder path.")
            return

        try:
            # Create organized output structure
            project_output_dir = self.file_ops.create_output_structure(
                input_path, self.config.DEFAULT_OUTPUT_DIR, is_temp
            )

            # Get all image files from directory (including subdirectories)
            image_files = self.file_ops.get_image_files_from_directory(working_folder)

            if not image_files:
                print("❌ No image files found in the input!")
                return

            print(f"📁 Found {len(image_files)} image files to process")

            # Analyze formats in the batch if optimizer is available
            if optimizer is not None:
                file_paths = [full_path for full_path, _ in image_files]
                format_counts = {"raw": 0, "jpeg": 0, "unknown": 0}
                for file_path in file_paths:
                    format_type = optimizer.detect_file_format(file_path)
                    format_counts[format_type] += 1

                if format_counts["raw"] > 0 or format_counts["jpeg"] > 0:
                    print(
                        f"📊 Format analysis: {format_counts['raw']} RAW, {format_counts['jpeg']} JPEG, {format_counts['unknown']} other"
                    )
                    if format_counts["raw"] > 0 and format_counts["jpeg"] > 0:
                        print(
                            "🔄 Mixed formats detected - automatic optimization will choose:"
                        )
                        print(
                            f"   📷 RAW files -> {optimizer.get_optimal_preset('dummy.nef', preset_name)}"
                        )
                        print(
                            f"   🖼️  JPEG files -> {optimizer.get_optimal_preset('dummy.jpg', preset_name)}"
                        )

            for label, total_pixels in self.config.RESOLUTIONS.items():
                output_folder = os.path.join(
                    project_output_dir, f"processed_photos_{label}_{preset_name}"
                )
                os.makedirs(output_folder, exist_ok=True)

                print(
                    f"\nProcessing {label.upper()} images with {preset_name} preset..."
                )

                for idx, (full_path, rel_path) in enumerate(image_files, 1):
                    try:
                        img = self.image_processor.load_image_smart_enhanced(full_path)

                        # Apply EXIF rotation
                        img = self.image_processor.fix_image_orientation(img)

                        # Get format-optimized preset if optimizer is available
                        optimal_preset = (
                            optimizer.get_optimal_preset(full_path, preset_name)
                            if optimizer is not None
                            else preset_name
                        )
                        format_info = (
                            optimizer.get_format_info(full_path)
                            if optimizer is not None
                            else {
                                "filename": os.path.basename(full_path),
                                "format": "unknown",
                            }
                        )

                        # Show format optimization info if different preset was chosen
                        if optimal_preset != preset_name:
                            print(
                                f"   🔄 {format_info['filename']} ({format_info['format'].upper()}) -> using {optimal_preset}"
                            )

                        # Apply Photoshop-style preset
                        enhanced_img, history = (
                            self.image_processor.apply_photoshop_preset(
                                img, optimal_preset
                            )
                        )

                        # Show last 3 adjustments
                        print(
                            f"   📝 {os.path.basename(full_path)}: {', '.join(history[-3:])}"
                        )

                        # Calculate target size maintaining original aspect ratio
                        original_ratio = enhanced_img.width / enhanced_img.height
                        target_width = int((total_pixels * original_ratio) ** 0.5)
                        target_height = int(total_pixels / target_width)
                        target_size = (target_width, target_height)

                        # Resize to exact target size
                        final_img = enhanced_img.resize(
                            target_size, Image.Resampling.LANCZOS
                        )

                        # Add watermark
                        if self.config.ENABLE_WATERMARK:
                            final_img = self.image_processor.add_watermark(
                                final_img,
                                watermark_opacity=self.config.WATERMARK_OPACITY,
                                scale_factor=self.config.WATERMARK_SCALE,
                            )

                        # Save with original filename prefix + mode prefix
                        original_name = os.path.splitext(os.path.basename(full_path))[0]
                        mode_prefix = self.image_processor.get_mode_prefix(preset_name)
                        new_filename = f"{original_name}_{mode_prefix}.jpg"
                        output_path = os.path.join(output_folder, new_filename)
                        final_img.save(output_path, "JPEG", quality=90, optimize=True)

                    except Exception as e:
                        print(
                            f"❌ Failed to process {os.path.basename(full_path)}: {e}"
                        )

                # Create ZIP archive
                zip_path = self.file_ops.create_zip_archive(
                    output_folder, project_output_dir, f"{label}_{preset_name}"
                )
                print(f"✅ Finished {label.upper()} folder zipped at:\n{zip_path}")

        finally:
            # Clean up temporary directory if needed
            if is_temp:
                self.file_ops.cleanup_temp_directory(working_folder)

    def process_with_custom_preset(
        self, input_path: str, custom_preset: Dict[str, float]
    ) -> None:
        """
        Process images with custom user-defined adjustments.
        :param input_path: Path to input images or folder
        :param custom_preset: Dictionary of custom adjustment values
        """
        print("🎨 Starting processing with custom settings...")

        # Handle ZIP extraction if needed
        working_folder, is_temp = self.file_ops.extract_zip_if_needed(input_path)
        if working_folder is None:
            print("❌ Failed to process input. Please check the file/folder path.")
            return

        try:
            # Create organized output structure
            project_output_dir = self.file_ops.create_output_structure(
                input_path, self.config.DEFAULT_OUTPUT_DIR, is_temp
            )

            # Get all image files from directory (including subdirectories)
            image_files = self.file_ops.get_image_files_from_directory(working_folder)

            if not image_files:
                print("❌ No image files found in the input!")
                return

            print(f"📁 Found {len(image_files)} image files to process")

            for label, total_pixels in self.config.RESOLUTIONS.items():
                output_folder = os.path.join(
                    project_output_dir, f"processed_photos_{label}_custom"
                )
                os.makedirs(output_folder, exist_ok=True)

                print(f"\nProcessing {label.upper()} images with custom settings...")

                for idx, (full_path, rel_path) in enumerate(image_files, 1):
                    try:
                        img = self.image_processor.load_image_smart_enhanced(full_path)
                        img = self.image_processor.fix_image_orientation(img)

                        # Apply custom adjustments using a PhotoshopStyleEnhancer-like interface
                        enhancer = self.image_processor.PhotoshopStyleEnhancer(img)

                        # Apply either exposure or brightness (exposure takes priority)
                        if custom_preset.get("exposure", 0) != 0:
                            enhancer.exposure_adjustment(
                                custom_preset.get("exposure", 0)
                            )
                        elif custom_preset.get("brightness", 0) != 0:
                            enhancer.brightness_adjustment(
                                custom_preset.get("brightness", 0)
                            )

                        enhancer.highlights_shadows(
                            highlights=custom_preset.get("highlights", 0),
                            shadows=custom_preset.get("shadows", 0),
                        )
                        enhancer.vibrance_saturation(
                            vibrance=custom_preset.get("vibrance", 0),
                            saturation=custom_preset.get("saturation", 0),
                        )
                        enhancer.clarity_structure(
                            clarity=custom_preset.get("clarity", 0),
                            structure=custom_preset.get("structure", 0),
                        )
                        enhancer.color_temperature(
                            temperature=custom_preset.get("temperature", 0)
                        )
                        enhancer.portrait_enhancements(
                            skin_smoothing=custom_preset.get("skin_smoothing", 0)
                        )

                        enhanced_img = enhancer.get_result()

                        # Resize
                        original_ratio = enhanced_img.width / enhanced_img.height
                        target_width = int((total_pixels * original_ratio) ** 0.5)
                        target_height = int(total_pixels / target_width)
                        target_size = (target_width, target_height)
                        final_img = enhanced_img.resize(
                            target_size, Image.Resampling.LANCZOS
                        )

                        # Add watermark
                        if self.config.ENABLE_WATERMARK:
                            final_img = self.image_processor.add_watermark(
                                final_img,
                                watermark_opacity=self.config.WATERMARK_OPACITY,
                                scale_factor=self.config.WATERMARK_SCALE,
                            )

                        # Save with original filename prefix + mode prefix
                        original_name = os.path.splitext(os.path.basename(full_path))[0]
                        mode_prefix = self.image_processor.get_mode_prefix("custom")
                        new_filename = f"{original_name}_{mode_prefix}.jpg"
                        output_path = os.path.join(output_folder, new_filename)
                        final_img.save(output_path, "JPEG", quality=90, optimize=True)

                    except Exception as e:
                        print(
                            f"❌ Failed to process {os.path.basename(full_path)}: {e}"
                        )

                # Create ZIP archive
                zip_path = self.file_ops.create_zip_archive(
                    output_folder, project_output_dir, f"{label}_custom"
                )
                print(
                    f"✅ Finished {label.upper()} custom folder zipped at:\n{zip_path}"
                )

        finally:
            # Clean up temporary directory if needed
            if is_temp:
                self.file_ops.cleanup_temp_directory(working_folder)

    # Add more methods as needed for extensibility

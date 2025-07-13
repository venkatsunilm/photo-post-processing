"""
CLI entry point for photo post-processing pipeline.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
import argparse
import types

from .pipeline import ImageProcessingPipeline
from pro_photo_processor.config import config
from pro_photo_processor.io import file_operations
from pro_photo_processor.core import image_processing
from pro_photo_processor.utils import get_mode_prefix  # noqa: F401


format_optimizer: types.ModuleType | None
try:
    from pro_photo_processor.presets import format_optimizer
except ImportError:
    format_optimizer = None

# --- Enhanced Logging Setup ---
logger = logging.getLogger("pro_photo_processor.cli")


def setup_logging(
    log_level: Optional[str] = None, log_file: Optional[str] = None
) -> None:
    """
    Set up logging with both console and rotating file handler.
    Log level can be set via argument, environment variable LOG_LEVEL, or defaults to INFO.
    This function reconfigures the existing logger.
    """
    if logger.hasHandlers():
        for h in logger.handlers[:]:
            logger.removeHandler(h)
    env_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = (log_level or env_level or "INFO").upper()
    level_value = getattr(logging, level, logging.INFO)
    logger.setLevel(level_value)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(level_value)
    logger.addHandler(ch)
    if not log_file:
        log_file = os.path.join(os.getcwd(), "photo_processor.log")
    try:
        fh = RotatingFileHandler(
            log_file, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        fh.setFormatter(formatter)
        fh.setLevel(level_value)
        logger.addHandler(fh)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")


def cli_main() -> None:
    parser = argparse.ArgumentParser(description="Photo Post-Processing Pipeline CLI")
    parser.add_argument(
        "--log-level",
        type=str,
        default=None,
        help="Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Overrides LOG_LEVEL env var.",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to log file (default: ./photo_processor.log)",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List all available enhancement presets and exit.",
    )
    parser.add_argument(
        "--list-presets-format",
        type=str,
        choices=["plain", "table", "json"],
        default="plain",
        help="Format for listing presets: plain, table, or json (default: plain)",
    )
    parser.add_argument(
        "--list-modes",
        action="store_true",
        help="List all available utility processing modes and exit.",
    )
    parser.add_argument(
        "--input",
        dest="input_path",
        type=str,
        default=None,
        help="Path to input image or folder (or ZIP). Default: ./input",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        type=str,
        default=None,
        help="Path to output directory. Default: ./output",
    )
    parser.add_argument(
        "--type",
        type=str,
        required=False,
        help="Processing type: either a preset name (e.g. portrait_subtle, sports_action) for enhancement, or a utility mode (resize_only, resize_watermark, watermark). Only one is allowed. If not provided, an interactive menu will be shown.",
    )
    parser.add_argument(
        "--custom",
        type=str,
        default=None,
        help="Custom preset as JSON string (optional)",
    )
    args = parser.parse_args()
    setup_logging(log_level=args.log_level, log_file=args.log_file)
    presets = [
        "portrait_subtle",
        "portrait_natural",
        "portrait_dramatic",
        "studio_portrait",
        "overexposed_recovery",
        "natural_wildlife",
        "sports_action",
        "enhanced_mode",
    ]
    utility_modes = ["resize_only", "resize_watermark", "watermark"]
    if args.list_presets:
        preset_descriptions = {
            "portrait_subtle": "Subtle portrait enhancement",
            "portrait_natural": "Natural look for portraits",
            "portrait_dramatic": "Dramatic lighting for portraits",
            "studio_portrait": "Studio-style portrait finish",
            "overexposed_recovery": "Recover details from overexposed images",
            "natural_wildlife": "Enhance wildlife/nature shots",
            "sports_action": "Sharpen and brighten action shots",
            "enhanced_mode": "General enhancement for all photos",
        }
        if args.list_presets_format == "json":
            import json

            logger.info(
                json.dumps(
                    [
                        {"name": k, "description": v}
                        for k, v in preset_descriptions.items()
                    ],
                    indent=2,
                )
            )
        elif args.list_presets_format == "table":
            try:
                from tabulate import tabulate

                table = [(k, v) for k, v in preset_descriptions.items()]
                logger.info("\n" + tabulate(table, headers=["Preset", "Description"]))
            except ImportError:
                logger.info("\nPreset               | Description")
                logger.info(
                    "---------------------|------------------------------------------"
                )
                for k, v in preset_descriptions.items():
                    logger.info(f"{k:<20} | {v}")
        else:
            logger.info("Available enhancement presets:")
            for k, v in preset_descriptions.items():
                logger.info(f"  - {k}: {v}")
        sys.exit(0)
    if args.list_modes:
        logger.info("Available utility processing modes:")
        for m in utility_modes:
            logger.info(f"  - {m}")
        sys.exit(0)
    input_path = args.input_path or getattr(
        config,
        "DEFAULT_INPUT_PATH",
        os.path.abspath(os.path.join(os.getcwd(), "input")),
    )
    output_path = args.output_path or getattr(
        config,
        "DEFAULT_OUTPUT_DIR",
        os.path.abspath(os.path.join(os.getcwd(), "output")),
    )
    logger.info(f"📥 Input path: {input_path}")
    logger.info(f"📤 Output path: {output_path}")
    logger.info(
        f"📝 Log file: {args.log_file or os.path.join(os.getcwd(), 'photo_processor.log')}"
    )
    preset_manager = format_optimizer if format_optimizer is not None else None
    config.DEFAULT_OUTPUT_DIR = output_path
    if not args.log_file and output_path:
        log_path = os.path.join(output_path, "photo_processor.log")
        for h in logger.handlers:
            if isinstance(h, RotatingFileHandler):
                try:
                    h.baseFilename = log_path
                except Exception:
                    pass
    pipeline = ImageProcessingPipeline(
        config=config,
        file_ops=file_operations,
        image_processor=image_processing,
        preset_manager=preset_manager,
    )
    selected_type = args.type
    if not selected_type:
        logger.info("\nSelect a processing type:")
        options = presets + utility_modes
        preset_descriptions = {
            "portrait_subtle": "Subtle portrait enhancement",
            "portrait_natural": "Natural look for portraits",
            "portrait_dramatic": "Dramatic lighting for portraits",
            "studio_portrait": "Studio-style portrait finish",
            "overexposed_recovery": "Recover details from overexposed images",
            "natural_wildlife": "Enhance wildlife/nature shots",
            "sports_action": "Sharpen and brighten action shots",
            "enhanced_mode": "General enhancement for all photos",
        }
        utility_descriptions = {
            "resize_only": "Resize to target resolutions only",
            "resize_watermark": "Resize and add watermark",
            "watermark": "Add watermark only",
        }
        menu_table = []
        for idx, name in enumerate(options, 1):
            if name in preset_descriptions:
                desc = preset_descriptions[name]
                kind = "Preset"
            else:
                desc = utility_descriptions.get(name, "Utility mode")
                kind = "Utility"
            menu_table.append((idx, name, kind, desc))
        try:
            from tabulate import tabulate

            logger.info(
                "\n"
                + tabulate(menu_table, headers=["No.", "Name", "Type", "Description"])
            )
        except ImportError:
            logger.info(f"{'No.':<4} {'Name':<20} {'Type':<10} Description")
            logger.info(f"{'-' * 4} {'-' * 20} {'-' * 10} {'-' * 40}")
            for row in menu_table:
                logger.info(f"{row[0]:<4} {row[1]:<20} {row[2]:<10} {row[3]}")
        max_attempts = 3
        attempts = 0
        while attempts < max_attempts:
            try:
                choice = int(input("Enter a number: ").strip())
                if 1 <= choice <= len(options):
                    selected_type = options[choice - 1]
                    logger.info(f"Selected processing type: {selected_type}")
                    break
                else:
                    logger.warning(
                        f"Please enter a number between 1 and {len(options)}."
                    )
                    print(f"Please enter a number between 1 and {len(options)}.")
            except ValueError:
                logger.warning("Invalid input. Please enter a number.")
                print("Invalid input. Please enter a number.")
            attempts += 1
        else:
            logger.error("Too many invalid attempts. Exiting.")
            print("Too many invalid attempts. Exiting.")
            sys.exit(2)
    if args.custom:
        import json

        try:
            custom_preset = json.loads(args.custom)
            if not isinstance(custom_preset, dict):
                raise ValueError("Custom preset must be a JSON object.")
        except Exception as e:
            logger.error(f"❌ Invalid custom preset JSON: {e}")
            sys.exit(1)
        pipeline.process_with_custom_preset(input_path, custom_preset)
    elif selected_type in utility_modes:
        pipeline.process_images(input_path, mode=selected_type)
    else:
        pipeline.process_with_preset(input_path, selected_type)


if __name__ == "__main__":
    cli_main()

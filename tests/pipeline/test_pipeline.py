import tempfile
from pro_photo_processor.pipeline import ImageProcessingPipeline
from pro_photo_processor.config import config
from pro_photo_processor.io import file_operations
from pro_photo_processor.core import image_processing


def test_pipeline_init():
    pipeline = ImageProcessingPipeline(
        config=config,
        file_ops=file_operations,
        image_processor=image_processing,
        preset_manager=None,
    )
    assert pipeline.config is config
    assert pipeline.file_ops is file_operations
    assert pipeline.image_processor is image_processing


def test_process_images_empty(monkeypatch):
    # NOTE: Minimal test for coverage. Full tests with real files will be added later.
    pipeline = ImageProcessingPipeline(config, file_operations, image_processing)
    # Patch file_ops.extract_zip_if_needed to return a temp dir and False
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr(
            file_operations, "extract_zip_if_needed", lambda path: (tmpdir, False)
        )
        monkeypatch.setattr(
            file_operations, "create_output_structure", lambda *a, **kw: tmpdir
        )
        monkeypatch.setattr(
            file_operations, "get_image_files_from_directory", lambda d: []
        )
        pipeline.process_images("fake_input", mode="resize_only")

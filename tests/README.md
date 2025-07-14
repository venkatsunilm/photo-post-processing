tests/
# Photo Post-Processing Test Suite

This directory contains all tests for the Photo Post-Processing Pipeline. Tests are written with [pytest](https://docs.pytest.org/en/stable/) and are designed for reproducibility, coverage, and quality.

---


## 📁 Directory Structure & Temporary Files

```
tests/
├── __init__.py
├── conftest.py
├── run_tests.py                # (legacy/manual runner, use pytest preferred)
├── format_comparison/
│   ├── test_optimizer.py
│   ├── integration_test.py
│   └── ...
├── image_processing/
│   ├── test_quality_impact.py
│   └── ...
├── preset_analysis/
│   ├── compare_presets.py
│   └── ...
├── raw_processing/
│   ├── test_raw_quality.py
│   └── ...
├── test_brightness_method.py
├── test_copy_or_cut_files.py
├── test_enhanced_raw.py
├── test_mode_12_fixes.py
├── test_rawpy_compatibility.py
├── test_resize_only.py
├── test_sports_fix.py
└── ...
```

---


> **Note:**
> - All tests use temporary files and directories, and monkeypatching, to avoid real file system or OS side effects. All temp files/dirs are cleaned up automatically.
> - Folders like `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.venv`, and `htmlcov` are auto-generated and can be ignored or cleaned with `make clean`.

### Run All Tests (Recommended)

```sh
uv run pytest
```

### Run Tests with Coverage

```sh
uv run pytest --cov=src --cov-report=term-missing
```

### Run a Specific Test Module

```sh
uv run pytest tests/image_processing/test_quality_impact.py
```

---


## 🧪 Test Types & Best Practices

- **Unit tests:** Test individual functions and modules
- **Integration tests:** Test end-to-end processing and pipeline logic
- **Performance tests:** Benchmark processing speed and memory usage
- **Quality tests:** Validate before/after image quality and metrics
- **Preset analysis:** Compare and recommend enhancement presets

---


## 📝 Usage Notes & Adding New Tests

- All new tests should use pytest fixtures and monkeypatching to ensure they are robust and portable.
- Keep tests side-effect free and clean up all temp files/dirs.

- All tests use sample images from the configured input directory
- Tests are read-only and do not modify original files
- RAW file tests may take longer due to file size
- All output is printed to the console for analysis

---

## 🐛 Troubleshooting

- **No test files found:** Ensure images are in the input directory
- **Import errors:** Run tests from the project root or `tests/` directory
- **RAW processing fails:** Check `rawpy` installation
- **Performance issues:** Test with a smaller image set first

---

## � Requirements

- All tests use the main project dependencies (see `pyproject.toml`):
  - Pillow (PIL)
  - rawpy
  - numpy
  - pytest
  - tqdm, colorama, etc.

---

## 🎯 Recommended Test Workflow

1. Run all tests: `uv run pytest`
2. Check coverage: `uv run pytest --cov=src --cov-report=term-missing`
3. Run specific tests for new features or bugfixes
4. Review console output for quality and performance metrics

---

## 📈 Output

- ✅ Success/failure indicators
- 📊 Performance and quality metrics
- � Preset recommendations
- 📈 Statistical analysis

---

## 🤝 Contributing Tests

- Add new tests in the appropriate subfolder
- Use descriptive names and docstrings
- Ensure all tests pass and coverage is maintained
- Follow project best practices (see `../docs/best_practices_guide.md`)

# Photo Post-Processing Pipeline

A professional, reproducible Python image processing pipeline with robust RAW support, modern development workflow, and built-in CI/CD, linting, type checking, and security.

---

## Features

- **Image Processing:** RAW, JPEG, and other formats using Pillow, OpenCV, and RawPy
- **Modern Python Tooling:**
  - Linting & formatting: [Ruff](https://pypi.org/project/ruff/)
  - Type checking: [mypy](https://pypi.org/project/mypy/)
  - Security: [bandit](https://pypi.org/project/bandit/), [safety](https://pypi.org/project/safety/)
  - Testing: [pytest](https://pypi.org/project/pytest/), [pytest-cov](https://pypi.org/project/pytest-cov/)
  - Pre-commit hooks: [pre-commit](https://pre-commit.com/)
- **CI/CD:** Automated with GitHub Actions (multi-version, coverage, security, artifact upload)
- **Reproducible Environments:** All dependencies pinned in pyproject.toml, managed with [uv](https://github.com/astral-sh/uv)
- **Clean Project Structure:**
  - Source: src
  - Tests: tests
  - Docs: docs
  - All config in pyproject.toml

---

## Quickstart

### 1. Clone and Install

```sh
git clone <your-repo-url>
cd photo-post-processing
uv sync --all-extras
```

### 2. Set Up Pre-commit Hooks

```sh
uv run pre-commit install
```

### 3. Run the Pipeline

```sh
uv run python src/process_photos.py
```

---

## Development Workflow

- **Lint:**
  `uv run ruff check src tests`
- **Format:**
  `uv run ruff format src tests`
- **Type Check:**
  `uv run mypy src`
- **Test:**
  `uv run pytest`
- **Test with Coverage:**
  `uv run pytest --cov=src --cov-report=term-missing`
- **Security:**
  `uv run bandit -r src/ -c .bandit -f json -o bandit-report.json`
  `uv run safety check --output json > safety-report.json`
- **Pre-commit (all files):**
  `uv run pre-commit run --all-files`

Or use the provided Makefile for common tasks:

```sh
make lint
make format
make test
make run
make test-cov
make setup-dev
make clean
```

---

## Continuous Integration

- **GitHub Actions** runs on every push and PR:
  - Lint, format, type check, test (with coverage)
  - Security checks (bandit, safety)
  - Uploads coverage and security reports as artifacts

---

## Project Structure

```
src/                # Main source code
tests/              # All tests and fixtures
docs/               # Documentation and guides
pyproject.toml      # All dependencies and tool config
.pre-commit-config.yaml
Makefile
.github/workflows/  # CI/CD pipeline
```

---

## Dependencies

All dependencies are pinned for reproducibility.
See pyproject.toml for exact versions.

- **Core:** pillow, opencv-python, rawpy, numpy, tqdm, colorama, psutil
- **Dev:** pytest, pytest-cov, ruff, mypy, pre-commit, bandit, safety

---

## Contributing

1. Fork and clone the repo
2. Install dev dependencies: `uv sync --all-extras`
3. Set up pre-commit: `uv run pre-commit install`
4. Use the `uv` commands above for linting, testing, etc.
   - (Optional) If you have `make` installed, you can use the provided Makefile for common tasks.
5. Open a PR with your changes

---

## License

MIT

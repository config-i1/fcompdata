# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Forecasting Competitions Datasets (fcompdata) - a Python library for loading M-Competition time series datasets (M1, M3, M4, Tourism) with an interface similar to R's Mcomp package.

## Commands

```bash
# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/

# Run type checker
mypy src/
```

## Testing workflow

Before reporting any code change as complete, run all three checks and make sure they pass:

```bash
ruff check src/   # `ruff check --fix src/` to auto-fix import order etc.
pytest            # must be 100% green
mypy src/         # currently clean — keep it that way
```

CI (`.github/workflows/python-package.yml`) only runs ruff + pytest, but mypy is also expected to be clean.

If a system Python doesn't have the dev tools, use a local venv: `python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"`, then run the binaries via `.venv/bin/ruff` etc.

## Architecture

```
src/fcompdata/
├── __init__.py      # Public API exports
├── fcompdata.py     # Core module with loaders and classes
├── download.py      # Download utilities for large datasets (M4)
└── data/            # JSON data files (bundled)
    ├── m1_data.json
    ├── m3_data.json
    └── tcomp_data.json
```

**Core classes** (`src/fcompdata/fcompdata.py`):
- `MCompSeries`: Single time series with `x` (train), `xx` (test), `h` (horizon), `period`, `type`, `description`
- `MCompDataset`: Container with dict-like access, supports `subset(series_type)` filtering
- `_LazyDataset`: Lazy-loading wrapper for module-level datasets

**Public API** (`from fcompdata import ...`):
- `M1`, `M3`, `M4`, `Tourism`: Lazy-loaded dataset instances
- `load_m1()`, `load_m3()`, `load_m4()`, `load_tourism()`: Explicit loader functions
- `MCompSeries`, `MCompDataset`: Classes for type hints

**Download module** (`from fcompdata.download import ...`):
- `download_m4(frequency=None)`: Download M4 data from Zenodo to ~/.fcompdata/
- `get_data_home()`: Get path to cache directory
- `get_m4_path(frequency)`: Get path to cached M4 file
- `clear_cache()`: Clear downloaded data

**Key design decisions**:
- 1-based indexing (R compatibility): `M3[1]` returns first series
- Dictionary-style attribute access: `series['x']` and `series.x` both work
- Lazy loading via `_LazyDataset`: Data only parses on first access
- Uses `importlib.resources` for package data access
- M4 (100k series) downloaded separately to keep package size small

## M4 Dataset

M4 requires downloading before use (~50MB total):
```python
from fcompdata.download import download_m4
download_m4()  # Downloads all frequencies to ~/.fcompdata/m4/
download_m4('yearly')  # Download only yearly

from fcompdata import M4, load_m4
series = M4[1]
yearly = load_m4('yearly')
```

M4 frequencies: yearly (23k), quarterly (24k), monthly (48k), weekly (359), daily (4227), hourly (414)

## Dependencies

- `numpy>=1.20` (runtime)
- `pytest`, `ruff`, `mypy` (dev)

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python library for loading M-Competition time series datasets (M1, M3, Tourism) with an interface similar to R's Mcomp package.

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

## Architecture

```
src/mcomp/
├── __init__.py      # Public API exports
├── mcomp.py         # Core module (~290 lines)
└── data/            # JSON data files
    ├── m1_data.json
    ├── m3_data.json
    └── tcomp_data.json
```

**Core classes** (`src/mcomp/mcomp.py`):
- `MCompSeries`: Single time series with `x` (train), `xx` (test), `h` (horizon), `period`, `type`, `description`
- `MCompDataset`: Container with dict-like access, supports `subset(series_type)` filtering
- `_LazyDataset`: Lazy-loading wrapper for module-level datasets

**Public API** (`from mcomp import ...`):
- `M1`, `M3`, `Tourism`: Lazy-loaded dataset instances
- `load_m1()`, `load_m3()`, `load_tourism()`: Explicit loader functions
- `MCompSeries`, `MCompDataset`: Classes for type hints

**Key design decisions**:
- 1-based indexing (R compatibility): `M3[1]` returns first series
- Dictionary-style attribute access: `series['x']` and `series.x` both work
- Lazy loading via `_LazyDataset`: Data only parses on first access
- Uses `importlib.resources` for package data access

## Dependencies

- `numpy>=1.20` (runtime)
- `pytest`, `ruff`, `mypy` (dev)

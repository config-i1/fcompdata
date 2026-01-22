"""
M-Competition time series datasets.

This package provides access to historical time series forecasting competition
datasets (M1, M3, Tourism) with an interface similar to R's Mcomp package.

Usage
-----
>>> from mcomp import M1, M3, Tourism
>>>
>>> # Access series by 1-based index (R-style)
>>> series = M3[1]
>>> print(series['x'])   # Training data
>>> print(series['xx'])  # Test data
>>> print(series['h'])   # Forecast horizon
>>>
>>> # Filter by type
>>> yearly = M3.subset('yearly')
>>> monthly = M1.subset('monthly')

Datasets
--------
M1 : MCompDataset
    M1 competition (1001 series)
M3 : MCompDataset
    M3 competition (3003 series)
Tourism : MCompDataset
    Tourism competition (1311 series)
"""

from mcomp.mcomp import (
    M1,
    M3,
    MCompDataset,
    MCompSeries,
    Tourism,
    load_m1,
    load_m3,
    load_tourism,
)

__all__ = [
    "M1",
    "M3",
    "Tourism",
    "MCompDataset",
    "MCompSeries",
    "load_m1",
    "load_m3",
    "load_tourism",
]

__version__ = "0.1.0"

"""
Forecasting Competitions Datasets.

This package provides access to historical time series forecasting competition
datasets (M1, M3, M4, Tourism) and several classic individual series
(AirPassengers, BJsales, Seatbelts, taylor) with an interface similar to R's
Mcomp package.

Usage
-----
>>> from fcompdata import M1, M3, Tourism
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

>>> # M4 requires downloading first (100k series, ~50MB)
>>> from fcompdata.download import download_m4
>>> download_m4()  # One-time download to ~/.fcompdata/
>>> from fcompdata import M4
>>> series = M4[1]

>>> # Individual classic series (bundled, no download required)
>>> from fcompdata import AirPassengers, BJsales, Seatbelts, taylor
>>> AirPassengers.x        # 132 training observations
>>> BJsales.xreg.dtype.names    # ('BJsales.lead',)
>>> Seatbelts.xreg.dtype.names  # ('kms', 'PetrolPrice', 'law')

Datasets
--------
M1 : MCompDataset
    M1 competition (1001 series)
M3 : MCompDataset
    M3 competition (3003 series)
M4 : MCompDataset
    M4 competition (100000 series) - requires download_m4() first
Tourism : MCompDataset
    Tourism competition (1311 series)
AirPassengers, BJsales, Seatbelts, taylor : MCompSeries
    Classic individual time series ported from R.
PromoData : MCompSeries
    Weekly promotional sales (CMAF Demand Forecasting course workshop).
"""

from importlib.metadata import PackageNotFoundError, version as _version

from fcompdata.fcompdata import (
    M1,
    M3,
    M4,
    AirPassengers,
    BJsales,
    MCompDataset,
    MCompSeries,
    PromoData,
    Seatbelts,
    Tourism,
    load_individual,
    load_m1,
    load_m3,
    load_m4,
    load_tourism,
    taylor,
)

__all__ = [
    "M1",
    "M3",
    "M4",
    "Tourism",
    "AirPassengers",
    "BJsales",
    "Seatbelts",
    "taylor",
    "PromoData",
    "MCompDataset",
    "MCompSeries",
    "load_m1",
    "load_m3",
    "load_m4",
    "load_tourism",
    "load_individual",
]

try:
    __version__ = _version("fcompdata")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

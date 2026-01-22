"""
M-Competition datasets loader.

Loads M1, M3, and Tourism competition datasets from local JSON files,
providing an interface similar to R's Mcomp package.

Usage:
    from competitions import M1, M3, Tourism

    # Access series by index (1-based, like R)
    series = M3[2568]
    print(series['x'])   # Training data
    print(series['xx'])  # Test data
    print(series['h'])   # Forecast horizon

    # Filter by type
    yearly = M3.subset('yearly')
"""
from __future__ import annotations

import json
from importlib import resources
from typing import Any, Iterator

import numpy as np
from numpy.typing import NDArray


class MCompSeries:
    """
    A single M-competition time series.

    Attributes
    ----------
    sn : str
        Series name/identifier
    x : NDArray
        Training data (in-sample)
    xx : NDArray
        Test data (out-of-sample)
    h : int
        Forecast horizon
    period : int
        Seasonal period (1=yearly, 4=quarterly, 12=monthly)
    type : str
        Series type (yearly, quarterly, monthly, other)
    n : int
        Length of training data
    description : str
        Series description
    """

    __slots__ = ("sn", "x", "xx", "h", "period", "type", "n", "description")

    def __init__(
        self,
        sn: str,
        x: NDArray,
        xx: NDArray,
        h: int,
        period: int,
        series_type: str,
        description: str = "",
    ) -> None:
        self.sn = sn
        self.x = x
        self.xx = xx
        self.h = h
        self.period = period
        self.type = series_type
        self.n = len(x)
        self.description = description

    def __repr__(self) -> str:
        return f"MCompSeries(sn='{self.sn}', n={self.n}, h={self.h}, type='{self.type}')"

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access for R-like interface."""
        return getattr(self, key)

    def keys(self) -> list[str]:
        """Return available keys."""
        return ["sn", "x", "xx", "h", "period", "type", "n", "description"]


class MCompDataset:
    """
    M-competition dataset container.

    Provides dictionary-like access to series, supporting 1-based indexing
    (like R's Mcomp package).

    Examples
    --------
    >>> from competitions import M3
    >>> series = M3[2568]  # 1-based index (R-style)
    >>> print(series['x'])  # Training data
    """

    def __init__(self, series_dict: dict[int, MCompSeries], name: str = "M") -> None:
        self._series = series_dict
        self._name = name
        self._keys_sorted = sorted(series_dict.keys())

    def __getitem__(self, key: int) -> MCompSeries:
        """
        Get series by 1-based index (R-style).

        Parameters
        ----------
        key : int
            1-based series index

        Returns
        -------
        MCompSeries
            The requested time series
        """
        if key in self._series:
            return self._series[key]
        raise KeyError(f"Series {key} not found in {self._name} dataset")

    def __len__(self) -> int:
        return len(self._series)

    def __iter__(self) -> Iterator[MCompSeries]:
        for key in self._keys_sorted:
            yield self._series[key]

    def __repr__(self) -> str:
        return f"{self._name} Dataset: {len(self)} series"

    def keys(self) -> list[int]:
        """Return all series indices."""
        return self._keys_sorted

    def items(self) -> Iterator[tuple[int, MCompSeries]]:
        """Iterate over (index, series) pairs."""
        for key in self._keys_sorted:
            yield key, self._series[key]

    def subset(self, series_type: str) -> MCompDataset:
        """
        Get subset of series by type.

        Parameters
        ----------
        series_type : str
            One of 'yearly', 'quarterly', 'monthly', 'other'

        Returns
        -------
        MCompDataset
            Subset containing only series of specified type
        """
        filtered = {k: v for k, v in self._series.items() if v.type == series_type}
        return MCompDataset(filtered, f"{self._name}_{series_type}")


def _parse_period(period_str: str) -> int:
    """Convert period string to numeric value."""
    period_map = {
        "YEARLY": 1,
        "QUARTERLY": 4,
        "MONTHLY": 12,
        "OTHER": 1,
    }
    return period_map.get(period_str.upper(), 1)


def _parse_series_type(period_str: str) -> str:
    """Convert period string to series type."""
    return period_str.lower()


def _load_json_dataset(filename: str, name: str) -> MCompDataset:
    """
    Load competition dataset from JSON file.

    Parameters
    ----------
    filename : str
        Name of JSON file in data directory
    name : str
        Dataset name (M1, M3, Tourism)

    Returns
    -------
    MCompDataset
        Loaded dataset
    """
    data_files = resources.files("competitions.data")
    with resources.as_file(data_files.joinpath(filename)) as filepath:
        with open(filepath, "r") as f:
            data = json.load(f)

    series_dict = {}
    for idx, (key, item) in enumerate(data.items(), start=1):
        # Extract values - JSON from R has single-element lists for scalars
        sn = item["sn"][0] if isinstance(item["sn"], list) else item["sn"]
        h = item["h"][0] if isinstance(item["h"], list) else item["h"]
        period_str = item["period"][0] if isinstance(item["period"], list) else item["period"]
        type_str = item.get("type", [period_str])
        type_str = type_str[0] if isinstance(type_str, list) else type_str
        description = item.get("description", [""])
        description = description[0] if isinstance(description, list) else description

        # Training and test data are regular arrays
        x = np.array(item["x"])
        xx = np.array(item["xx"])

        series_dict[idx] = MCompSeries(
            sn=sn,
            x=x,
            xx=xx,
            h=int(h),
            period=_parse_period(period_str),
            series_type=_parse_series_type(period_str),
            description=description,
        )

    return MCompDataset(series_dict, name)


def load_m3() -> MCompDataset:
    """
    Load M3 competition dataset.

    Returns
    -------
    MCompDataset
        M3 dataset with 3003 series (645 yearly, 756 quarterly,
        1428 monthly, 174 other)

    Examples
    --------
    >>> from competitions import load_m3
    >>> M3 = load_m3()
    >>> series = M3[2568]
    >>> print(f"Training length: {len(series['x'])}")
    """
    return _load_json_dataset("m3_data.json", "M3")


def load_m1() -> MCompDataset:
    """
    Load M1 competition dataset.

    Returns
    -------
    MCompDataset
        M1 dataset with 1001 series (181 yearly, 203 quarterly, 617 monthly)

    Examples
    --------
    >>> from competitions import load_m1
    >>> M1 = load_m1()
    >>> series = M1[1]
    >>> print(f"Training length: {len(series['x'])}")
    """
    return _load_json_dataset("m1_data.json", "M1")


def load_tourism() -> MCompDataset:
    """
    Load Tourism competition dataset.

    Returns
    -------
    MCompDataset
        Tourism dataset with 1311 series (518 yearly, 427 quarterly, 366 monthly)

    Examples
    --------
    >>> from competitions import load_tourism
    >>> Tourism = load_tourism()
    >>> series = Tourism[1]
    >>> print(f"Training length: {len(series['x'])}")
    """
    return _load_json_dataset("tcomp_data.json", "Tourism")


class _LazyDataset:
    """Lazy-loading wrapper for M-competition datasets."""

    def __init__(self, loader: callable, name: str) -> None:
        self._loader = loader
        self._data: MCompDataset | None = None
        self._name = name

    def _ensure_loaded(self) -> None:
        if self._data is None:
            self._data = self._loader()

    def __getitem__(self, key: int) -> MCompSeries:
        self._ensure_loaded()
        return self._data[key]

    def __len__(self) -> int:
        self._ensure_loaded()
        return len(self._data)

    def __iter__(self) -> Iterator[MCompSeries]:
        self._ensure_loaded()
        return iter(self._data)

    def __repr__(self) -> str:
        if self._data is None:
            return f"{self._name} Dataset (not loaded yet - access any series to load)"
        return repr(self._data)

    def keys(self) -> list[int]:
        self._ensure_loaded()
        return self._data.keys()

    def items(self) -> Iterator[tuple[int, MCompSeries]]:
        self._ensure_loaded()
        return self._data.items()

    def subset(self, series_type: str) -> MCompDataset:
        self._ensure_loaded()
        return self._data.subset(series_type)


# Module-level lazy datasets for convenient access
M1 = _LazyDataset(load_m1, "M1")
M3 = _LazyDataset(load_m3, "M3")
Tourism = _LazyDataset(load_tourism, "Tourism")

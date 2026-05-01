"""
Forecasting Competitions Datasets loader.

Loads M1, M3, M4, and Tourism competition datasets,
providing an interface similar to R's Mcomp package.

Usage:
    from fcompdata import M1, M3, M4, Tourism

    # Access series by index (1-based, like R)
    series = M3[2568]
    print(series['x'])   # Training data
    print(series['xx'])  # Test data
    print(series['h'])   # Forecast horizon

    # Filter by type
    yearly = M3.subset('yearly')

    # M4 requires downloading first (100k series)
    from fcompdata.download import download_m4
    download_m4()  # Downloads to ~/.fcompdata/
    from fcompdata import M4
    series = M4[1]
"""
from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from importlib import resources
from pathlib import Path
from typing import Any, cast

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
    y : NDArray
        Full series, equal to ``np.concatenate([x, xx])`` (length ``n + h``).
        Read-only property, computed on access.
    h : int
        Forecast horizon
    period : int
        Seasonal period (1=yearly, 4=quarterly, 12=monthly, 336=half-hourly)
    type : str
        Series type (yearly, quarterly, monthly, halfhourly, other)
    n : int
        Length of training data
    description : str
        Series description
    xreg : numpy.recarray | None
        Exogenous regressors as a structured array of length ``n + h`` with
        named fields equal to the column names. ``None`` if the series has
        no regressors. Equal to the row-wise concatenation of ``xregx`` and
        ``xregxx``.
    xregx : numpy.recarray | None
        Training portion of ``xreg`` (first ``n`` rows). ``None`` if absent.
    xregxx : numpy.recarray | None
        Holdout portion of ``xreg`` (last ``h`` rows). ``None`` if absent.
    """

    __slots__ = (
        "sn", "x", "xx", "h", "period", "type", "n", "description",
        "xreg", "xregx", "xregxx",
    )

    def __init__(
        self,
        sn: str,
        x: NDArray[Any],
        xx: NDArray[Any],
        h: int,
        period: int,
        series_type: str,
        description: str = "",
        xreg: np.recarray | None = None,
        xregx: np.recarray | None = None,
        xregxx: np.recarray | None = None,
    ) -> None:
        self.sn = sn
        self.x = x
        self.xx = xx
        self.h = h
        self.period = period
        self.type = series_type
        self.n = len(x)
        self.description = description
        self.xreg = xreg
        self.xregx = xregx
        self.xregxx = xregxx

    @property
    def y(self) -> NDArray[Any]:
        """Full series: row-wise concatenation of ``x`` (training) and ``xx`` (holdout).

        Computed on each access from the current ``x`` / ``xx``; not stored.
        Length equals ``n + h``.
        """
        return np.concatenate([self.x, self.xx])

    def __repr__(self) -> str:
        return f"MCompSeries(sn='{self.sn}', n={self.n}, h={self.h}, type='{self.type}')"

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access for R-like interface."""
        return getattr(self, key)

    def keys(self) -> list[str]:
        """Return available keys."""
        return [
            "sn", "x", "xx", "y", "h", "period", "type", "n", "description",
            "xreg", "xregx", "xregxx",
        ]


class MCompDataset:
    """
    M-competition dataset container.

    Provides dictionary-like access to series, supporting 1-based indexing
    (like R's Mcomp package).

    Examples
    --------
    >>> from fcompdata import M3
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
        "WEEKLY": 1,
        "DAILY": 1,
        "HOURLY": 1,
        "HALFHOURLY": 336,
        "OTHER": 1,
    }
    return period_map.get(period_str.upper(), 1)


def _parse_xreg(xreg_block: dict[str, Any]) -> np.recarray:
    """Build a numpy structured array (recarray) from a JSON xreg block.

    Expected schema: ``{"names": [...], "values": [[row], ...]}`` (row-major).
    Field names are preserved verbatim so that R column names like
    ``"BJsales.lead"`` survive the trip into Python.
    """
    names = list(xreg_block["names"])
    values = xreg_block["values"]
    dtype = np.dtype([(name, np.float64) for name in names])
    records = [tuple(float(v) for v in row) for row in values]
    return np.array(records, dtype=dtype).view(np.recarray)


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
    data_files = resources.files("fcompdata.data")
    with resources.as_file(data_files.joinpath(filename)) as filepath:
        with open(filepath) as f:
            data = json.load(f)

    series_dict = {}
    for idx, (_key, item) in enumerate(data.items(), start=1):
        # Extract values - JSON from R has single-element lists for scalars
        sn = item["sn"][0] if isinstance(item["sn"], list) else item["sn"]
        h = item["h"][0] if isinstance(item["h"], list) else item["h"]
        period_raw = item["period"][0] if isinstance(item["period"], list) else item["period"]
        if isinstance(period_raw, str):
            # Legacy schema (M1/M3/Tourism): period is a string code; the
            # competition's `type` field stores the category (DEMOGR, MICRO,
            # ...) and is unrelated to the frequency type, which we derive
            # from the period string itself.
            period_int = _parse_period(period_raw)
            type_str = _parse_series_type(period_raw)
        else:
            # Numeric period (used by the individual series): the JSON
            # `type` field carries the frequency label (e.g. "weekly").
            period_int = int(period_raw)
            type_raw = item.get("type", ["other"])
            type_str = type_raw[0] if isinstance(type_raw, list) else type_raw
        description = item.get("description", [""])
        description = description[0] if isinstance(description, list) else description

        # Training and test data are regular arrays
        x = np.array(item["x"])
        xx = np.array(item["xx"])

        # Optional exogenous regressors; preserved as a numpy recarray so that
        # R column names survive (e.g. Seatbelts: kms / PetrolPrice / law).
        xreg: np.recarray | None = None
        xregx: np.recarray | None = None
        xregxx: np.recarray | None = None
        if "xreg" in item and item["xreg"] is not None:
            xreg = _parse_xreg(item["xreg"])
            n_train = len(x)
            h_int = int(h)
            # numpy's type stubs widen recarray slices to ndarray, but at
            # runtime slicing a recarray preserves the recarray type.
            xregx = cast(np.recarray, xreg[:n_train])
            xregxx = cast(np.recarray, xreg[-h_int:])

        series_dict[idx] = MCompSeries(
            sn=sn,
            x=x,
            xx=xx,
            h=int(h),
            period=period_int,
            series_type=type_str,
            description=description,
            xreg=xreg,
            xregx=xregx,
            xregxx=xregxx,
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
    >>> from fcompdata import load_m3
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
    >>> from fcompdata import load_m1
    >>> M1 = load_m1()
    >>> series = M1[1]
    >>> print(f"Training length: {len(series['x'])}")
    """
    return _load_json_dataset("m1_data.json", "M1")


def load_individual() -> MCompDataset:
    """
    Load classic individual time series bundled with the package.

    Returns
    -------
    MCompDataset
        A dataset of four series (1-based indexing):
        ``1=AirPassengers``, ``2=BJsales``, ``3=Seatbelts``, ``4=taylor``.
        ``BJsales`` carries the leading indicator ``BJsales.lead`` as a
        single-column ``xreg``; ``Seatbelts`` uses the ``drivers`` column
        as the response and ``kms``/``PetrolPrice``/``law`` as ``xreg``.

    Examples
    --------
    >>> from fcompdata import load_individual
    >>> ds = load_individual()
    >>> ds[1].sn
    'AirPassengers'
    """
    return _load_json_dataset("individual_data.json", "Individual")


def load_tourism() -> MCompDataset:
    """
    Load Tourism competition dataset.

    Returns
    -------
    MCompDataset
        Tourism dataset with 1311 series (518 yearly, 427 quarterly, 366 monthly)

    Examples
    --------
    >>> from fcompdata import load_tourism
    >>> Tourism = load_tourism()
    >>> series = Tourism[1]
    >>> print(f"Training length: {len(series['x'])}")
    """
    return _load_json_dataset("tcomp_data.json", "Tourism")


def _parse_tsf_file(filepath: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """
    Parse a .tsf format file from Monash Time Series Forecasting Repository.

    Parameters
    ----------
    filepath : Path
        Path to .tsf file

    Returns
    -------
    tuple
        (metadata dict, list of series dicts)
    """
    metadata: dict[str, Any] = {}
    series_list: list[dict[str, Any]] = []
    col_names: list[str] = []
    col_types: list[str] = []

    in_data_section = False

    with open(filepath, encoding="latin-1") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("@"):
                if line.lower().startswith("@data"):
                    in_data_section = True
                    continue

                # Parse metadata
                parts = line.split(maxsplit=2)
                tag = parts[0].lower()

                if tag == "@attribute":
                    # @attribute name type
                    col_names.append(parts[1])
                    col_types.append(parts[2] if len(parts) > 2 else "string")
                elif tag == "@frequency":
                    metadata["frequency"] = parts[1] if len(parts) > 1 else None
                elif tag == "@horizon":
                    metadata["horizon"] = int(parts[1]) if len(parts) > 1 else None
                elif tag == "@missing":
                    metadata["missing"] = parts[1].lower() == "true" if len(parts) > 1 else False
                elif tag == "@equallength":
                    metadata["equallength"] = (
                        parts[1].lower() == "true" if len(parts) > 1 else False
                    )

            elif in_data_section and line:
                # Parse data line: attr1:attr2:...:values
                # Values are comma-separated after the last colon
                # Use maxsplit to handle timestamps that might have special chars
                num_attrs = len(col_names)  # Number of @attribute entries
                parts = line.split(":", maxsplit=num_attrs)

                if len(parts) > num_attrs:
                    series_data: dict[str, Any] = {}
                    for i, name in enumerate(col_names):
                        series_data[name] = parts[i]

                    # Last part contains the comma-separated values
                    values_str = parts[-1]
                    values = []
                    for v in values_str.split(","):
                        v = v.strip()
                        if v and v != "?":
                            values.append(float(v))
                        elif v == "?":
                            values.append(np.nan)
                    series_data["values"] = np.array(values)
                    series_list.append(series_data)

    metadata["col_names"] = col_names
    return metadata, series_list


def _load_tsf_dataset(filepath: Path, name: str, horizon: int, freq_type: str) -> MCompDataset:
    """
    Load competition dataset from .tsf file.

    Parameters
    ----------
    filepath : Path
        Path to .tsf file
    name : str
        Dataset name
    horizon : int
        Forecast horizon (used to split train/test)
    freq_type : str
        Frequency type (yearly, quarterly, etc.)

    Returns
    -------
    MCompDataset
        Loaded dataset
    """
    metadata, series_list = _parse_tsf_file(filepath)

    # Use horizon from metadata if available
    h = metadata.get("horizon", horizon)

    series_dict = {}
    for idx, item in enumerate(series_list, start=1):
        values = item["values"]
        sn = item.get("series_name", f"{name}_{idx}")

        # Split into train (x) and test (xx) based on horizon
        if len(values) > h:
            x = values[:-h]
            xx = values[-h:]
        else:
            # If series is too short, use all for training
            x = values
            xx = np.array([])

        series_dict[idx] = MCompSeries(
            sn=sn,
            x=x,
            xx=xx,
            h=h,
            period=_parse_period(freq_type),
            series_type=freq_type.lower(),
            description="",
        )

    return MCompDataset(series_dict, name)


# M4 horizon values by frequency
M4_HORIZONS = {
    "yearly": 6,
    "quarterly": 8,
    "monthly": 18,
    "weekly": 13,
    "daily": 14,
    "hourly": 48,
}


def load_m4(frequency: str | None = None) -> MCompDataset:
    """
    Load M4 competition dataset.

    The M4 dataset must first be downloaded using `download_m4()`.
    Data is cached in ~/.fcompdata/m4/.

    Parameters
    ----------
    frequency : str, optional
        Specific frequency to load: 'yearly', 'quarterly', 'monthly',
        'weekly', 'daily', or 'hourly'. If None, loads all frequencies
        combined into a single dataset.

    Returns
    -------
    MCompDataset
        M4 dataset. Full dataset has 100,000 series:
        - 23,000 yearly (h=6)
        - 24,000 quarterly (h=8)
        - 48,000 monthly (h=18)
        - 359 weekly (h=13)
        - 4,227 daily (h=14)
        - 414 hourly (h=48)

    Raises
    ------
    FileNotFoundError
        If data hasn't been downloaded yet.

    Examples
    --------
    >>> from fcompdata.download import download_m4
    >>> download_m4()  # Download first (one time)
    >>> from fcompdata import load_m4
    >>> M4 = load_m4()  # Load all frequencies
    >>> yearly = load_m4('yearly')  # Load only yearly
    """
    from fcompdata.download import get_data_home

    m4_dir = get_data_home() / "m4"

    if frequency is not None:
        if frequency not in M4_HORIZONS:
            raise ValueError(
                f"Unknown frequency '{frequency}'. "
                f"Must be one of: {list(M4_HORIZONS.keys())}"
            )
        frequencies = [frequency]
    else:
        frequencies = list(M4_HORIZONS.keys())

    all_series: dict[int, MCompSeries] = {}
    current_idx = 1

    for freq in frequencies:
        filepath = m4_dir / f"m4_{freq}_dataset.tsf"
        if not filepath.exists():
            raise FileNotFoundError(
                f"M4 {freq} data not found at {filepath}. "
                f"Please run: from fcompdata.download import download_m4; download_m4('{freq}')"
            )

        dataset = _load_tsf_dataset(filepath, f"M4_{freq}", M4_HORIZONS[freq], freq)

        # Re-index to maintain continuous 1-based indexing across frequencies
        for series in dataset:
            all_series[current_idx] = series
            current_idx += 1

    name = f"M4_{frequency}" if frequency else "M4"
    return MCompDataset(all_series, name)


class _LazyDataset:
    """Lazy-loading wrapper for M-competition datasets."""

    def __init__(self, loader: Callable[[], MCompDataset], name: str) -> None:
        self._loader = loader
        self._data: MCompDataset | None = None
        self._name = name

    def _ensure_loaded(self) -> MCompDataset:
        if self._data is None:
            self._data = self._loader()
        return self._data

    def __getitem__(self, key: int) -> MCompSeries:
        return self._ensure_loaded()[key]

    def __len__(self) -> int:
        return len(self._ensure_loaded())

    def __iter__(self) -> Iterator[MCompSeries]:
        return iter(self._ensure_loaded())

    def __repr__(self) -> str:
        if self._data is None:
            return f"{self._name} Dataset (not loaded yet - access any series to load)"
        return repr(self._data)

    def keys(self) -> list[int]:
        return self._ensure_loaded().keys()

    def items(self) -> Iterator[tuple[int, MCompSeries]]:
        return self._ensure_loaded().items()

    def subset(self, series_type: str) -> MCompDataset:
        return self._ensure_loaded().subset(series_type)


class _LazySeries:
    """Lazy proxy for a single series inside a (lazily-loaded) MCompDataset.

    Forwards both attribute and dict-style access to the underlying
    ``MCompSeries``, so ``BJsales.x`` and ``BJsales['x']`` both work
    identically to a real ``MCompSeries``.
    """

    __slots__ = ("_dataset", "_index", "_series")

    def __init__(self, dataset: _LazyDataset, index: int) -> None:
        self._dataset = dataset
        self._index = index
        self._series: MCompSeries | None = None

    def _resolve(self) -> MCompSeries:
        if self._series is None:
            self._series = self._dataset[self._index]
        return self._series

    def __getattr__(self, name: str) -> Any:
        # __getattr__ is only called when normal lookup fails, so the
        # __slots__ attributes above are handled automatically.
        return getattr(self._resolve(), name)

    def __getitem__(self, key: str) -> Any:
        return self._resolve()[key]

    def __repr__(self) -> str:
        if self._series is None:
            return f"<MCompSeries proxy (not loaded yet, index={self._index})>"
        return repr(self._series)

    def keys(self) -> list[str]:
        return self._resolve().keys()


# Module-level lazy datasets for convenient access
M1 = _LazyDataset(load_m1, "M1")
M3 = _LazyDataset(load_m3, "M3")
M4 = _LazyDataset(load_m4, "M4")
Tourism = _LazyDataset(load_tourism, "Tourism")

# Classic individual series (small, bundled with the package)
_Individual = _LazyDataset(load_individual, "Individual")
AirPassengers = _LazySeries(_Individual, 1)
BJsales = _LazySeries(_Individual, 2)
Seatbelts = _LazySeries(_Individual, 3)
taylor = _LazySeries(_Individual, 4)
PromoData = _LazySeries(_Individual, 5)

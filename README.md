# fcompdata

[![PyPI - Downloads](https://img.shields.io/pypi/dm/fcompdata.svg)](https://pypi.org/project/fcompdata/)

Forecasting Competitions Datasets - a Python library for loading M and tourism competitions time series datasets (M1, M3, M4, Tourism) with an interface similar to R's `Mcomp` and `Tcomp` packages.

## Installation

```bash
pip install fcompdata
```

or from github:

```
pip install git+https://github.com/config-i1/fcompdata
```

## Usage

```python
from fcompdata import M1, M3, Tourism

# Access series by 1-based index (R-style)
series = M3[1]
print(series['x'])    # Training data (numpy array)
print(series['xx'])   # Test data (numpy array)
print(series['y'])    # Full series: concat(x, xx), length n + h
print(series['h'])    # Forecast horizon
print(series['n'])    # Training data length
print(series['type']) # Series type (yearly, quarterly, monthly, other)

# Attribute access also works
print(series.sn)          # Series name
print(series.description) # Series description

# Filter by frequency type
yearly = M3.subset('yearly')
monthly = M1.subset('monthly')

# Iterate over all series
for series in M3:
    print(series.sn, len(series.x))

# Get series count
print(len(M3))  # 3003
```

## M4 Dataset

The M4 competition dataset contains 100,000 time series and is too large to bundle with the package. It must be downloaded separately before use. The data is sourced from the [Monash Time Series Forecasting Repository](https://forecastingdata.org/) hosted on Zenodo.

### Downloading M4 Data

```python
from fcompdata.download import download_m4

# Download all M4 frequencies (~50MB total, saved to ~/.fcompdata/m4/)
download_m4()

# Or download specific frequencies
download_m4('yearly')     # 23,000 series
download_m4('quarterly')  # 24,000 series
download_m4('monthly')    # 48,000 series
download_m4('weekly')     # 359 series
download_m4('daily')      # 4,227 series
download_m4('hourly')     # 414 series
```

The data is downloaded once and cached locally in `~/.fcompdata/m4/`. Subsequent calls will use the cached files.

### Using M4 Data

```python
from fcompdata import M4, load_m4

# Load all M4 series (requires all frequencies to be downloaded)
series = M4[1]

# Load a specific frequency
yearly = load_m4('yearly')
monthly = load_m4('monthly')

# Same interface as other datasets
print(series.x)       # Training data
print(series.xx)      # Test data
print(series.h)       # Forecast horizon
print(series.type)    # 'yearly', 'quarterly', etc.

# Filter and iterate
for s in yearly:
    print(s.sn, len(s.x))
```

### M4 Download Sources

The M4 data files are downloaded from the Monash Time Series Forecasting Repository on Zenodo:

| Frequency | Zenodo Record | Horizon |
|-----------|---------------|---------|
| Yearly    | [zenodo.org/record/4656379](https://zenodo.org/record/4656379) | 6 |
| Quarterly | [zenodo.org/record/4656410](https://zenodo.org/record/4656410) | 8 |
| Monthly   | [zenodo.org/record/4656480](https://zenodo.org/record/4656480) | 18 |
| Weekly    | [zenodo.org/record/4656522](https://zenodo.org/record/4656522) | 13 |
| Daily     | [zenodo.org/record/4656548](https://zenodo.org/record/4656548) | 14 |
| Hourly    | [zenodo.org/record/4656589](https://zenodo.org/record/4656589) | 48 |

### Cache Management

```python
from fcompdata.download import clear_cache, get_m4_path

# Check if a frequency is downloaded
path = get_m4_path('yearly')  # Returns Path or None

# Clear all downloaded data
clear_cache()

# Clear only M4 data
clear_cache('m4')
```

## Individual Time Series

In addition to the competition datasets, fcompdata bundles several classic
individual time series ported from base R and the `forecast` package. These
are tiny, load instantly, and behave like a single `MCompSeries` (`x`, `xx`,
`h`, `period`, `type`, `description`). Two of them carry exogenous regressors
on `xreg` / `xregx` / `xregxx`.

| Series          | Origin              | n    | h   | Period | xreg                         |
|-----------------|---------------------|------|-----|--------|------------------------------|
| `AirPassengers` | R `datasets`        | 144  | 12  | 12     | —                            |
| `BJsales`       | R `datasets`        | 150  | 12  | 12     | `BJsales.lead`               |
| `Seatbelts`     | R `datasets`        | 192  | 12  | 12     | `kms`, `PetrolPrice`, `law`  |
| `taylor`        | R `forecast`        | 4032 | 336 | 336    | —                            |
| `PromoData`     | CMAF DFR course     | 156  | 13  | 52     | `Promo1`, `Promo2`           |

```python
from fcompdata import AirPassengers, BJsales, Seatbelts, taylor

# Same MCompSeries interface as the competition series
print(AirPassengers.x)         # 132 training observations
print(AirPassengers.xx)        # 12 holdout observations
print(AirPassengers.period)    # 12 (monthly)

# Series with exogenous regressors are stored as numpy structured arrays
# (recarray), so the column names of explanatory variables are preserved:
print(BJsales.xreg.dtype.names)            # ('BJsales.lead',)
print(BJsales.xreg['BJsales.lead'][:5])    # first five values

print(Seatbelts.xreg.dtype.names)          # ('kms', 'PetrolPrice', 'law')
print(Seatbelts.xreg.kms[:5])              # 1-D array, recarray attribute access
print(Seatbelts.xregxx['law'])             # last 12 values of the law indicator

# xreg is the row-wise concatenation of xregx (training) and xregxx (holdout).
# To get a plain 2-D float matrix for linear algebra:
import numpy as np
mat = np.column_stack([Seatbelts.xreg[n] for n in Seatbelts.xreg.dtype.names])
```

Note: `BJsales` and `BJsales.lead` have `frequency=1` in R. fcompdata stores
them with `period=12` and `type='monthly'` to match the requested holdout of
twelve observations; the original R metadata is documented in the series
`description`.

## Datasets

### Bundled Datasets

These datasets are included with the package and available immediately:

| Dataset | Series | Yearly | Quarterly | Monthly | Other |
|---------|--------|--------|-----------|---------|-------|
| M1      | 1,001  | 181    | 203       | 617     | -     |
| M3      | 3,003  | 645    | 756       | 1,428   | 174   |
| Tourism | 1,311  | 518    | 427       | 366     | -     |

### Downloadable Datasets

These datasets require downloading before use:

| Dataset | Series  | Yearly | Quarterly | Monthly | Weekly | Daily | Hourly |
|---------|---------|--------|-----------|---------|--------|-------|--------|
| M4      | 100,000 | 23,000 | 24,000    | 48,000  | 359    | 4,227 | 414    |

## Series Attributes

Each `MCompSeries` object has the following attributes:

| Attribute     | Type         | Description                              |
|---------------|--------------|------------------------------------------|
| `sn`          | str          | Series name/identifier                   |
| `x`           | numpy.ndarray| Training data (in-sample)                |
| `xx`          | numpy.ndarray| Test data (out-of-sample)                |
| `y`           | numpy.ndarray| Full series: row-wise concatenation of `x` and `xx` (length `n + h`); read-only property |
| `h`           | int          | Forecast horizon                         |
| `n`           | int          | Length of training data                  |
| `period`      | int          | Seasonal period (1, 4, or 12)            |
| `type`        | str          | Series type (yearly/quarterly/monthly/other) |
| `description` | str          | Series description                       |
| `xreg`        | numpy.recarray \| None | Exogenous regressors (length `n + h`) as a structured array with named fields equal to the column names; `None` for series without regressors |
| `xregx`       | numpy.recarray \| None | Training portion of `xreg` (first `n` rows); `None` if absent |
| `xregxx`      | numpy.recarray \| None | Holdout portion of `xreg` (last `h` rows); `None` if absent  |

## Data Sources

The time series data in this package was imported from the following sources:

- **Mcomp** (M1 and M3 data): Hyndman, R.J. (2024). *Mcomp: Data from the M-Competitions*. R package. [CRAN](https://cran.r-project.org/package=Mcomp), [GitHub](https://github.com/robjhyndman/Mcomp)
- **Tcomp** (Tourism data): Hyndman, R.J. (2016). *Tcomp: Data from the 2010 Tourism Forecasting Competition*. R package. [CRAN](https://cran.r-project.org/package=Tcomp), [GitHub](https://github.com/ellisp/Tcomp-r-package)
- **Monash Time Series Forecasting Repository** (M4 data): [forecastingdata.org](https://forecastingdata.org/), hosted on [Zenodo](https://zenodo.org/communities/forecasting)
- **R `datasets` package** (AirPassengers, BJsales, BJsales.lead, Seatbelts): bundled with base R. [CRAN](https://stat.ethz.ch/R-manual/R-devel/library/datasets/html/00Index.html)
- **R `forecast` package** (taylor): Hyndman, R.J. (2024). *forecast: Forecasting functions for time series and linear models*. R package. [CRAN](https://cran.r-project.org/package=forecast), [GitHub](https://github.com/robjhyndman/forecast)
- **CMAF Demand Forecasting course** (PromoData): Svetunkov, I. (2024). *Demand Forecasting course materials* (Session 6.2 — ETS with regressors). [Centre for Marketing Analytics and Forecasting (CMAF)](https://cmaf.lancaster.ac.uk/), Lancaster University Management School.

## References

The datasets were used in the following forecasting competitions:

**M1 Competition:**
> Makridakis, S., Andersen, A., Carbone, R., Fildes, R., Hibon, M., Lewandowski, R., Newton, J., Parzen, E., & Winkler, R. (1982). The accuracy of extrapolation (time series) methods: Results of a forecasting competition. *Journal of Forecasting*, 1(2), 111–153. [doi:10.1002/for.3980010202](https://doi.org/10.1002/for.3980010202)

**M3 Competition:**
> Makridakis, S., & Hibon, M. (2000). The M3-Competition: Results, conclusions and implications. *International Journal of Forecasting*, 16(4), 451–476. [doi:10.1016/S0169-2070(00)00057-1](https://doi.org/10.1016/S0169-2070(00)00057-1)

**M4 Competition:**
> Makridakis, S., Spiliotis, E., & Assimakopoulos, V. (2020). The M4 Competition: 100,000 time series and 61 forecasting methods. *International Journal of Forecasting*, 36(1), 54–74. [doi:10.1016/j.ijforecast.2019.04.014](https://doi.org/10.1016/j.ijforecast.2019.04.014)

**Tourism Forecasting Competition:**
> Athanasopoulos, G., Hyndman, R.J., Song, H., & Wu, D.C. (2011). The tourism forecasting competition. *International Journal of Forecasting*, 27(3), 822–844. [doi:10.1016/j.ijforecast.2010.11.005](https://doi.org/10.1016/j.ijforecast.2010.11.005)

**Monash Time Series Forecasting Archive:**
> Godahewa, R., Bergmeir, C., Webb, G.I., Hyndman, R.J., & Montero-Manso, P. (2021). Monash Time Series Forecasting Archive. *Proceedings of the Neural Information Processing Systems Track on Datasets and Benchmarks* (NeurIPS Datasets and Benchmarks 2021). [arXiv:2105.06643](https://arxiv.org/abs/2105.06643)

The individual time series come from the following original sources:

**AirPassengers:**
> Box, G. E. P., Jenkins, G. M., Reinsel, G. C., & Ljung, G. M. (2015). *Time Series Analysis, Forecasting and Control* (5th ed.). Wiley. Series G.

**BJsales / BJsales.lead:**
> Box, G. E. P., & Jenkins, G. M. (1976). *Time Series Analysis, Forecasting and Control*. Holden-Day. Series M.

**Seatbelts:**
> Harvey, A. C., & Durbin, J. (1986). The effects of seat belt legislation on British road casualties: A case study in structural time series modelling. *Journal of the Royal Statistical Society A*, 149, 187–227. [doi:10.2307/2981553](https://doi.org/10.2307/2981553)

**taylor:**
> Taylor, J. W. (2003). Short-term electricity demand forecasting using double seasonal exponential smoothing. *Journal of the Operational Research Society*, 54, 799–805. [doi:10.1057/palgrave.jors.2601589](https://doi.org/10.1057/palgrave.jors.2601589)

**PromoData:**
> Svetunkov, I. (2024). *Demand Forecasting course materials* (Session 6.2 — ETS with regressors). Centre for Marketing Analytics and Forecasting (CMAF), Lancaster University Management School.

## License

LGPL-3.0-or-later

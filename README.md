# mcomp

Python library for loading M-Competition time series datasets (M1, M3, Tourism) with an interface similar to R's `Mcomp` package.

## Installation

```bash
pip install -e .
```

## Usage

```python
from mcomp import M1, M3, Tourism

# Access series by 1-based index (R-style)
series = M3[1]
print(series['x'])    # Training data (numpy array)
print(series['xx'])   # Test data (numpy array)
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

## Datasets

| Dataset | Series | Yearly | Quarterly | Monthly | Other |
|---------|--------|--------|-----------|---------|-------|
| M1      | 1001   | 181    | 203       | 617     | -     |
| M3      | 3003   | 645    | 756       | 1428    | 174   |
| Tourism | 1311   | 518    | 427       | 366     | -     |

## Series Attributes

Each `MCompSeries` object has the following attributes:

| Attribute     | Type         | Description                              |
|---------------|--------------|------------------------------------------|
| `sn`          | str          | Series name/identifier                   |
| `x`           | numpy.ndarray| Training data (in-sample)                |
| `xx`          | numpy.ndarray| Test data (out-of-sample)                |
| `h`           | int          | Forecast horizon                         |
| `n`           | int          | Length of training data                  |
| `period`      | int          | Seasonal period (1, 4, or 12)            |
| `type`        | str          | Series type (yearly/quarterly/monthly/other) |
| `description` | str          | Series description                       |

## Data Sources

The time series data in this package was imported from the following R packages:

- **Mcomp** (M1 and M3 data): Hyndman, R.J. (2024). *Mcomp: Data from the M-Competitions*. R package. [CRAN](https://cran.r-project.org/package=Mcomp), [GitHub](https://github.com/robjhyndman/Mcomp)
- **Tcomp** (Tourism data): Hyndman, R.J. (2016). *Tcomp: Data from the 2010 Tourism Forecasting Competition*. R package. [CRAN](https://cran.r-project.org/package=Tcomp), [GitHub](https://github.com/robjhyndman/Tcomp)

## References

The datasets correspond to the following forecasting competitions:

**M1 Competition:**
> Makridakis, S., Andersen, A., Carbone, R., Fildes, R., Hibon, M., Lewandowski, R., Newton, J., Parzen, E., & Winkler, R. (1982). The accuracy of extrapolation (time series) methods: Results of a forecasting competition. *Journal of Forecasting*, 1(2), 111–153. [doi:10.1002/for.3980010202](https://doi.org/10.1002/for.3980010202)

**M3 Competition:**
> Makridakis, S., & Hibon, M. (2000). The M3-Competition: Results, conclusions and implications. *International Journal of Forecasting*, 16(4), 451–476. [doi:10.1016/S0169-2070(00)00057-1](https://doi.org/10.1016/S0169-2070(00)00057-1)

**Tourism Forecasting Competition:**
> Athanasopoulos, G., Hyndman, R.J., Song, H., & Wu, D.C. (2011). The tourism forecasting competition. *International Journal of Forecasting*, 27(3), 822–844. [doi:10.1016/j.ijforecast.2010.11.005](https://doi.org/10.1016/j.ijforecast.2010.11.005)

## License

MIT

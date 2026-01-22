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

## License

MIT

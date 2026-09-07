# Data Access

## Directly from Zenodo

The full dataset is archived on Zenodo:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22181274.svg)](https://doi.org/10.5281/zenodo.22181274)

Visit the [Zenodo record](https://doi.org/10.5281/zenodo.22181274) and download the archives you need.

### Contents

| Archive | Description | Size |
|---------|-------------|------|
| `raw.zip` | Raw IOC parquet files (per station, per year) | ~23 GB |
| `clean.zip` | Cleaned time series (1 parquet per station) | ~5 GB |
| `surge.zip` | Detided time series (1 parquet per station) | ~14 GB |
| `transformations.zip` | JSON cleaning configurations | ~60 MB |
| `meta.csv` | Station metadata | ~400 KB |

After downloading, extract with:

```bash
unzip clean.zip
unzip surge.zip
unzip transformations.zip
unzip raw.zip
```

## GitHub mirror

Releases are also available on [GitHub](https://github.com/oceanmodeling/ioc_cleanup/releases).
The transformations (JSON configs) and metadata are mirrored there.
For the full dataset (raw + clean + surge), use Zenodo.

## How to cite

If you use this dataset, please cite:

```
Saillour, T. and Mavrogiorgos, P.: Reproducible, transparent and traceable cleaning of IOC Tide Gauge Data,
EGU General Assembly 2026, Vienna, Austria, 3–8 May 2026, EGU26-7777,
https://doi.org/10.5194/egusphere-egu26-7777, 2026.
```

Dataset DOI: [10.5281/zenodo.22181274](https://doi.org/10.5281/zenodo.22181274)

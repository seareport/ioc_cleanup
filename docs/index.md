# IOC Cleanup

`ioc_cleanup` provides a reproducible, transparent, and traceable workflow
for cleaning tide gauge data from [IOC](https://www.ioc-sealevelmonitoring.org/list.php) (Intergovernmental Oceanographic Commission) stations worldwide.

## IOC Cleanup database
All stations with clean data between 1st of January 2020 and the 31st of december 2025.

<iframe
  src="assets/cleaned_map.html"
  width="100%"
  height="740"
  style="border:none;">
</iframe>


## Getting Started

### Prerequisites

- Python 3.11+ (recommended)
- ~24 GB free disk space for raw IOC 2020-2025 data

### Installation

```bash
git clone https://github.com/seareport/ioc_cleanup.git
pip install -r requirements.txt
```

### Minimal example
```python
import searvey
import ioc_cleanup as C

station = "abed"
df_raw = searvey.fetch_ioc_station(station, "2020-01-01", "2026-01-01")

trans = C.load_transformation_from_path(
    "../transformations/abed_bub.json"
)

df_clean = C.transform(df_raw, trans)
```

## Example for `maya` station:

### From raw signal...
<iframe
  src="assets/example.html"
  width="100%"
  height="710"
  style="border:none;">
</iframe>

 ... using [JSON transformation](reference/json-schema.md) ...

### ... to clean signal
<iframe
  src="assets/example_clean.html"
  width="100%"
  height="710"
  style="border:none;">
</iframe>

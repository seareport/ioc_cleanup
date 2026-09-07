#

!!! success ""
    This project proposes a **community-driven, version-controlled**     approach where all cleaning decisions are explicitly **recorded** and **auditable**.

## Why?

Cleaning tide gauge data is often:

- :x: manual
- :x: poorly documented
- :x: hard to reproduce
- :x: difficult to review or share


## Concept

The core idea of `ioc_cleanup` is **declarative cleaning**.

Instead of scripts or notebooks, all cleaning decisions are:

- [x] Explicit
- [x] Version controlled
- [x] Human-readable
- [x] Reviewable

Cleaning logic lives entirely in JSON files.

## Why it matters

This methodology allows:

- [x] Flagging:
    * bad or corrupt data (timestamp / data ranges)
    * sensor breakpoints
    * singular phenomena (e.g. tsunamis, meteo-tsunamis, seiches, or unidentified events)
- [x] **Reproducible** cleaning
- [x] **Transparent** and **traceable** decisions stored in plain JSON
- [x] Peer review of cleaning decisions via GitHub
- [x] Easy extension to any other datasets (e.g. [GESLA](https://gesla787883612.wordpress.com/), [NDBC](https://www.ndbc.noaa.gov/))
- [x] Gradual growth in station coverage through community contributions


## Transformations

Each station/sensor pair is described by a JSON file located in:

```
./transformations/
```

These files define the transformation from **raw data → clean signal** by
declaring:

- valid time windows
- dropped timestamps
- dropped ranges
- breakpoints
- notes and metadata

More details in the [JSON format](./reference/json-schema.md)


## Dataset Details

### Cleaned Stations
<iframe
  src="./assets/cleaned_map.html"
  width="100%"
  height="740"
  style="border:none;">
</iframe>

Download the database as a csv: [**`cleaned_ioc_stations.csv`**](./assets/cleaned_ioc_stations.csv)

### Coverage
<iframe
  src="./assets/coverage_oceans.html"
  width="100%"
  height="330"
  style="border:none;">
</iframe>

### Data availability

<iframe
  src="./assets/data_availability_heatmap.html"
  width="100%"
  height="500"
  style="border:none;">
</iframe>


### Ratio of data removed

<iframe
  src="./assets/data_removed_map.html"
  width="100%"
  height="590"
  style="border:none;">
</iframe>

<iframe
  src="./assets/data_removed_hist.html"
  width="100%"
  height="320"
  style="border:none;">
</iframe>

### Note

The above figures have been generated with the helper functions in `scripts/` folder:

 1. `download_ioc.py` to download IOC stations
 2. `generate_stations_csv.py` to build the cleaned stations dataset from the `transformations` folder and the IOC station dataset (from step 1)
 3. `generate_maps.py` to create maps and graphs for the online documentation
 4. `save_cleaning_scenarios.py` to create the time series graphs used in the online documentation

Steps 3 and 4 require to have run step 1 for all cleaned IOC stations.

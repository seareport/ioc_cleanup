from __future__ import annotations

import logging
import pathlib

import ioc_cleanup as C

logger = logging.getLogger(__name__)

YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
OVERWRITE = True
opts = C.OPTS

raw_folder = pathlib.Path("./data")
surge_folder = pathlib.Path("./surge")
surge_folder.mkdir(exist_ok=True)

clean_candidates = C.get_transformation_paths()


def process_station(path: pathlib.Path) -> None:
    station, sensor = path.stem.split("_")
    outpath = surge_folder / f"{station}_{sensor}.parquet"

    if outpath.exists() and not OVERWRITE:
        return

    t = C.load_transformation(station, sensor)
    if t.skip:
        logger.info(f"skip flag active for station {station}")
        return

    logger.info(f"station: {station}")
    ts = C.load_station(station)
    if ts.empty:
        logger.info(f"no valid data for station {station}")
        return

    clean_ts = C.clean(ts, station, sensor)
    clean_ts.attrs["sensor"] = sensor

    opts["lat"] = float(clean_ts.attrs["lat"])
    res = C.surge(clean_ts, opts, C.RESAMPLE).to_frame(name=sensor)
    # inherit station metadata carried over from the raw/clean series attrs
    res.attrs = clean_ts.attrs
    res.attrs["sensor"] = sensor
    res.attrs["tidal_component"] = "removed"
    res.attrs["water_level_type"] = "surge_residual"
    res.attrs["detide_package"] = "utide"
    res.to_parquet(outpath)


def main() -> None:
    for path in clean_candidates:
        process_station(path)


if __name__ == "__main__":
    main()

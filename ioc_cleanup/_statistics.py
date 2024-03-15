from __future__ import annotations

import pathlib
import typing as T

import multifutures
import pandas as pd

from ._constants import DETIDE_END
from ._constants import DETIDE_START
from ._constants import SIMULATION_END
from ._constants import SIMULATION_START


def calc_ratio(sr: pd.Series[float], period: pd.DatetimeIndex) -> float:
    sr = sr[(period[0] <= sr.index) & (sr.index <= period[-1])]
    return len(sr) / len(period)


def calc_raw_statistics(sr: pd.Series[float]) -> dict[str, T.Any]:
    interval_value_counts = sr.index.to_series().diff().value_counts()
    main_interval_occurences = interval_value_counts.iloc[0]
    main_interval = T.cast(pd.Timedelta, interval_value_counts.index[0])
    detide_period = pd.date_range(DETIDE_START, DETIDE_END, freq=main_interval, inclusive="left")
    simulation_period = pd.date_range(SIMULATION_START, SIMULATION_END, freq=main_interval, inclusive="left")
    data = {
        "count": len(sr),
        "main_interval": main_interval,
        "main_interval_ratio": main_interval_occurences / len(sr),
        "detide_ratio": calc_ratio(sr, detide_period),
        "simulation_ratio": calc_ratio(sr, simulation_period),
        "min": sr.min(),
        "q001": sr.quantile(0.001),
        "q01": sr.quantile(0.01),
        "q25": sr.quantile(0.25),
        "mean": sr.mean(),
        "median": sr.median(),
        "q75": sr.quantile(0.75),
        "q99": sr.quantile(0.99),
        "q999": sr.quantile(0.999),
        "max": sr.max(),
        "range": abs(sr.max() - sr.min()),
        "std": sr.std(),
        "skew": sr.skew(),
        "kurtosis": sr.kurtosis(),
    }
    data.update(**sr.attrs)  # type: ignore[misc] # Keywords must be string
    return data


def calc_station_statistics(meta_row: T.Any, sensor: str, sr: pd.Series[float]) -> dict[str, T.Any]:
    data = {
        "ioc_code": meta_row.ioc_code,
        "sensor": sensor,
        "lon": meta_row.lon,
        "lat": meta_row.lat,
        "country": meta_row.country,
        "location": meta_row.location,
        # "geometry": row.geometry,
    }
    data.update(**calc_raw_statistics(sr))
    return data


def calc_station_statistics_from_path(meta: pd.DataFrame, path: pathlib.Path) -> dict[str, T.Any]:
    ioc_code, sensor = path.stem.split("_")
    meta_row = meta[meta.ioc_code == ioc_code].iloc[0]
    df = pd.read_parquet(path)
    sr = df[sensor]
    stats = calc_station_statistics(meta_row=meta_row, sensor=sensor, sr=sr)
    return stats


def calc_statistics(meta: pd.DataFrame, stations_dir: pathlib.Path, pattern: str = "*.parquet") -> pd.DataFrame:
    func_kwargs = [{"meta": meta, "path": path} for path in stations_dir.glob(pattern)]
    results = multifutures.multiprocess(calc_station_statistics_from_path, func_kwargs, check=True)
    stats = pd.DataFrame([r.result for r in results])
    return stats

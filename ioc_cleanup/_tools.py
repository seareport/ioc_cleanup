from __future__ import annotations

import os
import typing as T
from pathlib import Path

import hvplot.pandas  # noqa: F401
import numpy as np
import pandas as pd
import utide

from . import _constants
from . import _models
from . import _searvey

# PATH
JSON_DIR = _constants.TRANSFORMATIONS_DIR
OPTS = {
    "constit": "auto",
    "method": "ols",  # ols is faster and good for missing data (Ponchaut et al., 2001)
    "order_constit": "frequency",
    "Rayleigh_min": 0.97,
    "verbose": True,
}
RESAMPLE = 10


def get_transformation_paths() -> list[Path]:
    paths = sorted(JSON_DIR.glob("*.json"))
    return paths


def get_station_names() -> list[str]:
    stations = get_transformation_paths()
    station_sensor = []
    for path in stations:
        station_sensor.append(path.stem)
    return station_sensor


def dump_transformation(
    trans: _models.Transformation,
    dest_dir: str | os.PathLike[str] = _constants.TRANSFORMATIONS_DIR,
) -> None:
    path = f"{dest_dir}/{trans.ioc_code}_{trans.sensor}.json"
    with open(path, "w") as fd:
        fd.write(trans.model_dump_json(indent=2, round_trip=True))
        fd.write("\n")


def resolve_transformation_dir() -> Path:
    if JSON_DIR.exists():
        return JSON_DIR
    else:
        return Path(_constants.REGISTRY.fetch())


def load_transformation(
    ioc_code: str,
    sensor: str,
    src_dir: str | os.PathLike[str] = JSON_DIR,
) -> _models.Transformation:
    """
    Load a transformation definition for a station and sensor.

    This is a convenience wrapper around
    `load_transformation_from_path` that constructs the transformation
    filename from the IOC station code and sensor identifier.

    Args:
        ioc_code: IOC station code.
        sensor: Sensor identifier.
        src_dir: Directory containing transformation JSON files.

    Returns:
        Parsed transformation model.
    """
    if src_dir is None:
        src_dir = resolve_transformation_dir()
    path = Path(src_dir) / f"{ioc_code}_{sensor}.json"
    return load_transformation_from_path(path)


def load_transformation_from_path(path: str | os.PathLike[str]) -> _models.Transformation:
    """
    Load a transformation definition from a JSON file.

    Parameters:
        path: Path to a transformation JSON file describing cleaning rules.

    Returns:
        Parsed transformation model.
    """
    with open(path) as fd:
        contents = fd.read()
    model = _models.Transformation.model_validate_json(contents)
    return model


def transform(df: pd.DataFrame, transformation: _models.Transformation | None = None) -> pd.DataFrame:
    """
    Apply a cleaning transformation to an IOC sea-level time series.

    The transformation defines the valid time window, dropped timestamps,
    dropped date ranges, and sensor breakpoints. Bad data is ropped data from the DatFrame;
    no offset correction is applied.

    Parameters:
        df: Raw IOC sea-level time series. The DataFrame must have
            `ioc_code` and `sensor` entries in its attributes if
            `transformation` is not provided.
        transformation: Cleaning transformation to apply. If not provided,
            it is loaded automatically using DataFrame attributes.

    Returns:
        Cleaned time series with metadata stored in `DataFrame.attrs`.
    """
    df = df.copy()
    if transformation is None:
        transformation = load_transformation(ioc_code=df.attrs["ioc_code"], sensor=df.attrs["sensor"])
    df = df[transformation.start : transformation.end]  # type: ignore[misc]  # https://stackoverflow.com/questions/70763542/pandas-dataframe-mypy-error-slice-index-must-be-an-integer-or-none
    for start, end in transformation.dropped_date_ranges:
        df[start:end] = np.nan  # type: ignore[misc]  # https://stackoverflow.com/questions/70763542/pandas-dataframe-mypy-error-slice-index-must-be-an-integer-or-none
    if transformation.dropped_timestamps:
        t_ = pd.DatetimeIndex(transformation.dropped_timestamps)
        t0 = df.index[0]
        t1 = df.index[-1]
        drop_index = np.where(np.logical_and(t_ > t0, t_ < t1))[
            0
        ]  # this step is needed to select only timestamps within the DataFrame time window
        df.loc[t_[drop_index], :] = np.nan
    df.attrs["breakpoints"] = [
        b.isoformat() for b in sorted(transformation.breakpoints)
    ]  # isoformat otherwise the parquet export will fail
    df.attrs["status"] = "transformed"
    return df


def get_segments(df: pd.Series) -> list[pd.Series]:
    df = df.copy()
    if len(df.attrs["breakpoints"]) > 0:
        chunks = []
        prev = df.index.min()
        for bp in df.attrs["breakpoints"]:
            chunks.append(df.loc[prev:bp])
            prev = bp
        chunks.append(df.loc[prev:])
    else:
        chunks = [df]
    return chunks


def demean_signal(df: pd.Series) -> pd.Series:
    chunks = get_segments(df)
    for ichunk, chunk in enumerate(chunks):
        chunks[ichunk] -= chunk.mean()
    df = pd.concat(chunks)
    return df


def clean(df: pd.DataFrame, station: str, sensor: str) -> pd.Series:
    """
    Clean a raw IOC time series using the corresponding transformation file.

    Wrapper around `transform` function: returns a single sensor series.

    Parameters:
        df: Raw IOC station data.
        station: IOC station code.
        sensor: Sensor identifier.

    Returns:
        Cleaned sea-level time series for the selected sensor.
    """
    trans = load_transformation_from_path("./transformations/" + station + "_" + sensor + ".json")
    ts = transform(df, trans)[sensor]
    ts.attrs["cleaning_date"] = pd.Timestamp.now().isoformat()
    return ts


def surge(ts: pd.Series, opts: T.Mapping[str, T.Any], rsmp: int | None) -> pd.Series:
    """
    Compute the non-tidal (surge) component of a sea-level time series.

    Tidal constituents are estimated using UTide and reconstructed at the
    original timestamps. The tidal signal is then subtracted from the
    observed series.

    Parameters:
        ts: Sea-level time series.
        opts: UTide solver options.
        rsmp: Optional resampling interval in minutes. If provided, the series is resampled before tidal analysis.

    Returns:
        Surge (non-tidal residual) time series.
    """
    ts0 = ts.copy()
    if rsmp is not None:
        ts = ts.resample(f"{rsmp}min").mean()
        ts = ts.shift(freq=f"{rsmp / 2}min")
    coef = utide.solve(ts.index, ts, **opts)
    tidal = utide.reconstruct(ts0.index, coef, verbose=OPTS["verbose"])
    data = T.cast(np.ndarray, ts0.values - tidal.h)
    return pd.Series(data=data, index=ts0.index)


def load_clean_ts_for_year(
    station: str,
    sensor: str,
    year: int,
    folder: Path,
    *,
    demean: bool,
) -> pd.Series:
    r_ = _searvey.load_station(station, folder, 2020, 2026).sort_index()
    c_ = clean(r_, station, sensor)
    c_ = c_.loc[f"{year}-01-01" : f"{year}-12-31"].dropna()  # type: ignore[misc]
    if demean:
        c_ = demean_signal(c_)
    return c_


def load_surge_ts_for_year(
    station: str,
    sensor: str,
    year: int,
    folder: Path,
    *,
    demean: bool,
) -> pd.Series:
    c_ = load_clean_ts_for_year(station, sensor, year, folder, demean=demean)
    ioc = _searvey.get_meta()
    lat = ioc[ioc.ioc_code == station].lat.values[0]
    OPTS["lat"] = lat
    if not c_.empty:
        s_ = surge(c_, OPTS, RESAMPLE)
        s_.columns = [sensor]  # type: ignore[attr-defined]
        return s_
    else:
        return pd.Series()

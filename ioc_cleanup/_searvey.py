from __future__ import annotations

import functools
import logging
import os
import typing as T
from pathlib import Path

import geopandas as gpd
import pandas as pd
import searvey

logger = logging.getLogger(__name__)


@functools.cache
def get_meta() -> gpd.GeoDataFrame:
    """
    Retrieve IOC station metadata with geographic coordinates.

    Metadata are collected from both the IOC web service and the IOC API
    and merged into a single GeoDataFrame.

    Returns:
        GeoDataFrame containing IOC station codes, longitude, latitude,
        and geometry in EPSG:4326.
    """
    meta_web = searvey.get_ioc_stations()
    meta_api = (
        pd.read_json("http://www.ioc-sealevelmonitoring.org/service.php?query=stationlist&showall=all")
        .drop_duplicates()
        .rename(columns={"Code": "ioc_code"})
    )

    merged = pd.merge(
        meta_web.drop(columns=["lon", "lat", "geometry"]),
        meta_api[["ioc_code", "Lon", "Lat"]].rename(columns={"Lon": "lon", "Lat": "lat"}).drop_duplicates(),
        on=["ioc_code"],
    )
    merged = T.cast(
        gpd.GeoDataFrame,
        merged.assign(geometry=gpd.points_from_xy(merged.lon, merged.lat, crs="EPSG:4326")),
    )
    return merged


def download_raw(ioc_codes: list[str], start: pd.Timestamp, end: pd.Timestamp) -> dict[str, pd.DataFrame]:
    """
    Download raw IOC sea-level data for multiple stations.

    Parameters:
        ioc_codes: List of IOC station codes.
        start: Start timestamp.
        end: End timestamp.

    Returns:
        Dictionary mapping station codes to raw dataframes.
    """
    no_codes = len(ioc_codes)
    start_dates = pd.DatetimeIndex([start] * no_codes)
    end_dates = pd.DatetimeIndex([end] * no_codes)
    dataframes: dict[str, pd.DataFrame] = searvey._ioc_api._fetch_ioc(
        station_ids=ioc_codes,
        start_dates=start_dates,
        end_dates=end_dates,
        http_client=None,
        rate_limit=None,
        multiprocessing_executor=None,
        multithreading_executor=None,
        progress_bar=False,
    )
    return dataframes


def download_year_station(
    station: str,
    year: int,
    data_folder: str = "./data",
) -> None:
    """
    Download and store one year of IOC data for a single station.

    Data are saved as Parquet files under `<data_folder>/<year>/`.

    Parameters:
        station: IOC station code.
        year: Year to download.
        data_folder: Base directory for storing downloaded data.
    """
    from ioc_cleanup._constants import METADATA

    data_folder = os.path.abspath(data_folder)
    year_folder = os.path.join(data_folder, str(year))
    os.makedirs(year_folder, exist_ok=True)
    try:
        start = pd.Timestamp(f"{year}-01-01")
        end = pd.Timestamp(f"{year}-12-31T23:59:59")
        dict_df = download_raw([station], start, end)
        df = dict_df[station]
        if not df.empty:
            logger.info(f"  Saved {station} for {year}")
            ioc = get_meta()
            meta = ioc[ioc.ioc_code == station].iloc[0].to_dict()
            df.attrs = {**METADATA, **{k: str(v) for k, v in meta.items()}}  # type: ignore[dict-item]
            df.to_parquet(f"{year_folder}/{station}.parquet")
    except Exception as e:
        logger.error(f"Error for {station} in {year}: {e}")


def load_station(
    station: str,
    data_dir: Path = Path("./data"),
    start_year: int = 2011,
    end_year: int = 2026,
) -> pd.DataFrame:
    """
    Load multi-year IOC data for a station from local Parquet files.

    Parameters:
        station: IOC station code.
        data_dir: Base directory containing yearly Parquet files.
        start_year: First year to load (inclusive).
        end_year: Last year to load (exclusive).

    Returns:
        Concatenated DataFrame containing the available station data.
        Returns an empty DataFrame if no data are found.
    """
    dfs = []
    for year in range(start_year, end_year):
        path = data_dir / str(year) / f"{station}.parquet"
        if not os.path.exists(path):
            logger.debug(f"Path does not exist: {path}; no data for {year}")
            continue
        df = pd.read_parquet(path)
        if df.empty:
            logger.debug(f"DatFrame empty for station {station} in {year}")
            continue
        dfs.append(df)

    if dfs:
        return pd.concat(dfs)
    else:
        logger.error(f"No data found for station {station} betweeen {start_year} end {end_year}")
        return pd.DataFrame()

from __future__ import annotations

import glob
from pathlib import Path

import geopandas as gp
import holoviews as hv
import hvplot.pandas  # noqa: F401
import numpy as np
import pandas as pd
import panel as pn
import shapely.geometry
import tqdm
import xarray as xr

import ioc_cleanup as C

MAX_WAVE_POINTS = 2
KAMCHATKA_START = pd.Timestamp("2025-07-01")
KAMCHATKA_END = pd.Timestamp("2025-10-01")
TONGA_START = pd.Timestamp("2022-01-01")
TONGA_END = pd.Timestamp("2022-01-31")
DOCS_DIR = Path("docs/")
SURGE_DIR = Path("surge")
# plot kwargs
MAP_COMMON = {
    "geo": True,
    "x": "lon",
    "y": "lat",
}
MAP_BIG_POINTS = {
    **MAP_COMMON,
    **{"s": 100, "logz": True, "line_color": "k", "tiles": True, "hover_cols": "index"},
}
HIST = {
    "grid": True,
    "logy": True,
    "bins": 35,
    "ylim": (0.5, None),
    "ylabel": "Number of stations",
    "xlabel": "",
}
BAR = {
    "grid": True,
    "ylabel": "Number of cleaned stations",
    "xlabel": "Ocean",
    "c": "#D2EBF9",
    "legend": "top",
}
LINE = {
    "ylabel": "Percentage of IOC stations cleaned",
    "label": "Percentage of TGs cleaned / over total IOC stations",
    "color": "#0F60A8",
    "size": 80,
}


def extract_waves(time, eta, crossing="up"):
    """
    Extract wave properties using zero-crossing method.

    Parameters
    ----------
    time : array-like
        Time vector.
    eta : array-like
        Surface elevation.
    crossing : {'up', 'down'}
        Zero-crossing direction.

    Returns
    -------
    pd.DataFrame
        Columns: ['wave', 'H', 'T', 't_crest', 't_trough']
    """
    eta = np.asarray(eta)
    time = np.asarray(time)

    fluc = eta - eta.mean()
    sgn = np.sign(fluc)

    if crossing == "up":
        zc = np.where((sgn[:-1] < 0) & (sgn[1:] > 0))[0]
    else:
        zc = np.where((sgn[:-1] > 0) & (sgn[1:] < 0))[0]

    waves = []
    for i in range(len(zc) - 1):
        i0 = zc[i] + 1
        i1 = zc[i + 1]

        if i1 - i0 < MAX_WAVE_POINTS:
            continue

        segment = fluc[i0:i1]
        seg_time = time[i0:i1]

        crest_idx = np.argmax(segment)
        trough_idx = np.argmin(segment)

        waves.append(
            {
                "wave": i + 1,
                "H": segment[crest_idx] + abs(segment[trough_idx]),
                "T": time[i1] - time[i0],
                "t_crest": seg_time[crest_idx],
                "t_trough": seg_time[trough_idx],
            },
        )

    return pd.DataFrame(waves)


@pn.cache
def load_world_oceans():
    df = gp.read_file(
        "https://gist.githubusercontent.com/tomsail/2fa52d9667312b586e7d3baee123b57b/raw/f121bd446e7c276e7230fb9896e4d487d63a8cb1/world_maritime_sectors.json",
    )
    return df


def find_ocean_for_station(station, oceans_df, xstr="longitude", ystr="latitude"):
    point = shapely.geometry.Point(station[xstr], station[ystr])
    for _, ocean in oceans_df.iterrows():
        if point.within(ocean["geometry"].buffer(0)):
            # Return a tuple with the two desired column values
            return ocean["name"], ocean["ocean"]
    # Return a tuple with None for both values if no match is found
    return None, None


def assign_oceans(df):
    oceans_ = load_world_oceans()
    unique_stations = df.ioc_code.unique()
    mapping = {}
    for unique_station in unique_stations:
        s = df[df.ioc_code == unique_station].iloc[0]
        mapping[unique_station] = find_ocean_for_station(s, oceans_, "lon", "lat")
    df[["name", "ocean"]] = df.apply(
        lambda station: mapping[station.ioc_code],
        axis=1,
        result_type="expand",
    )
    return df


def save_map(hv_map, filename: str, height: int = 700) -> None:
    """Save an hvplot map to an HTML file via Panel."""
    pane = pn.Row(
        pn.pane.HoloViews(
            hv_map.opts(responsive=True),
            sizing_mode="stretch_width",
            height=height,
        ),
        width_policy="max",
    )
    pane.save(str(DOCS_DIR / "assets" / filename))


def get_removed_ratio(meta: pd.DataFrame) -> pd.DataFrame:
    ioc_codes = meta.ioc_code.to_list()
    meta["cleaned_ratio"] = 0.0

    for station in tqdm.tqdm(ioc_codes):
        for path in sorted(glob.glob(f"./transformations/{station}_*.json")):
            t = C.load_transformation_from_path(path)
            raw = C.load_station(station, C.DATA_DIR, start_year=2020, end_year=2026)
            total = len(raw[t.sensor].dropna().values)
            clean = C.clean(raw, t.ioc_code, t.sensor)
            clean_total = len(clean.dropna().values)
            meta.loc[meta.ioc_code == station, "cleaned_ratio"] = 1 - clean_total / total

    return meta


def detect_tsunamis(ioc_codes: list[str], tsunami_start: pd.Timestamp, tsunami_end: pd.Timestamp) -> dict:
    """Detect tsunami events within the configured time window."""
    recorded = {}
    for station in ioc_codes:
        for path in sorted(glob.glob(f"./transformations/{station}*.json")):
            t = C.load_transformation_from_path(path)
            for ts_start, ts_end in t.tsunami:
                if ts_start <= tsunami_start or ts_end >= tsunami_end:
                    continue
                surge = C.load_surge_ts_for_year(t.ioc_code, t.sensor, tsunami_start.year, C.DATA_DIR, demean=True)
                s_ = surge.loc[ts_start:ts_end]
                s_ -= s_.mean()
                waves = extract_waves(s_.index, s_).sort_values("H", ascending=False, ignore_index=True)
                recorded[station] = {
                    "wave number": waves.loc[0, "wave"],
                    "tsunami wave height": waves.loc[0, "H"],
                    "tsunami wave period": waves.loc[0, "T"],
                }
    return recorded


def make_tsunami_map(recorded_tsunamis: dict, ioc: pd.DataFrame, tsunami_name: str) -> None:
    """Build and save the Kamchatka tsunami map."""
    kamchatka = (
        pd.DataFrame(recorded_tsunamis)
        .T.join(ioc.set_index("ioc_code")[["lon", "lat"]], how="left")
        .astype({"tsunami wave height": float})
    )
    hv_map = kamchatka.hvplot.points(
        c="tsunami wave height",
        clim=(0, 2),
        cmap="rainbow4",
        title=f"Tsunami wave heights recorded for {tsunami_name} tsunami",
        **MAP_BIG_POINTS,
    )
    save_map(hv_map, f"{tsunami_name.lower()}_map.html")


def make_cleaned_stations_map(ioc: pd.DataFrame, clean: list[str]) -> None:
    """Build and save the cleaned stations map."""
    all_map = ioc.hvplot.points(
        **MAP_COMMON,
        c="k",
        s=2,
        label="All IOC stations",
        hover_cols="ioc_code",
    )
    clean_map = ioc[ioc.ioc_code.isin(clean)].hvplot.points(
        **MAP_COMMON,
        c="g",
        s=50,
        tiles=True,
        xlim=(-180, 180),
        ylim=(-70, 82.53),
        title="Cleaned IOC stations",
        label="Cleaned IOC stations",
        hover_cols="ioc_code",
        legend="bottom_right",
    )
    save_map(clean_map * all_map, "cleaned_map.html")


def make_cleaned_ratio_map(stats: pd.DataFrame) -> None:
    """Build and save the data availability map."""
    hv_map = stats.hvplot.points(
        c="cleaned_ratio",
        clim=(0.0001, 1),
        cmap="rainbow4",
        title="Data removed, from 0 to 1 (or 100%)",
        **MAP_BIG_POINTS,
    )
    save_map(hv_map, "data_removed_map.html")


def make_hist(df: pd.DataFrame, var: str, title: str, name: str, **kwargs):
    hv_graph = df[var].hvplot.hist(**kwargs, title=title)
    save_map(hv_graph, name, height=300)


def make_bar(df: pd.DataFrame, all_meta: pd.DataFrame, var: str, title: str, name: str):
    cleaned_counts = df[var].value_counts().sort_index()
    all_counts = all_meta[var].value_counts().sort_index()
    proportion = (cleaned_counts / all_counts * 100).dropna()

    combined = pd.DataFrame(
        {
            "Cleaned stations": cleaned_counts,
            "Percentage of total cleaned": proportion.reindex(cleaned_counts.index),
        },
    )

    bars_count = combined["Cleaned stations"].hvplot.bar(**BAR)
    line_pct = combined["Percentage of total cleaned"].hvplot(**LINE)

    def rotate_labels(plot):
        plot.state.xaxis.major_label_orientation = 0.785  # radians, ~45°

    overlay = (bars_count * line_pct).opts(
        hv.opts.Overlay(multi_y=True, title=title, hooks=[rotate_labels]),
    )
    save_map(overlay, name, height=370)


def compute_monthly_availability(stats: pd.DataFrame, surge_folder: Path) -> np.ndarray:
    """Compute monthly availability matrix (stations x months).

    Reads pre-computed surge parquet files and computes the ratio of
    non-NaN values to expected values per month.

    Returns an array of shape (len(stats), n_months).
    """
    import typing as T

    starts = pd.date_range(C.START, C.END, freq="1MS")
    ends = pd.date_range(C.START, C.END, freq="1ME")
    n_months = len(ends)
    tmp = np.zeros((len(stats), n_months))

    for ix, row in stats.iterrows():
        inpath = surge_folder / f"{row.ioc_code}_{row.sensor}.parquet"
        if not inpath.exists():
            tmp[ix, :] = 0
            continue
        ts = pd.read_parquet(inpath)
        for it, (s, e) in enumerate(zip(starts, ends, strict=False)):
            end = e + pd.Timedelta(days=1)
            sr = ts.loc[s:end]
            interval_value_counts = sr.index.to_series().diff().value_counts()
            if len(interval_value_counts):
                main_interval = T.cast(pd.Timedelta, interval_value_counts.index[0])
                period = pd.date_range(s, end, freq=main_interval, inclusive="left")
                tmp[ix, it] = C._statistics.calc_ratio(sr.dropna(), period)
            else:
                tmp[ix, it] = 0

    return tmp


def make_availability_heatmap(stats: pd.DataFrame, surge_folder: Path) -> None:
    """Build and save a station x month availability heatmap."""
    stations = stats["ioc_code"].to_list()
    months = pd.date_range(C.START, C.END, freq="1MS")[:-1]
    tmp = compute_monthly_availability(stats, surge_folder)

    da = xr.DataArray(
        np.array(tmp, dtype=float),
        dims=("station", "month"),
        coords={
            "station": np.arange(len(stations)),
            "month": months,
        },
    )

    df = da.to_dataframe("availability").reset_index()
    df["month"] = df["month"].dt.strftime("%Y-%m")
    df["station_str"] = df["station"].apply(lambda x: stations[x])

    heatmap = df.hvplot.heatmap(
        x="month",
        y="station_str",
        C="availability",
        cmap="fire",
        clim=(0, 1),
        width=900,
        height=max(400, len(stations) * 7),
        rot=45,
        fontscale=0.8,
    ).opts(
        default_tools=[],
        active_tools=[],
    )

    save_map(heatmap, "data_availability_heatmap.html", height=max(400, len(stations) * 7))


def main():
    DOCS_DIR.mkdir(exist_ok=True)

    ioc = C.get_meta()
    stats = C.calc_statistics(ioc, stations_dir=C.TRANSFORMATIONS_DIR, pattern="*.json")
    stats = assign_oceans(stats)
    ioc = assign_oceans(ioc)
    stats.to_csv(DOCS_DIR / "assets" / "cleaned_ioc_stations.csv", index=False)

    stats_with_removed_ratio = get_removed_ratio(stats)

    kamchatka_tsunamis = detect_tsunamis(stats.ioc_code.tolist(), KAMCHATKA_START, KAMCHATKA_END)
    tonga_tsunamis = detect_tsunamis(stats.ioc_code.to_list(), TONGA_START, TONGA_END)

    make_tsunami_map(kamchatka_tsunamis, ioc, "Kamchatka")
    make_tsunami_map(tonga_tsunamis, ioc, "Tonga")
    make_cleaned_stations_map(ioc, stats.ioc_code.to_list())
    make_cleaned_ratio_map(stats_with_removed_ratio)
    make_availability_heatmap(stats, SURGE_DIR)

    make_hist(
        stats_with_removed_ratio,
        "availability",
        "Data availability after cleaning, from 0 to 1 (or 100%)",
        "data_availability_hist.html",
        **HIST,
    )
    make_hist(
        stats_with_removed_ratio,
        "cleaned_ratio",
        "Data removed, from 0 to 1 (or 100%)",
        "data_removed_hist.html",
        **HIST,
    )
    make_bar(
        stats,
        ioc,
        "ocean",
        f"Repartition of the {len(stats)} cleaned stations across oceans",
        "coverage_oceans.html",
    )


if __name__ == "__main__":
    main()

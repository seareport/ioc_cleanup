from __future__ import annotations

import holoviews as hv
import pandas as pd
import panel as pn
import pytest
from holoviews import DynamicMap
from holoviews import Overlay

import ioc_cleanup as C
import ioc_cleanup._plots as P
import ioc_cleanup._tools as T

pn.extension()
hv.extension("bokeh")


IOC_SAMPLE = pytest.mark.parametrize(
    "station",
    [
        pytest.param("abur", id="abur"),
        pytest.param("bres", id="bres"),
    ],
)
DEMEAN = True
YEAR = 2020
YEARS = [2020, 2021]
EPS = 1e-6
IOC = C.get_meta()


@pytest.fixture(scope="session")
def data_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("data")


## Testing download
@IOC_SAMPLE
def test_download_station_data(station, data_dir):
    for year in YEARS:
        C.download_year_station(station, year, data_folder=data_dir)


## Testing cleaning
@IOC_SAMPLE
def test_load_clean_ts_for_year_demean(station, data_dir):
    series = C.load_clean_ts_for_year(
        station=station,
        sensor="rad",
        year=YEAR,
        folder=data_dir,
        demean=True,
    )

    assert isinstance(series, pd.Series)
    assert not series.empty

    meta = C.get_meta()
    meta_row = meta[meta.ioc_code == station]
    stats = C.calc_station_statistics(meta_row, "rad", series)

    assert isinstance(stats, dict)


## Testing the dashboard functions
def test_ui_widgets_exist():
    assert isinstance(P.UI.year, pn.widgets.IntInput)
    assert isinstance(P.UI.surge, pn.widgets.Checkbox)
    assert isinstance(P.UI.demean, pn.widgets.Checkbox)
    assert isinstance(P.UI.station_sensor, pn.widgets.Select)
    assert isinstance(P.UI.apply, pn.widgets.Button)


def test_plot_geographic_coverage_smoke():
    plot = P.plot_geographic_coverage(IOC, ["abur", "abed", "bres"])
    assert isinstance(plot, DynamicMap | Overlay)


def _series():
    return pd.Series(
        [1.0, 2.0, 3.0],
        index=pd.date_range("2020-01-01", periods=3, freq="h"),
    )


def test_print_all_points():
    box = pn.widgets.TextAreaInput()
    P.print_all_points(_series(), [0, 2], box)
    assert "2020-01-01T00:00:00" in box.value


def test_print_range():
    box = pn.widgets.TextAreaInput()
    P.print_range(_series(), [0, 2], box)
    assert box.value.startswith('["2020-01-01T00:00:00"')


def test_print_segment():
    box = pn.widgets.TextAreaInput()
    P.print_segment(_series(), [0, 2], box)
    assert '"offset"' in box.value


def test_get_notes():
    notes = P.get_notes("adak", "wls")
    assert notes == "After 2022-11 it is good. Before that too many spikes"


def test_transformation_ioc_code_matches_filename():
    paths = C._tools.get_transformation_paths()
    for path in sorted(paths):
        station, sensor = path.stem.rsplit("_", 1)
        t = C.load_transformation(station, sensor)
        assert station == t.ioc_code
        assert sensor == t.sensor


@IOC_SAMPLE
def test_load_surge_tide_switch(station, data_dir):
    clean = P.load_surge_tide(station, "rad", 2020, surge=False, demean=True, folder=data_dir)
    surge = P.load_surge_tide(station, "rad", 2020, surge=True, demean=True, folder=data_dir)
    opts = T.OPTS
    lat = IOC[IOC.ioc_code == station].lat.values[0]
    opts["lat"] = lat
    surge2 = T.surge(clean, opts, T.RESAMPLE)
    pd.testing.assert_series_equal(surge, surge2, rtol=1e-3)

from __future__ import annotations

import asyncio
import typing as T
from pathlib import Path

import holoviews as hv
import holoviews.streams
import pandas as pd
import panel as pn
import param

from . import _searvey
from . import _tools


def apply_callback(event: param.parameterized.Event) -> None:
    location = pn.state.location
    if location is not None:
        location._update_synced(event)


class UI:
    year: T.Any = pn.widgets.IntInput(
        name="Select Year",
        value=2020,
        start=2020,
        step=1,
        width=200,
    )
    surge: T.Any = pn.widgets.Checkbox(
        name="Detide Signal",
        value=False,
    )
    demean: T.Any = pn.widgets.Checkbox(
        name="Demean between breakpoints",
        value=True,
    )
    station_sensor: T.Any = pn.widgets.Select(
        name="Station and Sensor from the json list",
        options=_tools.get_station_names(),
        value=None,
        width=200,
    )
    apply: T.Any = pn.widgets.Button(
        name="Apply",
        button_type="primary",
        # Button has no ``color`` param in this Panel version; use a stylesheet
        # to give it a custom hex color (background + hover + border).
        stylesheets=[
            """
            :host { --design-primary-color: #0f7a74; }
            .bk-btn.bk-btn-primary {
                background-color: #0f7a74;
                border-color: #0f7a74;
                color: white;
            }
            .bk-btn.bk-btn-primary:hover {
                background-color: #0c635e;
                border-color: #0c635e;
            }
            """,
        ],
    )
    apply.on_click(apply_callback)


def plot_geographic_coverage(
    meta: pd.DataFrame,
    ioc_codes: list[str],
    title: str = "Geographic distribution of stations",
) -> hv.DynamicMap:
    stations_bad = meta[~meta.ioc_code.isin(ioc_codes)]
    stations_good = meta[meta.ioc_code.isin(ioc_codes)]
    plot_bad = stations_bad.hvplot.points(
        x="lon",
        y="lat",
        geo=True,
        tiles=True,
        color="red",
        hover=False,
        use_index=False,
        label="low",
    )
    plot_good = stations_good.hvplot.points(
        x="lon",
        y="lat",
        geo=True,
        tiles=True,
        color="green",
        hover_cols=["location", "country", "ioc_code", "sensor"],
        label="high",
    )
    return (plot_bad * plot_good).opts(title=title)


# Create a function to print selected points
def print_all_points(df: pd.Series, indices: list[int], text_box: pn.widgets.TextAreaInput) -> T.Any:
    if indices:
        indices = sorted(indices)
        timestamps = [f'    "{df.index[id_].strftime("%Y-%m-%dT%H:%M:%S")}"' for id_ in indices]
        value = ",\n".join(timestamps)
    else:
        value = "No selection!"
    text_box.value = value


def print_range(df: pd.Series, indices: list[int], text_box: pn.widgets.TextAreaInput) -> T.Any:
    if indices:
        indices = sorted(indices)
        first_ts = df.index[indices[0]].strftime("%Y-%m-%dT%H:%M:%S")
        last_ts = df.index[indices[-1]].strftime("%Y-%m-%dT%H:%M:%S")
        value = f'["{first_ts}", "{last_ts}"],'
    else:
        value = "No selection!"
    text_box.value = value


def print_segment(df: pd.Series, indices: list[int], text_box: pn.widgets.TextAreaInput) -> T.Any:
    if indices:
        first_ts = df.index[indices[0]].strftime("%Y-%m-%dT%H:%M:%S")
        last_ts = df.index[indices[-1]].strftime("%Y-%m-%dT%H:%M:%S")
        mean = df.iloc[indices[0] : indices[-1]].mean()

        value = "{\n"
        value += f'  "start": "{first_ts}",\n'
        value += f'  "end": "{last_ts}",\n'
        value += f'  "offset": {mean},\n'
        value += '  "scale_factor": 1.0\n'
        value += "}"
    else:
        value = "No selection!"
    text_box.value = value


def get_notes(station: str, sensor: str) -> str:
    trans = _tools.load_transformation_from_path(
        f"./transformations/{station}_{sensor}.json",
    )
    return trans.notes if trans.notes else "No notes"


def load_surge_tide(
    station: str,
    sensor: str,
    year: int,
    *,
    surge: bool,
    demean: bool,
    folder: Path = Path("./data"),
) -> pd.Series:
    if surge:
        return _tools.load_surge_ts_for_year(
            station,
            sensor,
            year,
            folder,
            demean=demean,
        )
    else:
        return _tools.load_clean_ts_for_year(
            station,
            sensor,
            year,
            folder,
            demean=demean,
        )


def plot_line(df: pd.Series) -> hv.Curve:
    return df.hvplot.line(
        tools=["hover", "crosshair", "undo"],
        grid=True,
        alpha=0.5,
        c="r",
        ylabel="Water level (m)",
    ).opts(
        responsive=True,
        ylim=(df.min() * 1.001, df.max() * 1.001),
    )


def plot_points(df: pd.Series) -> hv.Scatter:
    return df.hvplot.scatter(
        tools=["box_select"],
    ).opts(
        active_tools=["box_zoom"],
        color="gray",
        size=2,
        selection_color="red",
        selection_alpha=1.0,
        nonselection_color="gray",
        nonselection_alpha=0.45,
        responsive=True,
    )


def select_points() -> T.Any:
    def plot_dashboard(_event: T.Any) -> T.Any:
        year = UI.year.value
        surge = UI.surge.value
        demean = UI.demean.value
        station_sensor = UI.station_sensor.value
        station, sensor = station_sensor.split("_")

        points_all = pn.widgets.TextAreaInput(value="", height=200, placeholder="Selected indices will appear here")
        points_range = pn.widgets.TextAreaInput(value="", height=200, placeholder="Selected indices will appear here")
        segment = pn.widgets.TextAreaInput(value="", height=200, placeholder="Selected indices will appear here")
        notes = pn.pane.Markdown("Notes inserted in the JSON will appear here")
        error = pn.pane.Markdown("If there is any Error, it will appear here")

        try:
            df = load_surge_tide(station, sensor, year, surge=surge, demean=demean)
            notes.object = get_notes(station, sensor)
            if df.empty:
                ts = pd.date_range(f"{year}", f"{year+1}", freq="24h")
                df = pd.Series([0.0] * len(ts), index=ts)
                error.object = (
                    "<span style='color:red;'>Empty TS, no data for this year. Check start/end in JSON</span>"
                )

            curve = plot_line(df)
            points = plot_points(df)
            selection = holoviews.streams.Selection1D(source=points)
            selection.add_subscriber(lambda index: print_range(df=df, indices=index, text_box=points_range))
            selection.add_subscriber(lambda index: print_all_points(df=df, indices=index, text_box=points_all))
            selection.add_subscriber(lambda index: print_segment(df=df, indices=index, text_box=segment))

            ioc = _searvey.get_meta()
            item = ioc[ioc.ioc_code == station].iloc[0]
            plot = (curve * points).opts(
                title=f"{item.location} ({item.country}) - ioc_code: {item.ioc_code}, sensor: {sensor}",
            )

        except Exception as e:
            ts = pd.date_range(f"{year}", f"{year+1}", freq="24h")
            df = pd.Series([0.0] * len(ts), index=ts)
            hv_ = T.cast(T.Any, df).hvplot
            plot = hv_.line() * hv_.scatter()
            error.object = f"<span style='color:red;'>{e}</span>"

        return pn.Column(
            pn.Row(
                pn.pane.HoloViews(plot.opts(responsive=True), sizing_mode="stretch_width", height=700),
                width_policy="max",
            ),
            pn.Row(
                pn.Column("## Selected Indices:", points_all),
                pn.Column("## Selected Ranges:", points_range),
                pn.Column("## Segment info:", segment),
                pn.Column("## Notes:", notes),
            ),
            pn.Row(
                pn.Column("## Error:", error),
            ),
        )

    def _spinner(message: str) -> pn.Column:
        return pn.Column(
            pn.indicators.LoadingSpinner(
                value=True,
                size=60,
                color="primary",
                name=message,
                stylesheets=[":host { --primary-bg-color: #0f7a74; }"],
            ),
            align="center",
            sizing_mode="stretch_width",
        )

    async def dashboard_view(_apply: T.Any) -> T.Any:
        # Async generator: each ``yield`` updates the displayed pane. Show a
        # spinner first, load the (cached) metadata off the event loop, then show
        # a second spinner while the plot/detide analysis is built in a worker
        # thread, and finally yield the dashboard. Running the heavy work off the
        # event loop lets the intermediate spinner actually render.
        yield _spinner("Loading IOC station metadata…")
        await asyncio.to_thread(_searvey.get_meta)

        message = "Running detide analysis…" if UI.surge.value else "Loading data…"
        yield _spinner(message)
        result = await asyncio.to_thread(plot_dashboard, _apply)
        yield result

    main = pn.Column(
        pn.bind(dashboard_view, UI.apply),
        min_height=700,
        sizing_mode="stretch_width",
    )

    page = pn.template.FastListTemplate(
        sidebar_width=250,
        title="IOC Cleanup dashboard",
        header_background="#0f7a74",
        accent_base_color="#0f7a74",
        sidebar=[
            UI.station_sensor,
            UI.year,
            UI.surge,
            UI.demean,
            UI.apply,
        ],
        main=main,
    )

    return page.servable()

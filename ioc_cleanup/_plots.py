from __future__ import annotations

import functools
import operator
import typing as T

import holoviews as hv
import holoviews.streams
import pandas as pd
import panel as pn


def plot_geographic_coverage(
    meta: pd.DataFrame,
    ioc_codes: list[str],
    title: str = "Geographic distribution of stations",
) -> hv.DynamicMap:
    stations_bad = meta[~meta.ioc_code.isin(ioc_codes)]
    stations_good = meta[meta.ioc_code.isin(ioc_codes)]
    plot_bad = stations_bad.hvplot.points(geo=True, tiles=True, color="red", hover=False, use_index=False, label="low")
    plot_good = stations_good.hvplot.points(
        geo=True,
        tiles=True,
        color="green",
        hover_cols=["location", "country", "ioc_code", "sensor"],
        label="high",
    )
    return (plot_bad * plot_good).opts(title=title)


# Create a function to print selected points
def print_all_points(df: pd.DataFrame, indices: pd.Index[int]) -> None:
    if indices:
        print([p.isoformat() for p in df.iloc[indices].index.to_list()])  # noqa: T201
    else:
        print("No selection!")  # noqa: T201


def print_range(df: pd.DataFrame, indices: pd.Index[int]) -> None:
    if indices:
        first_ts = df.index[indices[0]]
        last_ts = df.index[indices[-1]]
        print(f'("{first_ts}", "{last_ts}"),')  # noqa: T201
    else:
        print("No selection!")  # noqa: T201


def select_points(df: pd.DataFrame) -> T.Any:
    curve = df.hvplot.line(tools=["hover", "crosshair", "undo"], grid=True)
    points = df.hvplot.scatter(tools=["box_select"]).opts(
        color="gray",
        active_tools=["box_zoom"],
        nonselection_color="gray",
        selection_color="red",
        selection_alpha=1.0,
        nonselection_alpha=0.3,
        size=1,
    )
    selection = holoviews.streams.Selection1D(source=points)

    button_all = pn.widgets.Button(name="Print All Points", button_type="primary")  # type: ignore[no-untyped-call]
    button_all.on_click(lambda _: print_all_points(df=df, indices=selection.index))

    button_range = pn.widgets.Button(name="Print Range", button_type="primary")  # type: ignore[no-untyped-call]
    button_range.on_click(lambda _: print_range(df=df, indices=selection.index))

    plot = curve * points
    layout = pn.Column(plot.opts(width=1600, height=500), pn.Row(button_all, button_range))
    out = pn.panel(layout).servable()
    return out


def compare_dataframes(*dataframes: T.Sequence[pd.DataFrame], title: str = "") -> hv.Layout:
    assert len(dataframes) > 1, "You must pass at least two dataframes!"
    title = title or ""
    options = {
        "tools": ["crosshair", "hover", "undo"],
        "active_tools": ["box_zoom"],
        "width": 1200,
        "height": 500,
        "show_grid": True,
    }
    renamed: list[pd.DataFrame] = []
    for i, df in enumerate(dataframes):
        assert isinstance(df, pd.DataFrame)
        renamed.append(df.rename(columns=({f"{df.columns[0]}": f"{df.attrs['ioc_code']}_{df.attrs['sensor']}_{i}"})))
    plots = functools.reduce(
        operator.add,
        (df.hvplot.line().opts(**options) for df in renamed),
    )
    layout = T.cast(hv.Layout, hv.Layout(plots).cols(1).opts(title=title))
    return layout

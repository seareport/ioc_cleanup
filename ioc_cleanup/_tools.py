from __future__ import annotations

import os

import numpy as np
import pandas as pd

from . import _constants
from . import _models


def dump_transformation(
    trans: _models.Transformation,
    dest_dir: str | os.PathLike[str] = _constants.TRANSFORMATIONS_DIR,
) -> None:
    path = f"{dest_dir}/{trans.ioc_code}_{trans.sensor}.json"
    with open(path, "w") as fd:
        fd.write(trans.model_dump_json(indent=2, round_trip=True))


def load_transformation(
    ioc_code: str,
    sensor: str,
    src_dir: str | os.PathLike[str] = _constants.TRANSFORMATIONS_DIR,
) -> _models.Transformation:
    path = f"{src_dir}/{ioc_code}_{sensor}.json"
    return load_transformation_from_path(path)


def load_transformation_from_path(path: str | os.PathLike[str]) -> _models.Transformation:
    with open(path) as fd:
        contents = fd.read()
    model = _models.Transformation.model_validate_json(contents)
    return model


def transform(df: pd.DataFrame, transformation: _models.Transformation | None = None) -> pd.DataFrame:
    df = df.copy()
    if transformation is None:
        transformation = load_transformation(ioc_code=df.attrs["ioc_code"], sensor=df.attrs["sensor"])
    df = df[transformation.start : transformation.end]  # type: ignore[misc]  # https://stackoverflow.com/questions/70763542/pandas-dataframe-mypy-error-slice-index-must-be-an-integer-or-none
    for start, end in transformation.dropped_date_ranges:
        df[start:end] = np.nan  # type: ignore[misc]  # https://stackoverflow.com/questions/70763542/pandas-dataframe-mypy-error-slice-index-must-be-an-integer-or-none
    if transformation.dropped_timestamps:
        df.loc[transformation.dropped_timestamps] = np.nan  # type: ignore[call-overload]
    for segment in transformation.segments:
        if segment.scale_factor != 1:
            df[segment.start : segment.end] *= segment.scale_factor  # type: ignore[misc]  # https://stackoverflow.com/questions/70763542/pandas-dataframe-mypy-error-slice-index-must-be-an-integer-or-none
        if segment.offset != 0:
            df[segment.start : segment.end] += segment.offset  # type: ignore[misc]  # https://stackoverflow.com/questions/70763542/pandas-dataframe-mypy-error-slice-index-must-be-an-integer-or-none
    df.attrs["status"] = "transformed"
    return df


def get_segment(df: pd.DataFrame, segment_index: int) -> pd.DataFrame:
    df = df.copy()
    trans = load_transformation(df.attrs["ioc_code"], df.attrs["sensor"])
    if segment_index > len(trans.segments):
        raise ValueError("Undefined semgent: %s", segment_index)
    segment = trans.segments[segment_index]
    df = df.loc[segment.start : segment.end]  # type: ignore[misc]  # https://stackoverflow.com/questions/70763542/pandas-dataframe-mypy-error-slice-index-must-be-an-integer-or-none
    return df

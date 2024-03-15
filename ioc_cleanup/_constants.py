from __future__ import annotations

import pathlib

import pandas as pd

SPLIT_DIR = pathlib.Path("split")
TRANSFORMATIONS_DIR = pathlib.Path("transformations")

DETIDE_START = pd.Timestamp("2022-01-01T00:00:00")
DETIDE_END = pd.Timestamp("2023-12-31T23:59:59")

SIMULATION_START = pd.Timestamp("2023-07-01T00:00:00")
SIMULATION_END = pd.Timestamp("2023-10-31T23:59:59")

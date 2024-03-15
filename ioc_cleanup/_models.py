from __future__ import annotations

import datetime

import pydantic


class Segment(pydantic.BaseModel):
    start: datetime.datetime
    end: datetime.datetime
    offset: float = 0.0
    scale_factor: float = 1.0


class Transformation(pydantic.BaseModel):
    ioc_code: str
    sensor: str
    notes: str = ""
    skip: bool = False
    start: datetime.datetime
    end: datetime.datetime
    high: float | None = None
    low: float | None = None
    dropped_date_ranges: list[tuple[datetime.datetime, datetime.datetime]] = []
    dropped_timestamps: list[datetime.datetime] = []
    segments: list[Segment] = []

    # model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

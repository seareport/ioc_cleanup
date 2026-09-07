from __future__ import annotations

import logging

import ioc_cleanup as C

logger = logging.getLogger(__name__)

YEARS = [2020, 2021, 2022, 2023, 2024, 2025]


def main():
    for code in C.get_meta().ioc_code:
        text = f"\n{code}"
        for year in YEARS:
            try:
                C.download_year_station(code, year, data_folder="./data")
                text += f" {year}"
            except Exception:
                text += " x"
        logger.info(text)


if __name__ == "__main__":
    main()

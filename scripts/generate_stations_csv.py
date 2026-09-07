from __future__ import annotations

import logging
from pathlib import Path

import ioc_cleanup as C

logger = logging.getLogger(__name__)

DOCS_DIR = Path("docs/assets")


def main():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    ioc = C.get_meta()
    stats = C.calc_statistics(ioc, stations_dir=C.TRANSFORMATIONS_DIR, pattern="*.json")

    out = DOCS_DIR / "cleaned_ioc_stations.csv"
    stats.to_csv(out, index=False)
    logger.info("Wrote %d stations to %s", len(stats), out)


if __name__ == "__main__":
    main()

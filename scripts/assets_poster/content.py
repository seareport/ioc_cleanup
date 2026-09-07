from __future__ import annotations

LEFT_TOP_TEXT = """
# Reproducible, transparent and traceable cleaning of IOC Tide Gauge Data

### Thomas Saillour<sup>1</sup> and Panagiotis Mavrogiorgos<sup>1</sup>

_<sup>1</sup>European Commission, Joint Research Center, DG JRC.E.1, Italy_
"""

LEFT_MID_TEXT = """
## Concept: Declarative cleaning

Tide gauge data from [IOC sea-level monitoring](https://www.ioc-sealevelmonitoring.org/list.php)
is widely used for storm-surge validation, tsunami detection and sea-level research.
Yet, the cleaning step is typically:

 * ❌ **Manual** - bespoke scripts per analyst
 * ❌ **Poorly documented** - decisions are rarely recorded
 * ❌ **Hard to reproduce** - no shared format or audit trail
 * ❌ **Difficult to review** - impossible to peer-review

**ioc_cleanup** proposes a **community-driven, version-controlled** method
where every cleaning transformation is stored in a plain **JSON transformation file**:

 * ✅ Explicit & human-readable
 * ✅ Version-controlled on GitHub
 * ✅ Fully reproducible
 * ✅ Open to peer review via pull requests
"""
LEFT_BOTTOM_TEXT = """
<style>
table {
    width: 100% !important;
}
table td, table th {
    text-align: left !important;
}
</style>

### What can be flagged & how

| Artefact type | Description | Action |
|---|---|---|
| Spikes | Individual erroneous timestamps | → **dropped_timestamps** |
| Bad ranges | Continuous corrupt data windows | → **dropped_date_ranges** |
| Breakpoints | Sensor regime changes / recalibrations | → **breakpoints** |
| Physical events | Tsunamis, seiches, meteo-tsunamis | → **tsunami** (keep, don't drop) |
| Flat signal | Frozen / stuck sensors | → **dropped_date_ranges** |
| DST steps | Daylight saving time artefacts | → **dropped_date_ranges** |
| Ambiguous | Nature of noise unclear | **Do nothing** |


### Details

- **Period:** 1 Jan 2020 - 31 Dec 2025
- **Sources:** 445 stations of IOC Global Sea-Level Monitoring network
- Details, docs and data can be found directly on the [GitHub page](https://github.com/oceanmodeling/ioc_cleanup) (flash the QR code)
"""

RIGHT_TEXT = """
### Installation
```bash
git clone https://github.com/seareport/ioc_cleanup.git
pip install -r requirements.txt
```
### Minimal Usage

```python
import searvey
import ioc_cleanup as C

df_raw = searvey.fetch_ioc_station("maya", "2020", "2026")
trans  = C.load_transformation_from_path(
    "transformations/maya_pwl.json"
)
df_clean = C.transform(df_raw, trans)
```
## Come and join the cleaning!
1. **Fork** the repository on GitHub
2. **Add or update** a JSON transformation file
3. Use the **interactive dashboard** to inspect and flag data
4. **Submit a pull request** with a clear description

## Futures plans
 * expand the database
 * apply the method to other datasets
 * let machines do the work

## Aknowledgements
 * EC JRC for funding and support
 * The [oceanmodeling](https://github.com/oceanmodeling) github community for help and feedback

## Bonus
This **poster** was entirely **generated with python** !

"""

JSON_TRANSFORMATION = """
### JSON Transformation Example:
```json
{
  "ioc_code": "maya",
  "sensor": "pwl",
  "notes": "lots of step values from numerical noise",
  "skip": false,
  "wip": false,
  "start": "2020-01-01T00:00:00",
  "end": "2026-01-01T00:00:00",
  "high": null,
  "low": null,
  "dropped_date_ranges": [
    ["2022-03-14T02:30:00", "2022-03-14T02:32:00"],
    ["2022-05-27T17:00:00", "2022-05-27T17:03:00"],
    ["2022-07-27T09:36:00", "2022-07-27T09:40:00"],
    ["2022-07-28T06:06:00", "2022-07-28T06:09:00"],

  ],
  "dropped_timestamps": [
    "2020-10-17T14:12:00",
    "2020-10-17T14:13:00",
    "2020-10-17T14:14:00"

  ],
  "breakpoints": [],
  "tsunami": []
}
```
"""

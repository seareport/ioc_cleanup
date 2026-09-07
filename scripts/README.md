This folder contains 3 helper functions:
 1. `download_ioc.py` to download IOC stations
 2. `generate_maps.py` to create maps and graphs for the online documentation
 3. `save_cleaning_scenarios.py` to create the time series graphs used in the online documentation

Steps 2 and 3 require to have run step 1 for all cleaned IOC stations.

The cleaned stations dataset can be retrieved with:

```python
import ioc_cleanup as C
ioc = C.get_meta()
stats = C.calc_statistics(ioc, stations_dir=C.TRANSFORMATIONS_DIR, pattern="*.json")
```

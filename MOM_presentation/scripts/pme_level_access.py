"""pme_level_access -- share of employed PMEs with at least one of the five FWAs available (ticked, or currently used), by job level.

Reads employee.dta (read only); writes data/pme_level_access.csv.  usage: python3 pme_level_access.py DIR_WITH_employee.dta
Level codes: 1 junior professional / specialist, 2 middle management, 3 senior management.
Five FWAs: working from home (ad hoc, scheduled or remote-first), staggered hours, compressed week, job sharing, part-time.
"""
import sys
from pathlib import Path

import pandas as pd

MOM = Path(__file__).resolve().parents[1]
d = pd.read_stata(Path(sys.argv[1]) / "employee.dta", convert_categoricals=False).drop_duplicates("id")
d = d[d.empstat.isin([1, 2])]
use = d.remote.isin([2, 3, 4]) | d.schedule.isin([2, 3]) | d.workload.isin([2, 3])
tick = d[["fwa_adhoc", "fwa_schedremote", "fwa_fullremote", "fwa_staggered", "fwa_compressed", "fwa_parttime",
          "fwa_jobshare"]].max(axis=1) == 1
d = d.assign(avail_any=(tick | use).astype(float), use_any=use.astype(float))
out = d.groupby("level").agg(n=("id", "size"), avail_any=("avail_any", "mean"), use_any=("use_any", "mean")).reset_index()
out[["avail_any", "use_any"]] *= 100
out.round(2).to_csv(MOM / "data" / "pme_level_access.csv", index=False)
print(out.round(1).to_string(index=False))

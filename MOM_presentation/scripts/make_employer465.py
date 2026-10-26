"""make_employer465 -- turn Dropbox final/employer.dta (employer survey after the 26 Oct 2026 update: 303 original firms + 162 from
snef.dta, 465 firms, 5,580 choice rows) into the layout the Python port reads (it was written for snef_employer_appended.dta):
the same columns plus id_new, choice_set_new and source (= `data`: 0 original panel, 1 SNEF list).  Read only on the Dropbox side.
usage: python3 make_employer465.py FINAL/employer.dta OUT/appended.dta
"""
import sys

import pandas as pd

d = pd.read_stata(sys.argv[1], convert_categoricals=False)
assert d["id"].nunique() == 465 and len(d) == 5580, (d["id"].nunique(), len(d))
d["id_new"] = d["id"]
d["choice_set_new"] = d["choice_set"]
d["source"] = d["data"].astype(float)
d.to_stata(sys.argv[2], write_index=False, version=118)
print("wrote", sys.argv[2], d.shape)

* employer_robustness.do -- employer versions of the three robustness checks the employee side runs in code_final.do
* Paste after the "main" employer block (it needs $data, $res, $table and $res/org_main.dta, $res/ymap_org.dta).
* Same model and WTP formula as the employer main model; group 0 = main (org_main.dta), group 1 = robustness sample.

**robustness check (employer)
//exclude salary outliers (monthly salary outside S$2,000-50,000)
tempname h
postfile `h' group str24 term double wtp double se double z double p double lb double ub ///
    using "$res/org_outlier.dta", replace

use "$data/employer.dta", clear
capture drop collaborative
gen collaborative = (jobculture == 2) if !missing(jobculture)

clogit chosen log_salary ib0.place ib0.timeflex ib0.load ib0.retention ib1.collaborative ///
    if salary_out == 0, group(choice_set) vce(cluster id)

matrix T = r(table)'
matrix T = T[1..., 1..6]
putexcel set "$table/employer_clogit.xlsx", sheet("robust_outlier", replace) modify
putexcel A1 = matrix(T), names nformat("0.000")
putexcel I1 = "N observations" J1 = (e(N))
putexcel I2 = "N respondents"  J2 = (e(N_clust))
putexcel clear

foreach t in 1.place 2.place 3.place 1.timeflex 2.timeflex 1.load 2.load 1.retention 2.retention {
    quietly nlcom (100*(exp(-_b[`t'] / _b[log_salary]) - 1))
    matrix W = r(table)
    post `h' (1) ("`t'") (W[1,1]) (W[2,1]) (W[3,1]) (W[4,1]) (W[5,1]) (W[6,1])
}
postclose `h'

use "$res/org_outlier.dta", clear
append using "$res/org_main.dta"
sort group term
export excel using "$table/employer_wtp.xlsx", sheet("robust_outlier", replace) firstrow(variables)


//exclude top/bottom 1% of current salary (percentiles over respondents, as on the employee side)
tempname h
postfile `h' group str24 term double wtp double se double z double p double lb double ub ///
    using "$res/org_trim.dta", replace

use "$data/employer.dta", clear
capture drop collaborative
gen collaborative = (jobculture == 2) if !missing(jobculture)

gen double base_salary_num = real(base_salary_orig)     // base_salary_orig is a string in employer.dta
egen byte tag_id = tag(id)
summarize base_salary_num if tag_id == 1, detail
local p1  = r(p1)
local p99 = r(p99)
gen salary_trim = inrange(base_salary_num, `p1', `p99') if !missing(base_salary_num)

clogit chosen log_salary ib0.place ib0.timeflex ib0.load ib0.retention ib1.collaborative ///
    if salary_trim == 1, group(choice_set) vce(cluster id)

matrix T = r(table)'
matrix T = T[1..., 1..6]
putexcel set "$table/employer_clogit.xlsx", sheet("robust_trim", replace) modify
putexcel A1 = matrix(T), names nformat("0.000")
putexcel I1 = "N observations" J1 = (e(N))
putexcel I2 = "N respondents"  J2 = (e(N_clust))
putexcel clear

foreach t in 1.place 2.place 3.place 1.timeflex 2.timeflex 1.load 2.load 1.retention 2.retention {
    quietly nlcom (100*(exp(-_b[`t'] / _b[log_salary]) - 1))
    matrix W = r(table)
    post `h' (1) ("`t'") (W[1,1]) (W[2,1]) (W[3,1]) (W[4,1]) (W[5,1]) (W[6,1])
}
postclose `h'

use "$res/org_trim.dta", clear
append using "$res/org_main.dta"
sort group term
export excel using "$table/employer_wtp.xlsx", sheet("robust_trim", replace) firstrow(variables)


//exclude same-side respondents (always chose option 1 or always option 2)
tempname h
postfile `h' group str24 term double wtp double se double z double p double lb double ub ///
    using "$res/org_side.dta", replace

use "$data/employer.dta", clear
capture drop collaborative
gen collaborative = (jobculture == 2) if !missing(jobculture)
bysort id: egen byte same_side_all = max(same_side)     // same_side is only filled on the tag row

clogit chosen log_salary ib0.place ib0.timeflex ib0.load ib0.retention ib1.collaborative ///
    if same_side_all == 0, group(choice_set) vce(cluster id)

matrix T = r(table)'
matrix T = T[1..., 1..6]
putexcel set "$table/employer_clogit.xlsx", sheet("robust_same_side", replace) modify
putexcel A1 = matrix(T), names nformat("0.000")
putexcel I1 = "N observations" J1 = (e(N))
putexcel I2 = "N respondents"  J2 = (e(N_clust))
putexcel clear

foreach t in 1.place 2.place 3.place 1.timeflex 2.timeflex 1.load 2.load 1.retention 2.retention {
    quietly nlcom (100*(exp(-_b[`t'] / _b[log_salary]) - 1))
    matrix W = r(table)
    post `h' (1) ("`t'") (W[1,1]) (W[2,1]) (W[3,1]) (W[4,1]) (W[5,1]) (W[6,1])
}
postclose `h'

use "$res/org_side.dta", clear
append using "$res/org_main.dta"
sort group term
export excel using "$table/employer_wtp.xlsx", sheet("robust_same_side", replace) firstrow(variables)

* Expected (Python port, wtp = pay cut %): outlier N=460 resp: 1-2d 19.7, 3-4d 39.7, remote 52.0, staggered 8.8, compressed 10.8, jobshare 25.9, part-time 37.5
*   trim N=458: 19.8 / 39.6 / 52.2 / 8.7 / 10.1 / 26.1 / 37.4;  same-side N=446: 18.8 / 39.0 / 50.4 / 10.1 / 8.8 / 25.9 / 36.2

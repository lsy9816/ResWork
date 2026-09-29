* 육아휴직 그림 (parental_leave.xlsx 기준)
* female: 0 = 아빠, 1 = 엄마, 2 = 전체 / number = 수급자 수 / pct = 사용률(%)

import excel "parental_leave.xlsx", sheet("Sheet2") firstrow clear
reshape wide number pct, i(year) j(female)        // 0 = 아빠, 1 = 엄마, 2 = 전체
replace number2 = number0 + number1 if year == 2025  // 2025년 전체 비어 있음
drop if year == 2001                                 // 2001년은 11~12월 2개월분
foreach v in 0 1 2 {
    replace number`v' = number`v' / 1000             // 천 명 단위
}
gen share = 100 * number0 / number2                  // 수급자 중 아빠 비중

set scheme s1color
graph set window fontface "Arial"

* 1. 수급자 수: 아래 파랑 = 아빠, 위 빨강 = 엄마, 검정 선 = 전체
twoway (area number2 year, color("204 51 99%40") lwidth(none)) ///
       (area number0 year, color("0 114 178%70") lwidth(none)) ///
       (connected number2 year, lcolor(black) mcolor(black) msize(vsmall)), ///
    ylabel(0(50)200, angle(0)) xlabel(2002 2005(5)2025) ytitle("") xtitle("") ///
    legend(order(3 "Total" 1 "Mothers" 2 "Fathers") rows(1) pos(6)) ///
    title("Parental Leave Benefit Recipients (thousands)")
graph export "fig1_recipients.png", width(2400) replace

* 2. 수급자 중 아빠 비중
twoway connected share year, lcolor("0 114 178") mcolor("0 114 178") msize(small) ///
    ylabel(0(10)40, angle(0)) xlabel(2002 2005(5)2025) ytitle("") xtitle("") ///
    title("Fathers' Share of Benefit Recipients (%)")
graph export "fig2_father_share.png", width(2400) replace

* 3. 출생아 부모 사용률: 엄마/아빠 패널 (y축 따로)
keep if inrange(year, 2010, 2024)
twoway connected pct1 year, lcolor("204 51 99") mcolor("204 51 99") msize(small) ///
    ylabel(0(20)80, angle(0)) xlabel(2010(2)2024) ytitle("") xtitle("") ///
    subtitle("Mothers") name(m, replace) nodraw
twoway connected pct0 year, lcolor("0 114 178") mcolor("0 114 178") msize(small) ///
    ylabel(0(2)12, angle(0)) xlabel(2010(2)2024) ytitle("") xtitle("") ///
    subtitle("Fathers") name(f, replace) nodraw
graph combine m f, cols(2) xsize(8) ysize(4) graphregion(color(white)) ///
    title("Parental Leave Use Rate of Parents of Newborns (%)")
graph export "fig3_userate.png", width(2400) replace

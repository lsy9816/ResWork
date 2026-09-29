* 육아휴직 그림 (parental_leave.xlsx Sheet2 기준)
* female: 0 = 아빠, 1 = 엄마, 2 = 전체
* number1 = 육아휴직급여 수급자 수(고용노동부), number2 = 육아휴직자 수(국가데이터처),
* number3 = 출생아 부모 중 육아휴직자 수(국가데이터처), pct = 출생아 부모 사용률(%), births = 출생아 수

import excel "parental_leave.xlsx", sheet("Sheet2") firstrow clear
rename (number1 number2 number3) (recip users newborn)
reshape wide recip users newborn pct births, i(year) j(female)       // 0 = 아빠, 1 = 엄마, 2 = 전체
replace recip2 = recip0 + recip1 if year == 2025      // 2025년 전체 비어 있음
drop if year == 2001                                   // 2001년은 11~12월 2개월분
foreach v in recip0 recip1 recip2 users0 users1 users2 newborn0 newborn1 newborn2 {
    replace `v' = `v' / 1000                           // 천 명 단위
}

set scheme s1color
graph set window fontface "Arial"

* 1. 사용률: 엄마, 아빠 각각 (y축 따로)
twoway connected pct1 year if inrange(year, 2010, 2024), ///
    lcolor("204 51 99") mcolor("204 51 99") msize(small) ///
    ylabel(0(20)80, angle(0)) xlabel(2010(2)2024) ytitle("") xtitle("") ///
    title("Parental Leave Use Rate of Mothers of Newborns (%)")
graph export "fig1a_userate_mothers.png", width(2400) replace

twoway connected pct0 year if inrange(year, 2010, 2024), ///
    lcolor("0 114 178") mcolor("0 114 178") msize(small) ///
    ylabel(0(2)12, angle(0)) xlabel(2010(2)2024) ytitle("") xtitle("") ///
    title("Parental Leave Use Rate of Fathers of Newborns (%)")
graph export "fig1b_userate_fathers.png", width(2400) replace

* 2. 수급자 수 (고용노동부): 아래 파랑 = 아빠, 위 빨강 = 엄마, 검정 선 = 전체
twoway (area recip2 year, color("204 51 99%40") lwidth(none)) ///
       (area recip0 year, color("0 114 178%70") lwidth(none)) ///
       (connected recip2 year, lcolor(black) mcolor(black) msize(vsmall)), ///
    ylabel(0(50)250, angle(0)) xlabel(2002 2005(5)2025) ytitle("") xtitle("") ///
    legend(order(3 "Total" 1 "Mothers" 2 "Fathers") rows(1) pos(6)) ///
    title("Parental Leave Benefit Recipients (thousands)")
graph export "fig2_recipients.png", width(2400) replace

* 3. 사용자 수 (국가데이터처): 같은 형식, 2010~2024 (2024년 잠정)
twoway (area users2 year, color("204 51 99%40") lwidth(none)) ///
       (area users0 year, color("0 114 178%70") lwidth(none)) ///
       (connected users2 year, lcolor(black) mcolor(black) msize(vsmall)) ///
       if inrange(year, 2010, 2024), ///
    ylabel(0(50)250, angle(0)) xlabel(2010(2)2024) ytitle("") xtitle("") ///
    legend(order(3 "Total" 1 "Mothers" 2 "Fathers") rows(1) pos(6)) ///
    title("Parental Leave Takers (thousands)")
graph export "fig3_users.png", width(2400) replace

* 4. 출생아 부모 중 육아휴직자 수 (국가데이터처): 같은 형식, 2010~2024 (2024년 잠정)
twoway (area newborn2 year, color("204 51 99%40") lwidth(none)) ///
       (area newborn0 year, color("0 114 178%70") lwidth(none)) ///
       (connected newborn2 year, lcolor(black) mcolor(black) msize(vsmall)) ///
       if inrange(year, 2010, 2024), ///
    ylabel(0(20)100, angle(0)) xlabel(2010(2)2024) ytitle("") xtitle("") ///
    legend(order(3 "Total" 1 "Mothers" 2 "Fathers") rows(1) pos(6)) ///
    title("Parental Leave Takers among Parents of Newborns (thousands)")
graph export "fig4_newborn_parents.png", width(2400) replace

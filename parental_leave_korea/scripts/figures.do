*==============================================================================
* 육아휴직 그림 (Stata 15 이상)
*
* 필요한 데이터 (변수: year father mother total)
*   recipients.dta : 고용노동부 육아휴직급여 초회 수급자 수 (명)
*   userate.dta    : 국가데이터처 출생아 부모 육아휴직 사용률 (%)
*
* 출력
*   fig1_recipients.png   수급자 수 (누적 면적: 엄마 + 아빠 = 전체)
*   fig1b_father_share.png 수급자 중 아빠 비중
*   fig1_combined.png     위 두 그림을 위아래로
*   fig2_userate.png      사용률 (엄마 / 아빠 패널, y축 따로)
*==============================================================================
version 15
clear all
graph set window fontface "Arial"    // 그림 안 글자는 영어만 사용 (한글 깨짐 방지)

* 색: 아빠 파랑, 엄마 빨강, 전체 검정
local cF "0 114 178"
local cM "204 51 99"
local cT "40 40 40"

* 공통 스타일
local style graphregion(color(white)) plotregion(color(white)) ///
    xtitle("") ytitle("") legend(off)
local ylopt angle(0) labsize(small) glcolor(gs14) glpattern(solid)
local tsty  size(medium) color(black) position(11) justification(left)
local nsty  size(vsmall) color(gs6) position(7) justification(left)

* 제도 변화 시점 (아빠의 달 2014.10, 첫 3개월 80% 2017.9, 3+3 2022.1, 6+6 2024.1)
local policy xline(2014.75 2017.67 2022 2024, lpattern(dash) lcolor(gs11) lwidth(thin))


*------------------------------------------------------------------------------
* Fig 1. 육아휴직급여 수급자 수
*------------------------------------------------------------------------------
use "recipients.dta", clear
drop if year < 2002                                   // 2001년은 11~12월 2개월분
replace total = father + mother if missing(total)     // 2025년 total 누락 보정

gen f_k   = father/1000
gen t_k   = total/1000
gen share = 100*father/total

* 마지막 해 값 (선 끝 라벨용)
qui sum year
local last = r(max)
qui sum f_k if year == `last'
local f = r(mean)
qui sum t_k if year == `last'
local t = r(mean)
local fL = string(`f',      "%3.0f")
local mL = string(`t' - `f', "%3.0f")
local tL = string(`t',      "%3.0f")
local xl = `last' + 0.4

twoway (area t_k year, fcolor("`cM'%45") lwidth(none))              ///
       (area f_k year, fcolor("`cF'%75") lwidth(none))              ///
       (connected t_k year, lcolor("`cT'") mcolor("`cT'")           ///
            msize(vsmall) lwidth(medthin)),                         ///
    `policy'                                                        ///
    text(205 2014.75 "Daddy month ", size(vsmall) color(gs7) placement(w)) ///
    text(190 2017.67 "80% for first 3 mo. ", size(vsmall) color(gs7) placement(w)) ///
    text(205 2022    "3+3 ", size(vsmall) color(gs7) placement(w))  ///
    text(190 2024    "6+6 ", size(vsmall) color(gs7) placement(w))  ///
    text(`t'             `xl' "Total `tL'k",   size(small) color("`cT'") placement(e)) ///
    text(`=(`t'+`f')/2'  `xl' "Mothers `mL'k", size(small) color("`cM'") placement(e)) ///
    text(`=`f'/2'        `xl' "Fathers `fL'k", size(small) color("`cF'") placement(e)) ///
    ylabel(0(50)200, `ylopt') yscale(range(0 212))                  ///
    xlabel(2002 2005(5)2025, labsize(small)) xscale(range(2002 2029)) ///
    title("Parental Leave Benefit Recipients in Korea (thousands)", `tsty') ///
    note("Source: Ministry of Employment and Labor, first-time recipients of parental leave benefits." ///
         "Dashed lines: policy changes. 2025: monthly benefit cap raised to KRW 2.5 million.", `nsty') ///
    `style' name(fig1, replace)
graph export "fig1_recipients.png", width(2400) replace


*------------------------------------------------------------------------------
* Fig 1b. 수급자 중 아빠 비중 (%)
*------------------------------------------------------------------------------
gen str8 lab = string(share, "%3.1f") + "%" if year == `last'

twoway (connected share year, lcolor("`cF'") mcolor("`cF'") msize(small) ///
            mlabel(lab) mlabpos(3) mlabcolor("`cF'") mlabsize(small)),   ///
    `policy'                                                        ///
    ylabel(0(10)40, `ylopt')                                        ///
    xlabel(2002 2005(5)2025, labsize(small)) xscale(range(2002 2029)) ///
    title("Fathers' Share of Benefit Recipients (%)", `tsty')       ///
    `style' name(fig1b, replace)
graph export "fig1b_father_share.png", width(2400) replace

graph combine fig1 fig1b, cols(1) xcommon imargin(small) ///
    graphregion(color(white)) xsize(6) ysize(8) name(fig1c, replace)
graph export "fig1_combined.png", width(2400) replace


*------------------------------------------------------------------------------
* Fig 2. 출생아 부모 육아휴직 사용률 (%) - 엄마/아빠 패널, y축 따로
*------------------------------------------------------------------------------
use "userate.dta", clear
qui sum year
local first = r(min)
local last  = r(max)

* 첫 해는 왼쪽, 마지막 해는 오른쪽에 값 표시
gen pos = cond(year == `first', 9, 3)
foreach v in mother father {
    gen str8 lab_`v' = string(`v', "%3.1f") + "%" if inlist(year, `first', `last')
}

local xopt xlabel(`first'(2)`last', labsize(small)) ///
           xscale(range(`=`first'-1.8' `=`last'+1.8'))

twoway (connected mother year, lcolor("`cM'") mcolor("`cM'") msize(small) ///
            mlabel(lab_mother) mlabvposition(pos) mlabcolor("`cM'") mlabsize(small)), ///
    ylabel(0(20)80, `ylopt') `xopt'                                  ///
    subtitle("Mothers", size(medsmall) color("`cM'") position(11) justification(left)) ///
    `style' name(g_m, replace) nodraw

twoway (connected father year, lcolor("`cF'") mcolor("`cF'") msize(small) ///
            mlabel(lab_father) mlabvposition(pos) mlabcolor("`cF'") mlabsize(small)), ///
    ylabel(0(2)12, `ylopt') `xopt'                                   ///
    subtitle("Fathers (note the smaller scale)", size(medsmall) color("`cF'") ///
             position(11) justification(left))                       ///
    `style' name(g_f, replace) nodraw

graph combine g_m g_f, cols(2) imargin(small) graphregion(color(white)) ///
    xsize(8) ysize(4)                                                ///
    title("Parental Leave Use Rate among Parents of Newborns (%)", `tsty') ///
    note("Share of parents of babies born in year t who started parental leave in the same year t." ///
         "Source: Statistics Korea, Parental Leave Statistics. Y-axes differ between panels.", `nsty') ///
    name(fig2, replace)
graph export "fig2_userate.png", width(2400) replace

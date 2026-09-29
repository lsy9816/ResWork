# 대한민국 육아휴직 수급자 수·육아휴직 사용률 통계: 전체 목록

작성일: 2026-09-29

> **수집 방법과 한계.** 이 자료를 만든 클라우드 환경에서는 kosis.kr, index.go.kr, data.go.kr, kostat.go.kr, moel.go.kr,
> eis.work24.go.kr, oecd.org, kli.re.kr, kihasa.re.kr 등이 네트워크 정책으로 모두 차단되어 **원자료 파일을 직접 받지 못했습니다.**
> 그래서 웹 검색으로 공식 보도자료와 언론 인용 수치를 모으고, 자료끼리 교차 확인해 `data/*.csv`로 다시 만들었습니다.
> 각 값에는 `검증상태` 열을 달았습니다. 원자료 일괄 다운로드는 `scripts/download_parental_leave_data.py`를
> 한국 사이트에 접속되는 PC에서 KOSIS API 키로 실행하세요.

---

## 1. 데이터 목록 (출처 · 지표 정의 · 데이터 기간)

### A. 행정통계 (전수, 시계열 데이터 있음)

| # | 출처 (작성기관 · 통계명) | 지표 정의 | 데이터 기간 · 주기 | 세부 구분 | 접근 경로 | 이번 수집 결과 |
|---|---|---|---|---|---|---|
| A1 | **고용노동부 「고용보험통계」 육아휴직급여 수급자** (모성보호 지급자 현황) | 해당 기간에 **육아휴직급여를 처음 받은 고용보험 피보험자 수(초회 수급자)**. 언론에서 말하는 "연간 육아휴직자 수"(예: 2024년 132,535명)는 대부분 이 값. 대상은 민간 근로자 중심이며 공무원·사립교원 제외. 급여 수급요건: 피보험단위기간 180일 이상, 30일 이상 휴직 | **2001.11(급여 도입)~현재**, 월별·연별 | 성별, 지역별, 기업규모별, 산업별, 연령별 | 고용행정통계 [모성보호지급자현황(월)](https://eis.work24.go.kr/eisps/rpt/reptDtl.do?menuId=030010020) · KOSIS(고용노동부) · [e-나라지표 1504 「출산 및 육아휴직급여 수급자 현황」](https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1504) · [공공데이터포털 15100479 「성별 지역별 육아휴직급여 수급자수」(월별, 매년 갱신)](https://www.data.go.kr/data/15100479/fileData.do) | 연간 전체·남성 2002~2025, 2026 상반기 재구성 → `data/moel_parental_leave_benefit_recipients_annual.csv` |
| A2 | **국가데이터처(구 통계청) 「육아휴직통계」** (국가승인통계, 2019.12 최초 공표, 매년 12월 잠정 → 이듬해 확정) | ① **육아휴직자 수**: 해당 연도에 **육아휴직을 시작한 사람**(임신 중이거나 만 8세 이하·초등 2학년 이하 자녀 대상). 고용보험·건강보험 등 행정자료 11종을 연계하며 공무원·교원 등 공공부문도 포함하는 것으로 파악(A1보다 큼. 대상 범위는 통계설명자료에서 재확인 권장). ② **출생아 부모 육아휴직 사용률**: 당해 출생아의 부모 중 같은 해에 육아휴직을 시작한 사람의 비율(%). ③ **출생아 100명당 육아휴직 부모 수**(2019~2022 공표본에서 사용, 이후 ②로 바뀜). ④ **출생 후 12개월 이내 사용률**(출생연도 코호트). ⑤ 출생코호트 누적(만 0~8세) 사용 | **2010~2024**(2025.12 공표본 기준), 연간 | 부·모, 기업규모, 산업, 연령, 시도, 휴직기간, 부모 동시 사용 등 | KOSIS 국내통계 > 고용·노동·임금 > 육아휴직통계 · [통계설명](https://mods.go.kr/statDesc.es?act=view&mid=a10501010000&sttr_cd=S002007) · [보도자료 목록](https://kostat.go.kr/board.es?bid=11814&mid=a10301030600) · [2024년 결과(잠정)](https://kostat.go.kr/board.es?act=view&bid=11814&list_no=442470&mid=a10301030600) | 연도별 주요 지표 재구성 → `data/kostat_parental_leave_statistics_headline.csv` |
| A3 | **국가지표체계 H0022** (index.go.kr) | 국가지표로 올라간 육아휴직 지표(A2 기반) | A2와 같음 | 부·모 | [지표상세](https://www.index.go.kr/unity/potal/indicator/IndexInfo.do?cdNo=260&clasCd=12&idxCd=H0022&upCd=9) | 접속 차단(A2 값으로 대체) |
| A4 | **인사혁신처 「행정부 국가공무원 인사통계」** | 해당 연도에 육아휴직을 쓴(발령된) 행정부 국가공무원 수 | 연간(인사통계연보). 확인한 값: 2016·2018·2020·2022·2025 | 성별, 부처별 | 인사혁신처 인사통계 | 일부 연도 → `data/public_sector_parental_leave.csv` |
| A5 | **행정안전부 「지방자치단체 공무원 인사통계」** / 내고장알리미 | 1.1~12.31에 **육아휴직 발령을 받은 지방공무원 수** | 연간(매년 3월 공개) | 자치단체별, 성별 | [내고장알리미 육아휴직 현황](https://laiis.go.kr/lips/nya/psnoper/personnelOperationDetail.do?type=4011700) | 접속 차단 |
| A6 | **기획재정부 ALIO 공공기관 경영정보공개** | 기관별 육아휴직자 수(성별). 일·가정 양립 지원제도 운영 현황 공시 | 최근 5년치 공시(연간). 2017~ | 공공기관별, 성별 | [ALIO 일·가정양립 통계](https://www.alio.go.kr/statistics/workhomeSupport.do) | 2017·2021 요약값만 |
| A7 | 기관 단위 공공데이터 (예: [한국장학재단 육아휴직 현황 15080684](https://www.data.go.kr/data/15080684/fileData.do)), [서울시 인사지표 육아휴직 현황](https://news.seoul.go.kr/gov/archives/536747) | 해당 기관·지자체 소속 직원의 육아휴직자 수 | 기관마다 다름 | 성별 | 공공데이터포털 / 서울시 | 접속 차단 |

### B. 2차 가공·국제비교 (다른 기관이 A1·A2를 다시 정리한 자료)

| # | 출처 | 지표 정의 | 기간 | 접근 경로 |
|---|---|---|---|---|
| B1 | 통계청 **「일·가정 양립 지표」** (2014.10 서비스 시작, 연간 보도자료) | 5개 분야 19개 지표 가운데 육아휴직자 수(A1 기반) 포함 | 2014~2019년경 공표 | 통계청 보도자료(예: [2019 보도 기사](https://www.seoul.co.kr/news/society/2019/12/19/20191219010018)) |
| B2 | 한국여성정책연구원 **「한국의 성인지 통계」** / GSIS | 성별 육아휴직자 수·비율(A1·A2 기반) | 연간 | [2022 한국의 성인지 통계(PDF)](https://gsis.kwdi.re.kr/gsis/upload/file/202309244_12695100000.pdf) |
| B3 | **OECD Family Database PF2.2** "Parents' use of childbirth-related leave" | 출생아 100명당 모성·부성·부모휴가 급여 수급자 수, 부모휴가 사용자 중 남성 비율(한국은 A1 기반) | 2000년대~최근(국가별 갱신) | [PF2.2 PDF](https://webfs.oecd.org/els-com/Family_Database/PF2-2-Use-childbirth-leave.pdf) · [PF2.1 아태판(OECD 한국정책센터)](https://oecdkorea.org/resource/download/2023/PF_2_1_Parental_leave_systems_2023.pdf) |
| B4 | **International Network on Leave Policies & Research** 한국 국가보고서 | 제도 요약과 사용 통계(아빠 육아휴직 보너스 사용자 등) | 매년 갱신 | [2021 Korea note](https://www.leavenetwork.org/fileadmin/user_upload/k_leavenetwork/country_notes/2021/Korea.final_edited_pm.21july2021.pdf) · [2020](https://www.leavenetwork.org/fileadmin/user_upload/k_leavenetwork/country_notes/2020/PMedited.Korea.no_supplement.31aug2020.pdf) |
| B5 | 국회도서관 「데이터로 보는 근로자 육아휴직」 | A1·A2 종합 인포그래픽 | 2023~2024 | [국가전략정보포털](https://nsp.nanet.go.kr/plan/subject/detail.do?nationalPlanControlNo=PLAN0000046750) |

### C. 조사통계 (표본조사, 보고서 안에 수치가 있음)

| # | 출처 | 지표 정의 | 조사 연도 | 원자료·보고서 |
|---|---|---|---|---|
| C1 | **고용노동부 「일·가정 양립 실태조사」** (남녀고용평등법 제6조의3) | 5인 이상 사업체 약 5,000곳의 인사담당자 대상. 육아휴직 제도 **인지율·도입률·사용 경험 사업체 비율**, 사용자 수 | 과거 3년 주기 → 최근 매년(2021·2022·2023 기준 등) | [2023 기준 보고서](https://www.moel.go.kr/info/publicdata/majorpublish/majorPublishView.do?bbs_seq=20241202134) · [보고서 15032836](https://www.data.go.kr/data/15032836/fileData.do) · [원자료 15100310](https://www.data.go.kr/data/15100310/fileData.do) |
| C2 | **여성가족부 「경력단절여성 등의 경제활동 실태조사」** | 25~54세 여성 약 8,500명 대상. 출산·육아기 육아휴직 사용 경험 비율 | 2013, 2016, 2019, 2022 (3년 주기) | [2022 결과보고서](https://www.mogef.go.kr/mp/pcd/mp_pcd_s001d.do?mid=plc517&bbtSn=704955) · [보고서 15054892](https://www.data.go.kr/data/15054892/fileData.do) |
| C3 | **한국보건사회연구원 「전국 출산력 및 가족보건·복지 실태조사」 → 「가족과 출산 조사」(2021~)** | 출산 전 취업 여성의 출산 전후 육아휴직 이용률 | 3년 주기(~2018), 2021~ | [2021년도 가족과 출산조사 보고서(2021-50)](https://repository.kihasa.re.kr/bitstream/201002/40281/7/%EC%97%B0%EA%B5%AC%EB%B3%B4%EA%B3%A0%EC%84%9C%202021-50.pdf) |
| C4 | **한국여성정책연구원 「여성가족패널(KLoWF)」** | 직장의 육아휴직 제도 유무, 본인의 사용 경험(패널) | 2007~, 격년 | KWDI 패널 홈페이지 |
| C5 | **한국노동연구원 「한국노동패널(KLIPS)」·「사업체패널조사(WPS)」** | 개인의 육아휴직 사용 여부 / 사업체 단위 육아휴직 사용자 수 | KLIPS 1998~ 매년, WPS 2005~ 격년 | KLI 패널 홈페이지 |

---

## 2. 이번에 확인한 핵심 수치

### 2-1. 고용노동부 육아휴직급여 초회 수급자 (A1)

| 연도 | 전체 | 남성 | 남성비중 | 연도 | 전체 | 남성 | 남성비중 |
|---|---:|---:|---:|---|---:|---:|---:|
| 2002 | 3,763* | 78* | 2.1% | 2014 | 76,833* | 3,421 | 4.5% |
| 2003 | 6,816 | 104* | 1.5% | 2015 | 87,339 | 4,872 | 5.6% |
| 2004 | 9,304 | 181* | 1.9% | 2016 | 89,795* | 7,616* | 8.5% |
| 2005 | 10,700 | 208* | 1.9% | 2017 | 90,123 | 12,043 | 13.4% |
| 2006 | 13,670 | 230* | 1.7% | 2018 | 99,199* | 17,665 | 17.8% |
| 2007 | 21,185 | 310* | 1.5% | 2019 | 105,165 | 22,297 | 21.2% |
| 2008 | 29,145 | 355 | 1.2% | 2020 | 112,040 | 27,423 | 24.5% |
| 2009 | 35,400 | 502 | 1.4% | 2021 | 110,555 | 29,041 | 26.3% |
| 2010 | 41,733 | 819 | 2.0% | 2022 | 131,084 | 37,884* | 28.9% |
| 2011 | 58,137* | 1,402 | 2.4% | 2023 | 126,008 | 35,336 | 28.0% |
| 2012 | 64,069* | 1,790 | 2.8% | 2024 | 132,535 | 41,829 | 31.6% |
| 2013 | 69,616* | 2,293 | 3.3% | 2025 | 184,329 | 67,200 | 36.5% |
| | | | | 2026 상반기 | 103,983 | 40,320 | 38.8% |

\* 공식 자료와 직접 대조하지 못한 값입니다. 원자료로 꼭 확인하세요. 나머지는 고용노동부 보도자료나 언론 인용으로 확인했습니다.

### 2-2. 국가데이터처 육아휴직통계 (A2)

| 기준연도 | 육아휴직자(시작자) | 부 | 출생아 부모 사용률 (전체/부/모) | 출생아 100명당 |
|---|---:|---:|---|---|
| 2010 | 72,769 | 1,967 | – | 2010년 출생 코호트 만 0~8세 누적 19.6명 (부 1.8, 모 17.8) |
| 2017 | 140,531 | | | |
| 2018 | 152,241 | | | |
| 2019 | 159,153 | | | 22.8 (부 1.3, 모 21.4) |
| 2020 | 169,345 | 38,511 | | 26.8 (부 2.5, 모 24.3) |
| 2021 | 173,631 | 41,910 | 25.9 / 4.1 / 65.4 (역산) | 29.8 (역산) |
| 2022 | 199,976 | | 30.2 / 6.8 / 70.0 (잠정) → 31.3 / 7.1 / 71.2 (역산 확정) | 35.0 |
| 2023 | 195,986 | (25.7%) | 32.9 / 7.4 / 73.2 (잠정) → 33.0 / 7.5 / 73.2 (역산 확정) | |
| 2024 | 206,226 | 60,117 | **34.7 / 10.2 / 72.2** (잠정) | |

- 부의 당해 사용률: 2015년 0.6%에서 2024년 10.2%로 늘었습니다.
- 출생 후 12개월 이내 사용률(코호트): 2015년 출생아는 부 1.1%·모 68.5%, 2021년 출생아는 부 10.2%·모 80.9%입니다(언론 인용, 분모 정의는 원문 확인 필요).
- 모든 값은 **각 연도 잠정 공표본 기준**이고, 이듬해 확정치로 수정됩니다. 최신 공표본의 시계열 표(KOSIS)로 한꺼번에 바꾸는 것을 권장합니다.

### 2-3. A1과 A2의 차이 (분석할 때 주의)

| | A1 고용노동부 | A2 국가데이터처 |
|---|---|---|
| 집계 단위 | 육아휴직**급여** 초회 수급자 | 육아휴직 **시작자** |
| 공공부문 | 제외 (고용보험 미적용) | 포함 |
| 2024년 값 | 132,535명 | 206,226명 |
| 사용률 | 없음 (분모 없음) | 출생아 부모 대비 사용률 제공 |

---

## 3. 보고서·논문 정리 (수치나 분석이 보고서·논문 안에 있는 자료)

### 국내 보고서

| 저자·기관 (연도) | 제목 | 자료 | 주요 내용 |
|---|---|---|---|
| 한국노동연구원 『노동리뷰』 (2018.11) | 통계프리즘: 한국 남성 육아휴직 현황 | 고용보험 DB | 2008~2017 육아휴직자·남성 추이(29,145명 → 90,123명, 남성 355명 → 12,043명) [PDF](https://repository.kli.re.kr/bitstream/2021.oak/6529/2/%EB%85%B8%EB%8F%99%EB%A6%AC%EB%B7%B0_no.164_2018.11_8.pdf) |
| 국회예산정책처 | 육아휴직 사용자의 성별 특성에 관한 연구 | 고용보험 DB | 2017.9 첫 3개월 소득대체율 인상(40%→80%) 전후의 휴직기간·고용유지율을 성별로 비교 [PDF](https://www.nabo.go.kr/board/file/down.do?fid=33315808) |
| 한국노동연구원 (기본연구) | 소득대체율 증가가 남성의 육아휴직 사용에 미친 영향 분석 | 고용보험 DB | 급여 인상이 남성 사용에 준 효과 [링크](https://kli.re.kr/board.es?act=view&bid=0007&list_no=143956&mid=a10505020000&nPage=1) |
| 한국노동연구원 | 육아휴직 사용에 관한 연구 | – | [PDF](https://www.kli.re.kr/kliFileDownload?fileName=FF19D359FA7258FD49258AC5000C667A_4.pdf&fileNameOrg=%EC%9C%A1%EC%95%84%ED%9C%B4%EC%A7%81+%EC%82%AC%EC%9A%A9%EC%97%90+%EA%B4%80%ED%95%9C+%EC%97%B0%EA%B5%AC_web.pdf&filePath1=jsphome%2FDATA%2FpblctList%2Fissue%2FFF19D359FA7258FD49258AC5000C667A) |
| 이규용 / 한국노동연구원 (2004) | 육아휴직 활용실태와 정책과제 | 고용보험·설문 | 제도 초기의 활용 실태 [ScienceON](https://scienceon.kisti.re.kr/srch/selectPORSrchReport.do?cn=TRKO201800034947) |
| 한국고용정보원 『고용동향브리프』 | 성별 육아휴직제도 활용 현황 분석 | 고용보험 DB | 성별 활용 현황 [링크](https://www.keis.or.kr/keis/ko/proj/118/pblc/rpt/detail.do?categoryIdx=126&reportIdx=5702) |
| 한국보건사회연구원 (2022) | 출산전후휴가 및 육아휴직제도 개편방안 연구 (연구보고서 2022-44) | 행정·조사자료 | 제도 개편 방향 [PDF](https://repository.kihasa.re.kr/bitstream/201002/42264/1/%EC%97%B0%EA%B5%AC%EB%B3%B4%EA%B3%A0%EC%84%9C%202022-44.pdf) |
| 한국보건사회연구원 (2021) | 2021년도 가족과 출산조사 (연구보고서 2021-50) | C3 | 제8장 일·생활 균형: 육아휴직 이용률 [PDF](https://repository.kihasa.re.kr/bitstream/201002/40281/7/%EC%97%B0%EA%B5%AC%EB%B3%B4%EA%B3%A0%EC%84%9C%202021-50.pdf) |
| 김지현 / 경기도여성가족재단 (2024) | 남성의 육아휴직제도 이용 요인 분석과 활성화 방안 모색 | 패널·행정자료 | 남성 이용 요인 [PDF](https://www.gwff.kr/storage/board/privacy/2024/05/13/PRIVACY_ATTACH_1715580711909.pdf) |
| 행정안전부 | 지방자치단체 지방직공무원 육아휴직 활용실태 및 개선방안 | 지방공무원 인사자료 | [ScienceON](https://scienceon.kisti.re.kr/srch/selectPORSrchReport.do?cn=TRKO201600001068) |
| 민주노동연구원 | 남성 노동자의 육아휴직 사용 격차와 차별(워킹페이퍼) / 공무원 육아휴직 실태 분석 Ⅲ(9급 코호트) | 고용보험·인사자료 | [보도자료](https://nodong.org/statement/7849640) · [이슈페이퍼](https://nodong.org/statement/7933652) |
| 발간기관 미확인 (2024.2) | 출산휴가 및 육아휴직 제도 국제비교와 시사점 | 국제비교 | [PDF](http://hwlabor.co.kr/data/file/data/1794735835_BLZH8M0o_dd43424f02f9bd6c9f4fa49c6e8ed6496c205b39.pdf) |

### 국내 학술논문 (KCI 등)

| 저자 (연도) | 제목 | 게재지 | 자료 |
|---|---|---|---|
| 김정호 (2012) | 육아휴직 지원과 여성의 노동공급 | KDI Journal of Economic Policy 34(1): 169–197 [링크](https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART001650984) | 고용보험 DB. 급여 인상이 여성의 이용률과 근로 연속성을 높임 |
| 이수영·이근주 (2011) | 한국 민간기업 근로여성의 육아휴직 활용 패턴 영향요인 연구: 고용보험 DB 분석을 중심으로 | KCI [ART001567103](https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART001567103) | 고용보험 DB |
| (2017년경) | 성평등 인센티브의 남성 육아휴직 사용 확대효과: 민간부문을 중심으로 | KCI [ART002267012](https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002267012) | 고용보험 DB. 아빠 육아휴직 보너스 효과 |
| 배호중·천재영 (2018) | 출산전후 휴가 및 육아휴직 활용가능성이 출산에 미치는 영향: 신혼여성을 중심으로 | 여성연구 96(1) [링크](https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART002330229) | 여성가족패널 |
| 이지혜·진미정 (2024) | 육아휴직제도 변화와 여성 임금근로자의 취업 상태 | 보건사회연구 44(1): 398–425 [PDF](https://www.kihasa.re.kr/hswr/assets/pdf/1462/journal-44-1-398.pdf) | 패널자료 |
| 윤명수·부가청 (2016) | (제목 미확인) 사업체패널로 본 육아휴직 활용 현황과 결정요인 | 국회예산정책처 보고서의 선행연구 인용 | 사업체패널 |
| – | 육아휴직 이후 무슨 일이 있었을까?: 젠더효과와 고용유지를 중심으로 본 심층면접 분석 | KCI [ART002730313](https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002730313) | 질적 연구 |
| – | 기업특성과 가족친화제도 활용 용이성: 여성관리자의 육아휴직 및 본인병가제도 활용을 중심으로 | KCI [ART001485591](https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART001485591) | 여성관리자패널 |
| – | 미취학자녀를 둔 맞벌이 여성의 육아휴직제도 이용의사에 관한 연구 | KCI [ART001890966](https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART001890966) | 설문 |

### 해외 학술논문·국제기구 자료

| 저자·기관 (연도) | 제목 | 게재지 |
|---|---|---|
| (2023) | Parental Leave Reforms in South Korea, 1995–2021: Policy Translation and Institutional Legacies | *Social Politics* 30(4): 1113– [링크](https://academic.oup.com/sp/article/30/4/1113/7136011) |
| – | Pushes and pulls of father leave policy reform: Czech Republic and South Korea | *Journal of International and Comparative Social Policy* [링크](https://www.cambridge.org/core/journals/journal-of-international-and-comparative-social-policy/article/pushes-and-pulls-of-father-leave-policy-reform-unpacking-divergent-father-leave-reforms-in-the-czech-republic-and-south-korea/036130CC234B60875D151D90DA3074A0) |
| (2023) | 'Undoing gender' or selection effects?: fathers' uptake of leave and involvement in housework and childcare in South Korea | *Journal of Family Studies* [링크](https://www.tandfonline.com/doi/full/10.1080/13229400.2023.2200747) |
| (2022) | Norms about childcare, working hours, and fathers' uptake of parental leave in South Korea | *Community, Work & Family* [링크](https://www.tandfonline.com/doi/full/10.1080/13668803.2022.2031889) |
| (2022) | Is Leave for Fathers Pronatalist? A Mixed-Methods Study of the Impact of Fathers' Uptake of Parental Leave on Couples' Childbearing Intentions in South Korea | *Population Research and Policy Review* [링크](https://link.springer.com/article/10.1007/s11113-022-09697-4) |
| (2024) | Impact of parental leave system on the childbirth plan among working married women: a three-year follow-up study of KLoWF | [PMC10832238](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10832238/) |
| OECD (2019) | Korea's Unborn Future: Understanding Low-Fertility Trends, ch. "Family policies are a piece of the puzzle, not a cure-all" | [링크](https://www.oecd.org/en/publications/korea-s-unborn-future_005ce8f7-en/full-report/family-policies-are-a-piece-of-the-puzzle-not-a-cure-all_2c6d8268.html) |
| Kim, H. & Shin, E. (2021); Kim, H. (2020) | Korea country note, *International Review of Leave Policies and Research* | [2021](https://www.leavenetwork.org/fileadmin/user_upload/k_leavenetwork/country_notes/2021/Korea.final_edited_pm.21july2021.pdf) · [2020](https://www.leavenetwork.org/fileadmin/user_upload/k_leavenetwork/country_notes/2020/PMedited.Korea.no_supplement.31aug2020.pdf) |

(저자를 '–'로 표시한 논문은 검색 결과에서 저자를 확인하지 못한 것입니다.)

---

## 4. 파일 구성

```
parental_leave_korea/
├── README.md                                            # 이 문서
├── data/
│   ├── moel_parental_leave_benefit_recipients_annual.csv  # A1: 2002~2025 + 2026H1
│   ├── kostat_parental_leave_statistics_headline.csv      # A2: 지표별·연도별 주요값
│   └── public_sector_parental_leave.csv                   # A4 국가공무원, A6 공공기관
└── scripts/
    └── download_parental_leave_data.py                    # KOSIS API·공공데이터포털 일괄 다운로드(로컬 실행)
```

CSV는 엑셀에서 한글이 깨지지 않도록 UTF-8(BOM)으로 저장했습니다.

## 5. 원자료로 대체하는 순서 (권장)

1. KOSIS에서 **「육아휴직통계」 최신 공표본(2025.12)** 시계열 표를 받아 `kostat_*.csv`를 대체합니다. 잠정·확정 차이가 이것으로 해결됩니다.
2. 고용행정통계 **모성보호지급자현황(월)**이나 공공데이터포털 15100479에서 월별 원자료를 받아 `moel_*.csv`의 `*` 값을 검증합니다.
3. 공공부문을 따로 보려면 인사혁신처 인사통계연보(국가직), 내고장알리미(지방직), ALIO(공공기관)를 합칩니다.

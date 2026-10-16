# MOM_presentation: 고용주 결과를 appended 표본(n = 397)으로 바꾼 작업본

교수님 폴더(`ResWork_SY/SNEF_survey/final/deck_support`, `final/overleaf`)는 수정하지 않았습니다.
그 폴더의 코드는 읽기만 하고, 바뀐 결과물은 모두 이 폴더에만 둡니다.

## 2026-10-16 업데이트 (WTP 기준)
- 본문·부록 모두 전체 응답자 사용, Lucid 제외 값과 †범위 삭제, 같은 임금에서 선택 확률(equal-pay share) 삭제 → 전부 WTP.
- 부호: **양수 = 포기하는 임금**. PME = 포기할 임금, 고용주 = 요구하는 임금 삭감(= 모형 WTP의 부호 반전). 격차 = 고용주 요구 − PME 포기(양수 = 마찰).
- 새 파일: `scripts/build_wtp_data.py`(→ `data/wtp_deck.csv`), `scripts/fig_wtp.py`, `scripts/fig_backup_wtp.py`, `scripts/make_tables_wtp.py`, `latex/CHANGES_wtp_update.md`.
- 올릴 파일은 `overleaf_upload/` 또는 `MOM_overleaf_upload.zip`. 아래 옛 설명(동일임금 확률 기준)은 참고용입니다.

## 폴더 구성
| 경로 | 내용 |
|---|---|
| `latex/main-2.tex` | 발표자료. 고용주 값은 appended 결과로 교체. 아직 appended 결과가 없는 값은 이전(303개사) 값을 빨간색 `\Pend{}`로 표시 |
| `latex/tables/` | 고용주 값이 들어간 표 6개(T_eqpay, T_org_pct, T_yardstick, T_gap, T_flexiload, T_concerns). Overleaf의 `tables/`에서 같은 이름의 파일만 교체 |
| `scripts/make_figs_appended.py` | 고용주 그림 3개(F_org_eqpay, F_where_r5, F_meet_r5)를 다시 그리는 실행 파일. 교수님 `deck_support/scripts`의 figstyle/fig_main/fig_v2를 읽기 전용으로 사용 |
| `latex/parts/` | Dropbox 업로드 한도 때문에 `main-2.tex`를 프레임 경계에서 4개로 나눈 파일. Dropbox의 `latex/main-2.tex`는 이 4개를 `\input`하는 래퍼이고, 합치면 GitHub의 단일 파일 `main-2.tex`와 바이트 단위로 같음 |
| `scripts/fig_r5_appended.py` | 교수님 `fig_r5.py`를 읽어서 메모리에서만 고용주 기대값을 appended 값으로 바꿔 실행(원본 파일은 수정하지 않음) |
| `data/dce_eqpay.csv` | 그림용 동일임금 선택확률(PME 행은 원본 그대로, 고용주 행은 appended_clogit.xlsx main) |
| `data/employer_channels_appended.csv` | F_where_r5용 집단별 값(appended_clogit.xlsx physical_1/2, creative_concern_1/0) |
| `figures/` | 위 스크립트의 결과물. 처음에는 비어 있으니 아래 명령으로 생성 |

## 그림 다시 그리기
```
python3 ~/Dropbox/MOM_presentation/scripts/make_figs_appended.py
```
결과는 `MOM_presentation/figures/`에 PDF와 PNG로 저장됩니다. Overleaf의 `figures/`에서 같은 이름의 PDF만 교체하면 됩니다.
필요한 패키지: matplotlib, openpyxl (선택: pymupdf, 크기 점검용).

## 계산 방법
- 동일임금 선택확률 = invlogit(b), 95% CI는 delta method(교수님 `deck_eqpay.do`와 같은 식). 이전 계수로 계산하면 기존 슬라이드 값이 그대로 재현됩니다.
- 고용주 할인율은 `appended_wtp.xlsx`의 값입니다.
- 격차(T_gap)는 appended_wtp.xlsx에 gap 시트가 없어 반올림된 값으로 계산한 근삿값입니다.

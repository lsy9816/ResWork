"""육아휴직 관련 원자료 일괄 다운로드 스크립트 (로컬 PC에서 실행용)

이 스크립트를 작성한 클라우드 환경에서는 kosis.kr·data.go.kr 접속이 막혀 있어
실행해 보지 못했습니다. 한국 사이트에 접속되는 PC에서 실행하세요.

사용법
------
1) KOSIS 공유서비스(https://kosis.kr/openapi/)에서 회원가입 후 API 키 발급
2) pip install requests pandas openpyxl
3) KOSIS_API_KEY=발급키 python scripts/download_parental_leave_data.py

동작
----
- KOSIS 통합검색 API로 '육아휴직' 키워드 통계표 목록을 받아 raw/kosis_table_list.csv로 저장
- 목록의 각 통계표를 메타데이터(분류 수) 조회 후 전체 항목·전체 분류로 내려받아
  raw/kosis/<orgId>_<tblId>.csv 로 저장 (연간 → 월간 → 분기 순으로 시도)
- 공공데이터포털 파일데이터 페이지에서 첨부파일 링크를 찾아 raw/datagokr/ 에 저장 (best-effort)
"""

import os
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

API_KEY = os.environ.get("KOSIS_API_KEY", "")
OUT = Path(__file__).resolve().parent.parent / "raw"
KOSIS = "https://kosis.kr/openapi"

SEARCH_KEYWORDS = ["육아휴직", "육아휴직급여", "출산전후휴가"]

# 공공데이터포털 파일데이터 (페이지 ID)
DATAGOKR_PAGES = {
    "15100479": "고용노동부_성별 지역별 육아휴직급여 수급자수",
    "15032836": "고용노동부_일가정양립실태조사 보고서",
    "15100310": "고용노동부_일가정양립실태조사 데이터",
    "15054892": "여성가족부_경력단절여성 등의 경제활동실태조사 보고서",
    "15080684": "한국장학재단_육아휴직 현황",
}


def kosis_get(path, **params):
    params.update(apiKey=API_KEY, format="json", jsonVD="Y")
    r = requests.get(f"{KOSIS}/{path}", params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and data.get("err"):
        raise RuntimeError(f"KOSIS err {data.get('err')}: {data.get('errMsg')}")
    return data


def search_tables():
    frames = []
    for kw in SEARCH_KEYWORDS:
        data = kosis_get("statisticsSearch.do", method="getList", searchNm=kw,
                         startCount=1, resultCount=200, sort="RANK")
        df = pd.DataFrame(data)
        df["검색어"] = kw
        frames.append(df)
        time.sleep(0.5)
    tables = pd.concat(frames, ignore_index=True).drop_duplicates(["ORG_ID", "TBL_ID"])
    tables.to_csv(OUT / "kosis_table_list.csv", index=False, encoding="utf-8-sig")
    return tables


def n_classification_levels(org_id, tbl_id):
    """통계표의 분류(objL) 단계 수. 조회 실패 시 1 반환."""
    try:
        meta = kosis_get("statisticsData.do", method="getMeta", type="ITM",
                         orgId=org_id, tblId=tbl_id)
        obj_ids = {m.get("OBJ_ID") for m in meta if m.get("OBJ_ID") != "ITEM"}
        return max(1, len(obj_ids))
    except Exception:
        return 1


def download_table(org_id, tbl_id):
    levels = n_classification_levels(org_id, tbl_id)
    base = dict(method="getList", orgId=org_id, tblId=tbl_id, itmId="ALL")
    for i in range(1, levels + 1):
        base[f"objL{i}"] = "ALL"
    last_err = "데이터 없음"
    for prd_se, start, end in (("Y", "1990", "2030"), ("M", "200101", "203012"),
                               ("Q", "20011", "20304"), ("H", "20011", "20302")):
        try:
            data = kosis_get("Param/statisticsParameterData.do", prdSe=prd_se,
                             startPrdDe=start, endPrdDe=end, **base)
        except Exception as e:  # 해당 주기 없음, 셀 수 초과(4만 셀) 등
            last_err = e
            continue
        if data:
            pd.DataFrame(data).to_csv(OUT / "kosis" / f"{org_id}_{tbl_id}_{prd_se}.csv",
                                      index=False, encoding="utf-8-sig")
            return prd_se
    raise RuntimeError(last_err)


def download_datagokr():
    (OUT / "datagokr").mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0"
    for pid, name in DATAGOKR_PAGES.items():
        page = s.get(f"https://www.data.go.kr/data/{pid}/fileData.do", timeout=60).text
        m_atch = re.search(r"atchFileId['\"]?\s*[:=]\s*['\"]([A-Z0-9_]+)", page)
        m_sn = re.search(r"fileDetailSn['\"]?\s*[:=]\s*['\"]?(\d+)", page)
        if not m_atch:
            print(f"  [수동 다운로드 필요] {name}: https://www.data.go.kr/data/{pid}/fileData.do")
            continue
        url = ("https://www.data.go.kr/cmm/cmm/fileDownload.do"
               f"?atchFileId={m_atch.group(1)}&fileDetailSn={m_sn.group(1) if m_sn else 1}")
        r = s.get(url, timeout=120)
        cd = r.headers.get("Content-Disposition", "")
        ext = re.search(r"\.(\w+)\"?$", cd)
        fn = OUT / "datagokr" / f"{pid}_{name}.{ext.group(1) if ext else 'bin'}"
        fn.write_bytes(r.content)
        print(f"  saved {fn.name} ({len(r.content):,} bytes)")


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "kosis").mkdir(exist_ok=True)
    if not API_KEY:
        sys.exit("KOSIS_API_KEY 환경변수를 설정하세요 (https://kosis.kr/openapi/ 에서 발급).")

    tables = search_tables()
    print(f"KOSIS 통계표 {len(tables)}개 발견 → raw/kosis_table_list.csv")
    for _, t in tables.iterrows():
        try:
            prd = download_table(t["ORG_ID"], t["TBL_ID"])
            print(f"  OK  [{prd}] {t['ORG_ID']}_{t['TBL_ID']} {t.get('TBL_NM', '')}")
        except Exception as e:
            print(f"  FAIL {t['ORG_ID']}_{t['TBL_ID']} {t.get('TBL_NM', '')}: {e}")
        time.sleep(0.5)

    print("공공데이터포털 파일데이터 다운로드")
    download_datagokr()


if __name__ == "__main__":
    main()

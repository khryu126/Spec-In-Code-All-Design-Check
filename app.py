import streamlit as st
import pandas as pd
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="유대리 스펙체크", layout="wide")

# 2. 데이터 불러오기 함수 (전체 데이터 유지 및 안전한 병합)
@st.cache_data
def load_data():
    spec_file = '스펙인코드.csv' if os.path.exists('스펙인코드.csv') else '스펙인코드.CSV'
    img_file = '이미지경로.csv' if os.path.exists('이미지경로.csv') else '이미지경로.CSV'
    
    encodings = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']
    spec_df = None
    img_df = None

    # 파일 로드 시도
    for enc in encodings:
        try:
            spec_df = pd.read_csv(spec_file, encoding=enc)
            spec_df.columns = spec_df.columns.str.strip()
            break
        except: continue

    for enc in encodings:
        try:
            img_df = pd.read_csv(img_file, encoding=enc)
            img_df.columns = img_df.columns.str.strip()
            break
        except: continue

    if spec_df is not None and img_df is not None:
        # 컬럼 자동 식별
        s_col = next((c for c in spec_df.columns if '품번' in c), spec_df.columns[0])
        i_col = next((c for c in img_df.columns if '품번' in c), img_df.columns[0])
        url_col = next((c for c in img_df.columns if 'URL' in c or '이미지' in c or '경로' in c), img_df.columns[-1])

        # 데이터 타입 통일 및 공백 제거
        spec_df[s_col] = spec_df[s_col].astype(str).str.strip()
        img_df[i_col] = img_df[i_col].astype(str).str.strip()

        # 전체 병합 (중복 유지, 누락 방지)
        merged = pd.merge(spec_df, img_df, left_on=s_col, right_on=i_col, how='left')
        
        return merged, url_col
    return None, None

df, url_key = load_data()

# 3. 메인 화면 구성
st.title("🏗️ 자재 스펙 & 이미지 통합 조회")

# 검색창 및 버튼
col_search, col_btn = st.columns([4, 1])
with col_search:
    query = st.text_input("🔍 검색어 입력", placeholder="검색어를 입력하세요 (예: 35-328)").strip()
with col_btn:
    search_clicked = st.button("검색", use_container_width=True)

# 4. 결과 표시 로직
if query or search_clicked:
    if df is not None:
        # 전체 텍스트 검색
        mask = df.astype(str).apply(lambda row: row.str.contains(query, case=False, na=False).any(), axis=1)
        results = df[mask]
        
        if not results.empty:
            st.success(f"✅ 총 {len(results)}건의 결과가 발견되었습니다.")
            for _, row in results.iterrows():
                st.markdown("---")
                c1, c2 = st.columns([1, 1.2

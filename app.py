import streamlit as st
import pandas as pd
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="유대리 스펙체크", layout="wide")

# 2. 데이터 불러오기 함수
@st.cache_data
def load_data():
    spec_file = '스펙인코드.csv' if os.path.exists('스펙인코드.csv') else '스펙인코드.CSV'
    img_file = '이미지경로.csv' if os.path.exists('이미지경로.csv') else '이미지경로.CSV'
    
    encodings = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']
    spec_df = None
    img_df = None

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
        s_col = next((c for c in spec_df.columns if '품번' in c), spec_df.columns[0])
        i_col = next((c for c in img_df.columns if '품번' in c), img_df.columns[0])
        url_col = next((c for c in img_df.columns if 'URL' in c or '이미지' in c or '경로' in c), img_df.columns[-1])

        spec_df[s_col] = spec_df[s_col].astype(str).str.strip()
        img_df[i_col] = img_df[i_col].astype(str).str.strip()

        # 중복을 허용하는 조인 (이미지 파일 기준으로 누락 방지)
        merged = pd.merge(spec_df, img_df, left_on=s_col, right_on=i_col, how='left')
        
        return merged, url_col
    return None, None

df, url_key = load_data()

# 3. 메인 화면 구성
st.title("🏗️ 자재 스펙 & 이미지 통합 조회")

col_search, col_btn = st.columns([4, 1])
with col_search:
    query = st.text_input("🔍 검색어 입력", placeholder="35-328 등 아무거나 입력하세요", label_visibility="collapsed").strip()
with col_btn:
    search_clicked = st.button("검색", use_container_width=True)

# 4. 결과 표시 로직
if query or search_clicked:
    if df is not None:
        mask = df.astype(str).apply(lambda row: row.str.contains(query, case=False, na=False).any(), axis=1)
        results = df[mask]
        
        if not results.empty:
            st.success(f"✅ 총 {len(results)}건의 결과가 발견되었습니다.")
            for _, row in results.iterrows():
                st.markdown("---")
                # 이 부분이 에러가 났던 72번 줄입니다. 괄호와 대괄호를 확실히 닫았습니다.
                c1, c2 = st.columns([1, 1.2]) 
                
                with c1:
                    st.subheader("📋 자재 정보")
                    for col in df.columns:
                        if "_y" not in col and col != url_key:
                            val = row[col] if pd.notna(row[col]) else "-"
                            st.write(f"**{col}:** {val}")
                
                with c2:
                    st.subheader("🖼️ 이미지 확인")
                    url = row.get(url_key)
                    if pd.isna(url) or not str(url).startswith('http'):
                        for col in df.columns:
                            if str(row[col]).startswith('http'):
                                url = row[col]
                                break
                    
                    if pd.notna(url) and str(url).startswith('http'):
                        # 액박 방지용 HTML 코드
                        html_code = f"""
                            <img src="{url}" 
                                 style="width: 100%; border-radius: 5px; object-fit: contain;" 
                                 onerror="this.style.display='none';">
                            <br>
                            <a href="{url}" target="_blank" style="font-size: 0.8em; color: gray; text-decoration: none;">
                                🔗 [원본 링크 열기] (이미지가 안 보이면 클릭)
                            </a>
                        """
                        st.markdown(html_code, unsafe_allow_html=True)
                    else:
                        st.write("이미지 준비 중입니다.")
        else:
            st.warning(f"📍 '{query}'에 대한 검색 결과가 없습니다.")
    else:
        st.error("데이터 파일을 불러오지 못했습니다.")

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="자재 정보 통합 조회", layout="wide")

@st.cache_data
def load_data():
    # 파일명이 대문자인지 소문자인지 확인해서 있는 것을 가져옵니다.
    spec_file = '스펙인코드.csv' if os.path.exists('스펙인코드.csv') else '스펙인코드.CSV'
    img_file = '이미지경로.csv' if os.path.exists('이미지경로.csv') else '이미지경로.CSV'
    
    try:
        # 인코딩도 한국어 엑셀에서 가장 흔한 두 가지를 다 시도합니다.
        try:
            spec = pd.read_csv(spec_file, encoding='utf-8-sig')
            img = pd.read_csv(img_file, encoding='utf-8-sig')
        except:
            spec = pd.read_csv(spec_file, encoding='cp949')
            img = pd.read_csv(img_file, encoding='cp949')
            
        merged = pd.merge(spec, img[['추출된_품번', '카카오톡_전송용_URL']], 
                          left_on='품번', right_on='추출된_품번', how='left')
        return merged
    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
        return None

df = load_data()

# (이하 검색 UI 코드는 동일...)
st.title("🏗️ 자재 스펙 & 이미지 통합 조회")
query = st.text_input("🔍 검색어 입력 (대표코드, 품명, 품번)").strip()

if query and df is not None:
    results = df[df['대표코드'].str.contains(query, case=False, na=False) | 
                 df['품명'].str.contains(query, case=False, na=False) | 
                 df['품번'].str.contains(query, case=False, na=False)]
    if not results.empty:
        for _, row in results.iterrows():
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📋 자재 스펙")
                st.info(f"**대표코드:** {row['대표코드']}")
                st.write(f"**품명:** {row['품명']}")
                st.write(f"**품번:** {row['품번']}")
            with col2:
                st.subheader("🖼️ 이미지")
                if pd.notna(row.get('카카오톡_전송용_URL')):
                    st.image(row['카카오톡_전송용_URL'], use_container_width=True)
                else:
                    st.warning("등록된 이미지가 없습니다.")
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="유대리 스펙체크", layout="wide")

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
            spec_df['품번'] = spec_df['품번'].astype(str).str.strip()
            break
        except: continue

    for enc in encodings:
        try:
            img_df = pd.read_csv(img_file, encoding=enc)
            # 이미지 파일의 품번 컬럼 이름도 정리
            img_df['추출된_품번'] = img_df['추출된_품번'].astype(str).str.strip()
            break
        except: continue

    if spec_df is not None and img_df is not None:
        # [수정] how='outer'로 변경하여 양쪽 어디든 데이터가 있으면 다 가져옵니다.
        merged = pd.merge(spec_df, img_df[['추출된_품번', '카카오톡_전송용_URL']], 
                          left_on='품번', right_on='추출된_품번', how='outer')
        
        # [중요] 스펙 정보가 없는 경우(이미지 파일에만 있는 경우) 품번을 채워줍니다.
        merged['품번'] = merged['품번'].fillna(merged['추출된_품번'])
        
        # 비어있는 정보는 깔끔하게 '-'로 채우기
        merged = merged.fillna('-')
        
        return merged
    return None

df = load_data()

st.title("🏗️ 자재 스펙 & 이미지 통합 조회")
query = st.text_input("🔍 검색 (대표코드, 품명, 품번 입력)", "").strip()

if query:
    if df is not None:
        # 모든 검색 대상 컬럼을 문자열로 바꿔서 검색 (오류 방지)
        mask = (df['대표코드'].astype(str).str.contains(query, case=False, na=False) | 
                df['품명'].astype(str).str.contains(query, case=False, na=False) | 
                df['품번'].astype(str).str.contains(query, case=False, na=False))
        results = df[mask]
        
        if not results.empty:
            st.write(f"✅ 총 **{len(results)}**건의 자재가 검색되었습니다.")
            for _, row in results.iterrows():
                st.markdown("---")
                col1, col2 = st.columns([1, 1.2])
                with col1:
                    st.subheader("📋 자재 정보")
                    st.markdown(f"**🔹 대표코드:** {row.get('대표코드', '-')}")
                    st.markdown(f"**🔹 품명:** {row.get('품명', '-')}")
                    st.markdown(f"**🔹 품번:** {row.get('품번', '-')}")
                    st.markdown(f"**🔹 경면(전면):** {row.get('경면(전면)', '-')}")
                    st.markdown(f"**🔹 임가공처:** {row.get('임가공처', '-')}")
                with col2:
                    st.subheader("🖼️ 이미지 확인")
                    url = row.get('카카오톡_전송용_URL')
                    if pd.notna(url) and str(url).startswith('http'):
                        try:
                            st.image(url, use_container_width=True)
                            st.caption(f"🔗 [고화질 원본 보기]({url})")
                        except:
                            st.write("❌ 이미지를 불러올 수 없습니다.")
                    else:
                        st.write("이미지 준비 중입니다.")
        else:
            st.write("📍 검색 결과가 없습니다.")
    else:
        st.error("데이터 로드 실패")

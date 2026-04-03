# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
import sys
from datetime import datetime
import textwrap

# 프로젝트 루트 경로 추가
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# .env 파일 로드 (직접 구현)
def load_env():
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

load_env()

from src.survey_generator import SurveyGenerator
from src.research_design_generator import ResearchDesignGenerator
from src.database import SocialWelfareDB
from src.ai_engine import AIEngine

# 페이지 설정
st.set_page_config(
    page_title="AI 사회복지 연구 설계 도구",
    page_icon="🤖"
)

# DB 및 AI 엔진 초기화
db = SocialWelfareDB()

# 환경 변수 및 st.secrets에서 최신 키 로드 (Streamlit Cloud 환경 대응)
try:
    env_api_key = (
        st.secrets.get("OPENROUTER_API_KEY") or 
        st.secrets.get("OPENAI_API_KEY") or 
        os.environ.get("OPENROUTER_API_KEY") or 
        os.environ.get("OPENAI_API_KEY", "")
    )
except:
    env_api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY", "")

if 'api_key' not in st.session_state or not st.session_state.api_key:
    st.session_state.api_key = env_api_key

# 엔진 초기화 (최신 키 사용)
ai_engine = AIEngine(api_key=st.session_state.api_key or env_api_key)

# 세션 상태 초기화
if 'current_view' not in st.session_state:
    st.session_state.current_view = "list"  # list or detail
if 'selected_history_id' not in st.session_state:
    st.session_state.selected_history_id = None
if 'auth_id' not in st.session_state:
    st.session_state.auth_id = None
if 'auth_del_id' not in st.session_state:
    st.session_state.auth_del_id = None
if 'auth_down_id' not in st.session_state:
    st.session_state.auth_down_id = None

def main():
    # 세션 상태 기반 뷰 전환 (버튼 클릭 시 처리)

    # 프리미엄 디자인 시스템 (CSS) - 반드시 들여쓰기 없이 주입하여 마크다운 코드 블록 인식을 방지함
    css_code = """
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css">
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
            background-color: #F8FAFC !important;
        }
        .main-header {
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            padding: 40px 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px rgba(30, 58, 138, 0.2);
        }
        .main-header h1 {
            font-weight: 800 !important;
            letter-spacing: -1px;
            margin-bottom: 10px !important;
            color: white !important;
            margin-top: 0 !important;
        }
        .main-header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        /* 카드 스타일 적용 (Modern CSS :has 선택자 사용) */
        div[data-testid="stVerticalBlock"]:has(> div > div > div > .card-tag) {
            background-color: white !important;
            padding: 2rem 0 !important; /* 상하 여백만 부여, 좌우는 컬럼으로 조절 */
            border-radius: 20px !important;
            box-shadow: 0 12px 24px rgba(0,0,0,0.06) !important;
            border: 1px solid #E2E8F0 !important;
            margin-bottom: 2.5rem !important;
        }
        /* 카드 내부 여백 마커 숨기기 */
        .card-tag { display: none; }
        div.stMarkdown a {
            color: #2563EB !important;
            text-decoration: none !important;
            font-weight: 700 !important;
        }
        div.stMarkdown a:hover {
            color: #1D4ED8 !important;
            text-decoration: underline !important;
        }
        div[data-testid="baseButton-secondary"], div[data-testid="baseButton-secondary"] div {
            border-radius: 8px !important;
        }
        div[data-testid="baseButton-secondary"] {
            background-color: #F1F5F9 !important;
            color: #475569 !important;
            font-weight: 500 !important;
            height: 2.2rem !important;
            border: none !important;
            white-space: nowrap !important;
        }
        div[data-testid="baseButton-primary"] {
            background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%) !important;
            border: none !important;
            padding: 12px 24px !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.4) !important;
            border-radius: 10px !important;
        }
        hr {
            margin: 0.8rem 0 !important;
            border-color: #E2E8F0 !important;
        }
        </style>
    """
    st.markdown(textwrap.dedent(css_code).strip(), unsafe_allow_html=True)

    # 헤더 섹션
    header_html = """
        <div class="main-header">
            <h1>🤖 AI 사회복지 연구 리서치 허브</h1>
            <p>지능형 알고리즘을 통한 최적의 연구 설계 및 조사 도구 자동화 시스템</p>
        </div>
    """
    st.markdown(textwrap.dedent(header_html).strip(), unsafe_allow_html=True)

    # 상단: 연구 생성 폼
    render_generation_form()
    
    st.divider()
    
    # 하단: 생성 이력 목록
    render_history_view()

def render_generation_form():
    with st.container():
        st.markdown('<div class="card-tag"></div>', unsafe_allow_html=True)
        _, content_col, _ = st.columns([0.05, 0.9, 0.05])
        with content_col:
            st.subheader("💡 연구 주제 입력")
            # 세션 상태에 생성된 주제 저장
            if 'ai_recommended_topics' not in st.session_state:
                st.session_state.ai_recommended_topics = []
            
            # 초기값 설정 (최초 실행 시 빈값)
            if 'main_topic_input' not in st.session_state:
                st.session_state.main_topic_input = ""

            topic_input = st.text_area(
                "기획하고 계신 사회복지 연구 주제를 자유롭게 입력해 주세요.",
                placeholder="예: 재택근무가 사회복지사의 직무 만족도와 서비스 질에 미치는 영향 분석",
                height=75,
                key="main_topic_input"
            )

            def on_recommend_topic():
                # 추천 주제 생성 및 세션 상태 업데이트
                history = db.get_all_history()
                existing_topics = [item['topic'] for item in history] if history else []
                new_topic = ai_engine.generate_single_topic(exclude_topics=existing_topics)
                st.session_state.main_topic_input = new_topic

            # AI 도움받기 섹션 (간소화) - 콜백 방식으로 변경하여 API 오류 회피
            st.button("🪄 AI에게 주제 추천받기", use_container_width=True, on_click=on_recommend_topic)

            st.divider()

            st.subheader("👤 연구자 정보")
            col1, col2, col3 = st.columns(3)
            with col1:
                student_id = st.text_input("학번", placeholder="20240000")
            with col2:
                name = st.text_input("이름", placeholder="홍길동")
            with col3:
                password = st.text_input("비밀번호 (숫자 4자리)", placeholder="1234", type="password", max_chars=4)

            st.divider()
            
            if st.button("🚀 AI 연구 설계 시작", type="primary", use_container_width=True):
                # 4자리 숫자 비밀번호 유효성 검사
                if not (password.isdigit() and len(password) == 4):
                    st.error("비밀번호는 숫자 4자리로 입력해 주세요.")
                    return

                # 텍스트 영역의 최신 값 가져오기
                current_topic = st.session_state.main_topic_input
                
                if not st.session_state.api_key or st.session_state.api_key == "your_api_key_here":
                    st.error("⚠️ **API Key**가 설정되지 않았거나 초기값입니다.")
                    return
                    
                if not current_topic:
                    st.error("연구 주제를 입력해 주세요.")
                    return
                if not all([student_id, name, password]):
                    st.error("연구자 정보를 모두 입력해 주세요.")
                    return

                with st.spinner("AI가 연구 주제를 분석하고 설계를 생성 중입니다..."):
                    try:
                        # 1. AI 주제 분석
                        topic_data = ai_engine.analyze_topic(current_topic)
                        
                        # 2. 설문 및 설계서 생성
                        survey_gen = SurveyGenerator(topic_dict=topic_data)
                        survey_res = survey_gen.generate_full_survey()
                        
                        researcher_info = {"student_id": student_id, "name": name, "password": password}
                        design_gen = ResearchDesignGenerator(topic_dict=topic_data, researcher_info=researcher_info)
                        design_res = design_gen.generate_full_design()
                        
                        # 3. DB 저장
                        db.save_generation(current_topic, researcher_info, design_res, survey_res)
                        
                        st.success("✅ 생성이 완료되었습니다! 아래 '조사연구설계서' 목록에서 확인하실 수 있습니다.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"생성 중 오류가 발생했습니다: {str(e)}")

def render_history_view():
    history = db.get_all_history()
    
    if not history:
        st.info("아직 생성된 연구 이력이 없습니다. '새 연구 생성' 탭에서 시작해 보세요.")
        return

    # 상세 보기 모드인 경우
    if st.session_state.current_view == "detail" and st.session_state.selected_history_id:
        render_detail_view(st.session_state.selected_history_id)
        if st.button("⬅️ 목록으로 돌아가기"):
            st.session_state.current_view = "list"
            st.rerun()
        return

    # 이력 목록 섹션 시작 (컨테이너 기반 카드 스타일)
    with st.container():
        st.markdown('<div class="card-tag"></div>', unsafe_allow_html=True)
        _, content_col, _ = st.columns([0.05, 0.9, 0.05])
        with content_col:
            st.subheader("📂 조사연구설계서 리스트")
            
            # 테이블 헤더 (다운로드 버튼 폭 확보를 위해 비율 조정: 4.5 + 1.8 + 1.7 + 2.0 = 10)
            cols = st.columns([4.5, 1.8, 1.7, 2.0])
            cols[0].write("**연구 주제**")
            cols[1].write("**연구자**")
            cols[2].write("**생성일**")
            cols[3].write("**자료**")
            st.divider()

            for item in history:
                cols = st.columns([4.5, 1.8, 1.7, 2.0])
                # 연구 주제를 클릭하면 상세 보기 권한 확인(auth_id) 설정 (ID 타입을 명시적으로 str로 맞춰 비교 안전성 확보)
                if cols[0].button(item['topic'], key=f"title_{item['id']}", use_container_width=True):
                    st.session_state.auth_id = item['id']
                    st.session_state.auth_down_id = None
                    st.rerun()
                    
                cols[1].write(item['researcher_name'])
                cols[2].write(item['created_at'])
                
                if cols[3].button("다운로드", key=f"down_{item['id']}", use_container_width=True):
                    st.session_state.auth_down_id = item['id']
                    st.session_state.auth_id = None
                    st.rerun()
                
                # 보기 비밀번호 확인 창
                if st.session_state.auth_id == item['id']:
                    with st.container():
                        st.info("상세 내용을 보려면 비밀번호를 입력하세요.")
                        pw_input = st.text_input("비밀번호 4자리", type="password", key=f"pw_in_{item['id']}")
                        col_c1, col_c2 = st.columns(2)
                        if col_c1.button("확인", key=f"pw_btn_{item['id']}", use_container_width=True):
                            detail = db.get_generation_detail(item['id'])
                            # 구글 시트에서 앞자리 0이 소실될 수 있으므로 zfill(4)로 보정
                            stored_pw = str(detail.get('password', '')).strip().replace(".0", "").zfill(4) if detail else ""
                            input_pw = str(pw_input).strip().zfill(4)
                            if detail and stored_pw == input_pw:
                                st.session_state.selected_history_id = item['id']
                                st.session_state.current_view = "detail"
                                st.session_state.auth_id = None
                                st.rerun()
                            else:
                                if detail:
                                    st.error("비밀번호가 일치하지 않습니다.")
                                else:
                                    st.error("해당 항목의 상세 데이터를 불러올 수 없습니다.")
                        if col_c2.button("취소", key=f"pw_cancel_{item['id']}", use_container_width=True):
                            st.session_state.auth_id = None
                            st.rerun()

                # 다운로드 비밀번호 확인 창
                if st.session_state.auth_down_id == item['id']:
                    with st.container():
                        st.info("다운로드하려면 비밀번호를 입력하세요.")
                        pw_down_input = st.text_input("비밀번호 4자리", type="password", key=f"pw_down_in_{item['id']}")
                        col_down1, col_down2 = st.columns(2)
                        
                        detail = db.get_generation_detail(item['id'])
                        stored_pw = str(detail.get('password', '')).strip().replace(".0", "").zfill(4) if detail else ""
                        input_down_pw = str(pw_down_input).strip().zfill(4)
                        if detail and stored_pw == input_down_pw:
                            combined_data = format_combined_data(detail)
                            col_down1.download_button(
                                "파일 다운로드",
                                data=combined_data,
                                file_name=f"연구설계서_통합_{item['id']}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        else:
                            if col_down1.button("확인", key=f"pw_down_btn_{item['id']}", use_container_width=True):
                                if pw_down_input: st.error("비밀번호가 틀렸습니다.")
                                
                        if col_down2.button("취소", key=f"pw_down_cancel_{item['id']}", use_container_width=True):
                            st.session_state.auth_down_id = None
                            st.rerun()
                st.divider()

def render_detail_view(history_id):
    with st.container():
        st.markdown('<div class="card-tag"></div>', unsafe_allow_html=True)
        _, content_col, _ = st.columns([0.05, 0.9, 0.05])
        with content_col:
            detail = db.get_generation_detail(history_id)
            if not detail:
                st.error("데이터를 불러올 수 없습니다.")
                return

            st.subheader(f"📄 {detail['topic']}")
            
            # 통합 뷰: 연구설계서 + 설문지
            design = detail['design']
            survey = detail['survey']
            
            st.markdown("### 📝 1. 연구설계서")
            hwp_text = format_design_to_hwp(design, detail)
            st.text(hwp_text)
            
            st.divider()
            
            st.markdown("### 📋 2. 설문지 문항")
            st.markdown(f"**총 문항 수**: {len(survey.get('all_items', [])) if 'all_items' in survey else 0}개")
            for section in survey.get('sections', []):
                st.markdown(f"**{section['name']}**")
                for item in section['items']:
                    st.markdown(f"- {item['text']}")
            
            st.divider()

def render_settings():
    with st.container():
        st.markdown('<div class="card-tag"></div>', unsafe_allow_html=True)
        _, content_col, _ = st.columns([0.05, 0.9, 0.05])
        with content_col:
            st.subheader("⚙️ 시스템 설정")
            new_key = st.text_input("OpenRouter 또는 OpenAI API Key", value=st.session_state.api_key, type="password")
            if st.button("저장"):
                st.session_state.api_key = new_key
                st.success("설정이 저장되었습니다.")

def format_combined_data(detail):
    """연구설계서와 설문지를 하나의 텍스트로 통합"""
    design_text = format_design_to_hwp(detail['design'], detail)
    survey = detail['survey']
    
    survey_text = "\n\n" + "="*50 + "\n"
    survey_text += "부록: 설문지 문항\n"
    survey_text += "="*50 + "\n"
    
    for section in survey.get('sections', []):
        survey_text += f"\n[{section['name']}]\n"
        for item in section['items']:
            survey_text += f"- {item['text']}\n"
            
    return design_text + survey_text

def format_design_to_hwp(design, detail):
    """연구설계서 데이터를 학술적 양식으로 변환"""
    # 데이터 안전하게 추출 (get 사용)
    p_purpose = design.get('2_연구목적과배경', {})
    p_vars = design.get('5_변수정의', {})
    p_sampling = design.get('8_표집계획', {})
    p_analysis = design.get('12_데이터분석', {})
    
    hwp_text = f"""사회복지연구 설계서
제출자 정보: {detail.get('researcher_id','')} / {detail.get('researcher_name','')}
생성 일시: {detail.get('created_at','')}

1. 연구 주제: {design.get('1_연구주제', {}).get('한줄', 'N/A')}

2. 연구 목적과 배경
 가. 필요성:
{p_purpose.get('necessity', 'N/A')}
 나. 배경:
{p_purpose.get('background', 'N/A')}

3. 연구문제 (RQ)
{chr(10).join([f" RQ{i+1}: {q}" for i, q in enumerate(design.get('3_연구문제', []))])}

4. 연구 가설 (H)
{chr(10).join([f" H{i+1}: {h.get('H'+str(i+1), h.get('H1', ''))} (방향성: {h.get('direction', 'N/A')})" for i, h in enumerate(design.get('4_가설', []))])}

5. 변수 정의 및 측정 수준
 가. 독립변수: {p_vars.get('독립변수', {}).get('명칭', 'N/A')}
    - 조작적 정의: {p_vars.get('독립변수', {}).get('조작적정의', 'N/A')}
    - 측정수준: {p_vars.get('독립변수', {}).get('측정수준', 'N/A')}
 나. 종속변수: {p_vars.get('종속변수', {}).get('명칭', 'N/A')}
    - 조작적 정의: {p_vars.get('종속변수', {}).get('조작적정의', 'N/A')}
 다. 통제변수: {', '.join(design.get('5_변수정의', {}).get('통제변수', {}).get('명칭', []))}

6. 표집 및 조사 설계
 - 모집단: {p_sampling.get('모집단', 'N/A')}
 - 표집방법: {p_sampling.get('표집방법', 'N/A')}
 - 목표표본수: {p_sampling.get('목표표본수', 'N/A')}

7. 자료분석 계획
 - 분석방법: {p_analysis.get('가설검증', 'N/A')}
 - 소프트웨어: {p_analysis.get('소프트웨어', 'N/A')}
"""
    return hwp_text

if __name__ == "__main__":
    main()
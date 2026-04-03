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

# .env 파일 로드
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
    page_title="사회복지 연구 설계 도구",
    page_icon=""
)

db = SocialWelfareDB()

def get_api_key():
    try:
        if "OPENROUTER_API_KEY" in st.secrets and st.secrets["OPENROUTER_API_KEY"]:
            return str(st.secrets["OPENROUTER_API_KEY"]).strip()
        if "OPENAI_API_KEY" in st.secrets:
            return str(st.secrets["OPENAI_API_KEY"]).strip()
        try:
            gsheets = st.secrets.get("connections", {}).get("gsheets", {})
            if "OPENROUTER_API_KEY" in gsheets:
                return str(gsheets["OPENROUTER_API_KEY"]).strip()
        except:
            pass
    except:
        pass
    return str(os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY", "")).strip()

env_api_key = get_api_key()

if 'api_key' not in st.session_state or not st.session_state.api_key:
    st.session_state.api_key = env_api_key

ai_engine = AIEngine(api_key=st.session_state.api_key or env_api_key)

if 'current_view' not in st.session_state:
    st.session_state.current_view = "list"
if 'selected_history_id' not in st.session_state:
    st.session_state.selected_history_id = None
if 'auth_id' not in st.session_state:
    st.session_state.auth_id = None
if 'auth_down_id' not in st.session_state:
    st.session_state.auth_down_id = None
if 'topic_area' not in st.session_state:
    st.session_state.topic_area = ""

def main():
    st.title("사회복지 연구 리서치 허브")
    st.caption("지능형 알고리즘을 통한 최적의 연구 설계 및 조사 도구 자동화 시스템")
    st.divider()

    render_generation_form()
    st.divider()
    render_history_view()

def render_generation_form():
    st.subheader("연구 주제 입력")
    
    if 'topic_area' not in st.session_state:
        st.session_state.topic_area = ""

    st.text_area(
        "기획하고 계신 사회복지 연구 주제를 자유롭게 입력해 주세요.",
        placeholder="예: 재택근무가 사회복지사의 직무 만족도와 서비스 질에 미치는 영향 분석",
        height=50,
        key="topic_area"
    )

    def on_recommend_topic():
        history = db.get_all_history()
        existing_topics = [item['topic'] for item in history] if history else []
        new_topic = ai_engine.generate_single_topic(exclude_topics=existing_topics)
        st.session_state.topic_area = new_topic

    st.button("연구 주제 추천받기", use_container_width=True, on_click=on_recommend_topic)
    st.divider()

    st.subheader("연구자 정보")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("학번", placeholder="20240000", key="reg_student_id")
    with col2:
        st.text_input("이름", placeholder="홍길동", key="reg_name")
    with col3:
        st.text_input("비밀번호 (숫자 4자리)", placeholder="1234", type="password", max_chars=4, key="reg_password")

    st.divider()
    
    if st.button("연구 설계 시작", type="primary", use_container_width=True):
        sid = st.session_state.reg_student_id
        nm = st.session_state.reg_name
        pw = st.session_state.reg_password
        
        if not (pw.isdigit() and len(pw) == 4):
            st.error("비밀번호는 숫자 4자리로 입력해 주세요.")
            return

        current_topic = st.session_state.topic_area
        
        if not st.session_state.api_key:
            st.error("API Key가 설정되지 않았습니다.")
            return
            
        if not current_topic:
            st.error("연구 주제를 입력해 주세요.")
            return
        if not all([sid, nm]):
            st.error("연구자 정보를 모두 입력해 주세요.")
            return

        with st.spinner("LLM이 연구 분석 및 설계를 생성 중입니다..."):
            try:
                topic_data = ai_engine.analyze_topic(current_topic)
                survey_res = SurveyGenerator(topic_dict=topic_data).generate_full_survey()
                r_info = {"student_id": sid, "name": nm, "password": pw}
                design_res = ResearchDesignGenerator(topic_dict=topic_data, researcher_info=r_info).generate_full_design()
                db.save_generation(current_topic, r_info, design_res, survey_res)
                st.success("생성이 완료되었습니다!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"생성 중 오류 발생: {str(e)}")

def render_history_view():
    history = db.get_all_history()
    if not history:
        st.info("아직 생성된 연구 이력이 없습니다.")
        return

    if st.session_state.current_view == "detail" and st.session_state.selected_history_id:
        render_detail_view(st.session_state.selected_history_id)
        if st.button("목록으로 돌아가기"):
            st.session_state.current_view = "list"
            st.rerun()
        return

    st.subheader("조사연구설계서 리스트")
    cols = st.columns([4.9, 1.8, 1.8, 1.5])
    cols[0].markdown("<div style='text-align: center;'><b>연구 주제</b></div>", unsafe_allow_html=True)
    cols[1].markdown("<div style='text-align: center;'><b>연구자</b></div>", unsafe_allow_html=True)
    cols[2].markdown("<div style='text-align: center;'><b>생성일</b></div>", unsafe_allow_html=True)
    cols[3].markdown("<div style='text-align: center;'><b>자료</b></div>", unsafe_allow_html=True)

    st.divider()

    for item in history:
        r_cols = st.columns([4.9, 1.8, 1.8, 1.5])
        if r_cols[0].button(item['topic'], key=f"t_{item['id']}", use_container_width=True):
            st.session_state.auth_id = item['id']
            st.session_state.auth_down_id = None
            st.rerun()
            
        r_cols[1].markdown(f"<div style='text-align: center;'>{item.get('researcher_name', 'N/A')}</div>", unsafe_allow_html=True)
        r_cols[2].markdown(f"<div style='text-align: center;'>{item.get('created_at', 'N/A')}</div>", unsafe_allow_html=True)
        
        if r_cols[3].button("다운로드", key=f"d_{item['id']}", use_container_width=True):
            st.session_state.auth_down_id = item['id']
            st.session_state.auth_id = None
            st.rerun()
        
        if st.session_state.get('auth_id') == item['id']:
            pw = st.text_input("비밀번호 입력", type="password", key=f"p_{item['id']}")
            c1, c2 = st.columns(2)
            if c1.button("확인", key=f"pb_{item['id']}", use_container_width=True):
                detail = db.get_generation_detail(item['id'])
                stored_pw = str(detail.get('password', '')).strip().replace(".0", "").zfill(4) if detail else ""
                if detail and stored_pw == pw.strip().zfill(4):
                    st.session_state.selected_history_id = item['id']
                    st.session_state.current_view = "detail"
                    st.session_state.auth_id = None
                    st.rerun()
                else:
                    st.error("비밀번호 불일치")
            if c2.button("취소", key=f"pc_{item['id']}", use_container_width=True):
                st.session_state.auth_id = None
                st.rerun()

        if st.session_state.get('auth_down_id') == item['id']:
            pwd = st.text_input("비밀번호 입력", type="password", key=f"pd_{item['id']}")
            dc1, dc2 = st.columns(2)
            detail = db.get_generation_detail(item['id'])
            stored_pw = str(detail.get('password', '')).strip().replace(".0", "").zfill(4) if detail else ""
            
            if detail and stored_pw == pwd.strip().zfill(4):
                data = format_combined_data(detail)
                dc1.download_button("파일 다운로드", data=data, file_name=f"연구설계_{item['id']}.txt", use_container_width=True)
            else:
                if dc1.button("확인", key=f"pdb_{item['id']}", use_container_width=True):
                    st.error("비밀번호 불일치")
            if dc2.button("취소", key=f"pdc_{item['id']}", use_container_width=True):
                st.session_state.auth_down_id = None
                st.rerun()
        st.divider()

def render_detail_view(history_id):
    detail = db.get_generation_detail(history_id)
    if not detail:
        st.error("데이터 로드 실패")
        return

    st.subheader(f"{detail['topic']}")
    tab1, tab2 = st.tabs(["1. 연구설계서", "2. 설문지 문항"])
    
    with tab1:
        st.text(format_design_to_hwp(detail.get('design', {}), detail))
    with tab2:
        survey = detail.get('survey', {})
        for section in survey.get('sections', []):
            with st.expander(f"📌 {section['name']}", expanded=True):
                for item in section['items']:
                    st.markdown(f"- {item['text']}")

def format_combined_data(detail):
    design_text = format_design_to_hwp(detail['design'], detail)
    survey = detail['survey']
    survey_text = "\n\n" + "="*50 + "\n부록: 설문지 문항\n" + "="*50 + "\n"
    for section in survey.get('sections', []):
        survey_text += f"\n[{section['name']}]\n"
        for item in section['items']:
            survey_text += f"- {item['text']}\n"
    return design_text + survey_text

def format_design_to_hwp(design, detail):
    p_p = design.get('2_연구목적과배경', {})
    p_v = design.get('5_변수정의', {})
    p_s = design.get('8_표집계획', {})
    p_a = design.get('12_데이터분석', {})
    
    return f"""사회복지연구 설계서
제출자: {detail.get('researcher_id','')} / {detail.get('researcher_name','')}
일시: {detail.get('created_at','')}

1. 주제: {design.get('1_연구주제', {}).get('한줄', 'N/A')}

2. 목적 및 배경
 가. 필요성: {p_p.get('necessity', 'N/A')}
 나. 배경: {p_p.get('background', 'N/A')}

3. 연구문제
{chr(10).join([f" RQ{i+1}: {q}" for i, q in enumerate(design.get('3_연구문제', []))])}

4. 가설
{chr(10).join([f" H{i+1}: {h.get('H'+str(i+1), h.get('H1', ''))} ({h.get('direction', 'N/A')})" for i, h in enumerate(design.get('4_가설', []))])}

5. 변수
 가. 독립: {p_v.get('독립변수', {}).get('명칭', 'N/A')} ({p_v.get('독립변수', {}).get('조작적정의', 'N/A')})
 나. 종속: {p_v.get('종속변수', {}).get('명칭', 'N/A')} ({p_v.get('종속변수', {}).get('조작적정의', 'N/A')})
 다. 통제: {', '.join(design.get('5_변수정의', {}).get('통제변수', {}).get('명칭', []))}

6. 표집: {p_s.get('모집단', 'N/A')} / {p_s.get('표집방법', 'N/A')} / {p_s.get('목표표본수', 'N/A')}
7. 분석: {p_a.get('가설검증', 'N/A')} ({p_a.get('소프트웨어', 'N/A')})
"""

if __name__ == "__main__":
    main()

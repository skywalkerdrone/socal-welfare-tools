# -*- coding: utf-8 -*-
import os
import json
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

# 로컬 .env 로드
load_dotenv()

class AIEngine:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Args:
            api_key: API Key (없으면 환경변수에서 로드)
            model: 사용할 AI 모델 명칭
        """
        # OpenRouter 키 우선, 없으면 OpenAI 키 사용
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        # 구글 제미나이 또는 미스트랄 무료 모델로 명시적으로 변경 (openrouter/auto-free 대신 권장)
        self.model = model or os.getenv("AI_MODEL_NAME", "google/gemini-pro-1.5-exp-0827:free")
        self.base_url = os.getenv("AI_API_BASE", "https://openrouter.ai/api/v1")
        
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                default_headers={
                    "HTTP-Referer": "https://social-welfare-tool.streamlit.app", # 식별용 주소
                    "X-Title": "AI Social Welfare Research Tool"
                }
            )
        else:
            self.client = None

    def analyze_topic(self, topic_text: str) -> Dict:
        """
        주제 텍스트를 분석하여 연구 설계에 필요한 구조화된 데이터 반환
        """
        if not self.client:
            raise ValueError("API Key가 설정되지 않았습니다. .env 파일을 확인해 주세요.")

        system_prompt = """사회복지 연구 전문가로서 사용자의 연구 주제를 분석하여 연구 설계에 필요한 JSON 데이터를 생성해 주세요.
반환 형식은 반드시 다음 키를 포함하는 유효한 JSON이어야 합니다:
{
  "name": "연구 제목 (입력된 주제를 바탕으로 학술적으로 정리)",
  "target": "연구 대상자 (예: 홀몸 어르신, 사회복지사 등)",
  "independent": {
    "name": "독립변수 명칭",
    "operational": "독립변수의 조작적 정의",
    "measurement_level": "등간척도",
    "levels": "5점 리커트 척도",
    "items": ["설문 문항1", "설문 문항2", "설문 문항3", "설문 문항4", "설문 문항5", "설문 문항6"]
  },
  "dependent": {
    "name": "종속변수 명칭",
    "operational": "종속변수의 조작적 정의",
    "measurement_level": "등간척도",
    "levels": "5점 리커트 척도",
    "items": ["설문 문항1", "설문 문항2", "설문 문항3", "설문 문항4", "설문 문항5", "설문 문항6"]
  },
  "control_variables": ["통제변수1", "통제변수2", "통제변수3"],
  "scale_type": "5점 리커트 척도"
}
문항은 사회복지 실천 현장에서 실제로 사용될 수 있을 만큼 명확하고 타당해야 합니다."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt + "\n\n중요: 반드시 JSON 형식으로만 응답하며, 앞뒤에 코드 블록(```json)을 붙이지 마세요."},
                    {"role": "user", "content": f"다음 주제를 분석해 주세요: {topic_text}"}
                ]
            )
            
            content = response.choices[0].message.content.strip()
            # 마크다운 코드 블록 제거 로직 추가
            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()
            
            result = json.loads(content)
            return result

        except Exception as e:
            # 오류 발생 시 최소한의 형태는 유지하여 반환 (실제 서비스에서는 상세 오류 처리 필요)
            print(f"AI 분석 오류: {e}")
            raise e

    def generate_research_topics(self, category: str) -> list:
        """
        특정 복지 카테고리에 맞는 연구 주제 5가지를 생성하여 리스트로 반환
        """
        if not self.client:
            raise ValueError("API Key가 설정되지 않았습니다.")

        system_prompt = f"""사회복지 연구 전문가로서 '{category}' 분야에 관한 혁신적이고 실천적인 연구 주제 5가지를 제안해 주세요.
각 주제는 학술지 투고가 가능할 정도의 수준이어야 하며, 한국 사회복지 현장의 최신 트렌드를 반영해야 합니다.
모든 응답은 반드시 **한국어**로 작성해야 합니다.
응답은 반드시 주제 텍스트만 포함하는 JSON 리스트 형식이어야 합니다.
예: ["주제1", "주제2", "주제3", "주제4", "주제5"]"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt + "\n\n중요: 반드시 [" + '"주제1", "주제2"...] 형식으로만 응답하며, 마크다운 코드 블록을 포함하지 마세요.'},
                    {"role": "user", "content": f"'{category}' 분야의 연구 주제 5개를 추천해 주세요."}
                ]
            )
            
            content = response.choices[0].message.content.strip()
            # 마크다운 코드 블록 제거 로직 보완
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```JSON", "").replace("```", "").strip()
            
            # 제어 문자 제거 (JSON 파싱 오류 방지)
            import re
            content = re.sub(r'[\x00-\x1F\x7F]', '', content)
            
            topics = json.loads(content)
            if isinstance(topics, list):
                return topics[:5]
            return []
        except Exception as e:
            print(f"AI 주제 생성 오류: {e}")
            return [
                f"{category} 관련 최근 정책 변화와 서비스 이용실태 분석",
                f"{category} 대상자의 삶의 질 향상을 위한 프로그램 효과성 검증",
                f"디지털 전환 시대의 {category} 전달체계 개선 방안 연구",
                f"{category} 전담 사회복지사의 소진(Burnout) 영향 요인 분석",
                f"지역사회 중심의 {category} 돌봄 네트워크 구축 전략"
            ]

    def generate_single_topic(self, exclude_topics: Optional[list] = None) -> str:
        """
        랜덤한 복지 분야를 선정하여 하나의 연구 주제를 생성하고 문자열로 반환
        Args:
            exclude_topics: 추천에서 제외할 주제 목록 (중복 방지)
        """
        import random
        categories = ["노인복지", "청소년복지", "여성복지", "외국인복지", "장애인복지", "아동복지", "지역복지"]
        category = random.choice(categories)

        if not self.client:
            return f"{category} 관련 최근 정책 변화와 서비스 이용실태 분석"

        # 제외할 주제 문구 생성
        exclude_prompt = ""
        if exclude_topics and len(exclude_topics) > 0:
            exclude_prompt = f"\n다음 주제들은 이미 존재하므로 이와 동일하거나 아주 유사한 주제는 **절대** 추천하지 마세요:\n" + "\n".join([f"- {t}" for t in exclude_topics[:10]])

        system_prompt = f"""사회복지 연구 전문가로서 '{category}' 분야에 관한 혁신적이고 실천적인 연구 주제 1가지만 추천해 주세요.
학술적으로 가치 있고 실천 현장에서 활용 가능한 구체적인 제목이어야 합니다.
**반드시 한국어로만 작성하고, 영문 번역이나 괄호 안의 영문 표기를 절대 포함하지 마세요.**
답변은 반드시 마침표 없이 한 줄의 완성된 문장(제목 형태)으로만 작성하세요.
설명이나 인사말 없이 오직 핵심 연구 주제 텍스트 50자 이내로만 응답하세요.{exclude_prompt}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"'{category}' 관련하여 기존에 없던 새로운 연구 주제 1개를 추천해 주세요."}
                ]
            )
            
            topic = response.choices[0].message.content.strip()
            
            # 따옴표, 괄호 및 불필요한 공백 제거 (정규표현식 활용)
            import re
            # 괄호와 그 안의 내용 제거 (번역 방지)
            topic = re.sub(r'\([^)]*\)', '', topic)
            # 영문자 제거 (영단어 포함 방지)
            topic = re.sub(r'[a-zA-Z]', '', topic)
            # 모든 종류의 따옴표 제거 (쌍따옴표, 홑따옴표, 스마트 따옴표 등)
            topic = re.sub(r'["\'`‘’“”]', '', topic)
            
            # 앞뒤 불필요한 문장부호 및 공백 제거
            topic = topic.strip(' .,')
            # 여러 개의 공백을 하나로 축소
            topic = re.sub(r'\s+', ' ', topic).strip()
            
            # 만약 결과가 너무 짧아지면(실패 시) 기본값 반환
            if len(topic) < 5:
                return f"{category} 관련 사회복지 서비스 실태 및 개선 방안 연구"

            return topic
        except Exception as e:
            print(f"AI 단일 주제 생성 오류: {e}")
            return f"{category} 기반 사회복지 실천 모델의 효과성 및 개선 방안 연구"

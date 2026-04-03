# -*- coding: utf-8 -*-
"""
설문문항 생성기
"""

from typing import Dict, List, Tuple, Optional
from config import TOPICS, LIKERT_LABELS

class SurveyGenerator:
    """설문문항 자동 생성 클래스"""

    def __init__(self, topic_id: Optional[int] = None, topic_dict: Optional[Dict] = None, researcher_info: Optional[Dict] = None):
        self.topic_id = topic_id or 1
        if topic_dict:
            self.topic = topic_dict
        else:
            self.topic = TOPICS[self.topic_id]
        self.researcher_info = researcher_info or {}

    def generate_intro(self) -> str:
        """설문 인트로 생성"""
        topic_name = self.topic["name"]
        return f"""본 설문은 {topic_name} 관련 연구입니다.
익명이며, 응답 소요 시간은 약 5분입니다.
모든 응답은 연구 목적으로만 사용되며, 개인정보는 철저히 보호됩니다.
감사합니다."""

    def generate_demographic_items(self) -> List[Dict]:
        """인구통계학적 문항 생성"""
        items = []

        return items

    def generate_independent_items(self) -> List[Dict]:
        """독립변수 측정 문항 생성"""
        items = []
        indep = self.topic["independent"]

        if self.topic_id == 1:
            # ... 기존 1번 로직 유지 시 생략 가능하지만, 여기서는 공통 항목 추가로 대체
            pass
        
        # 커스텀 주제 지원: topic_dict['independent']['items']가 있으면 활용
        if "items" in indep:
            for idx, text in enumerate(indep["items"], start=1):
                items.append({
                    "id": f"indep_custom_{idx}",
                    "text": text,
                    "type": "likert_5",
                    "options": [{"value": i, "label": f"{i}점"} for i in range(1, 6)],
                    "variable": f"indep_var_{idx}"
                })
        
        return items

    def generate_dependent_items(self) -> List[Dict]:
        """종속변수 측정 문항 (리커트 5점) 생성"""
        items = []
        dep = self.topic["dependent"]

        # 리커트 5점 옵션
        likert_options = [
            {"value": 1, "label": "매우 그렇지 않다"},
            {"value": 2, "label": "그렇지 않다"},
            {"value": 3, "label": "보통이다"},
            {"value": 4, "label": "그렇다"},
            {"value": 5, "label": "매우 그렇다"}
        ]

        if "items" in dep:
            for idx, text in enumerate(dep["items"], start=1):
                items.append({
                    "id": f"dep_custom_{idx}",
                    "text": text,
                    "type": "likert_5",
                    "options": likert_options,
                    "variable": f"dep_var_{idx}"
                })
        elif "items_support" in dep:
             # 기존 3번 로직 스타일 지원
             pass

        return items

    def generate_control_items(self) -> List[Dict]:
        """통제변수 문항 생성"""
        items = []
        controls = self.topic["control_variables"]

        # 기본 통제변수 매핑
        control_map = {
            "연령대": {"id": "control_age", "type": "single", "options": ["40대", "50대", "60대 이상"]},
            "취업 상태": {"id": "control_employment", "type": "single", "options": ["취업", "비취업"]},
            "건강 자기평가": {
                "id": "control_health_self",
                "type": "likert_5",
                "options": [
                    {"value": 1, "label": "매우 나쁨"},
                    {"value": 2, "label": "나쁨"},
                    {"value": 3, "label": "보통"},
                    {"value": 4, "label": "좋음"},
                    {"value": 5, "label": "매우 좋음"}
                ]
            },
            "만성질환 유무": {"id": "control_chronic", "type": "single", "options": ["있음", "없음"]},
            "1인가구 여부": {"id": "control_single", "type": "single", "options": ["예", "아니오"]},
            "배우자 유무": {"id": "control_spouse", "type": "single", "options": ["있음", "없음"]}
        }

        for ctrl in controls:
            if ctrl in control_map:
                ctrl_info = control_map[ctrl]
                items.append({
                    "id": ctrl_info["id"],
                    "text": f"{ctrl}을(를) 선택해 주세요." if ctrl_info["type"] == "single" else f"{ctrl}에 대해 응답해 주세요.",
                    "type": ctrl_info["type"],
                    "options": ctrl_info["options"],
                    "variable": ctrl_info["id"].replace("control_", "")
                })
            else:
                # 정의되지 않은 통제변수는 기본 주관식 또는 단순 선택형으로 생성
                items.append({
                    "id": f"control_custom_{controls.index(ctrl)}",
                    "text": f"{ctrl}에 대해 입력하거나 선택해 주세요.",
                    "type": "single",
                    "options": ["해당함", "해당하지 않음"], # 기본값
                    "variable": f"custom_ctrl_{controls.index(ctrl)}"
                })

        return items

    def generate_full_survey(self) -> Dict:
        """전체 설문 생성"""
        survey = {
            "topic_id": self.topic_id,
            "topic_name": self.topic["name"],
            "intro": self.generate_intro(),
            "sections": [
                {
                    "name": "인구통계학적 정보",
                    "items": self.generate_demographic_items()
                },
                {
                    "name": "독립변수",
                    "items": self.generate_independent_items()
                },
                {
                    "name": "종속변수",
                    "items": self.generate_dependent_items()
                },
                {
                    "name": "통제변수",
                    "items": self.generate_control_items()
                }
            ]
        }

        # 모든 아이템 평탄화
        all_items = []
        for section in survey["sections"]:
            all_items.extend(section["items"])
        survey["all_items"] = all_items
        survey["total_items"] = len(all_items)

        return survey

    def export_to_dict(self) -> Dict:
        """내보내기용 딕셔너리"""
        survey = self.generate_full_survey()

        # 변수 정의서 생성
        var_defs = {
            "독립변수": {
                "name": self.topic["independent"].get("name", "독립변수"),
                "operational_definition": self.topic["independent"].get("operational", "정의되지 않음"),
                "measurement_level": self.topic["independent"].get("measurement_level", "등간척도"),
                "items": self.topic["independent"].get("items", [])
            },
            "종속변수": {
                "name": self.topic["dependent"]["name"],
                "operational_definition": self.topic["dependent"]["operational"],
                "measurement_level": self.topic["dependent"]["measurement_level"],
                "items": self.topic["dependent"]["items"] if "items" in self.topic["dependent"]
                        else {"지지감": self.topic["dependent"]["items_support"],
                              "고립감": self.topic["dependent"]["items_isolation"]}
            },
            "통제변수": self.topic["control_variables"]
        }

        return {
            "survey": survey,
            "variable_definitions": var_defs,
            "metadata": {
                "topic_id": self.topic_id,
                "scale_type": self.topic["scale_type"],
                "generated_by": "Social Welfare Survey Generator v0.1"
            }
        }
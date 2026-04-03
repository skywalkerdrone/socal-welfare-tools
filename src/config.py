# -*- coding: utf-8 -*-
"""
설문 주제 구성 및 메타데이터
"""

TOPICS = {
    1: {
        "name": "지역 평생교육 참여가 중년 여성의 삶의 만족도에 미치는 영향",
        "name_en": "Lifelong Education Participation and Life Satisfaction among Middle-aged Women",
        "target": "중년 여성 (40-60대)",
        "independent": {
            "name": "평생교육 참여",
            "operational": "최근 6개월간 평생교육 프로그램 참여 여부 및 빈도",
            "measurement_level": "명목/서열",
            "items": [
                "참여 여부 (예/아니오)",
                "월평균 참여 횟수 (0회/1-2회/3-4회/5회 이상)",
                "프로그램 평균 참여기간 (1개월미만/1-3개월/4-6개월/7개월 이상)"
            ]
        },
        "dependent": {
            "name": "삶의 만족도",
            "operational": "전반적 삶 만족도 및 주요 영역 만족도 5점 리커트 척도 평균",
            "measurement_level": "간격",
            "items": [
                "전반적으로 현재의 삶에 만족한다",
                "지난 한 달, 나의 성취감은 높은 편이다",
                "가족·친구와의 관계에 전반적으로 만족한다",
                "여가시간 활용에 만족한다",
                "앞으로의 생활에 대해 긍정적으로 느낀다"
            ]
        },
        "control_variables": [
            "연령대", "취업 상태", "건강 자기평가"
        ],
        "scale_type": "리커트 5점",
        "sample_items": list(range(1, 13)),  # 1-12
    },
    2: {
        "name": "지역 보건소 건강프로그램 이용 경험과 건강행동 변화",
        "name_en": "Health Program Participation and Health Behavior Change",
        "target": "지역 주민 (40세 이상)",
        "independent": {
            "name": "보건소 건강프로그램 이용",
            "operational": "최근 3개월간 보건소 프로그램 이용 여부 및 횟수",
            "measurement_level": "명목/서열",
            "items": [
                "이용 여부 (예/아니오)",
                "총 참여 횟수 (0/1-2/3-5/6회 이상)"
            ]
        },
        "dependent": {
            "name": "건강행동 변화",
            "operational": "건강 행동 실천 정도 5점 리커트 척도 평균",
            "measurement_level": "간격",
            "items": [
                "운동 시 회당 30분 이상 실천한다",
                "가공식품 섭취를 줄이려고 노력한다",
                "매일 야채/과일을 충분히 섭취한다",
                "평균 수면시간은 6-8시간이다",
                "수면의 질이 전반적으로 좋다",
                "건강을 위해 구체적 목표를 세우고 실천한다"
            ]
        },
        "control_variables": [
            "연령대", "만성질환 유무"
        ],
        "scale_type": "리커트 5점",
        "sample_items": list(range(1, 13)),  # 1-12 (변경 필요)
    },
    3: {
        "name": "커뮤니티 모임 참여와 사회적 지지감 및 고립감",
        "name_en": "Community Participation, Social Support, and Isolation",
        "target": "지역 주민 (40세 이상)",
        "independent": {
            "name": "커뮤니티 모임 참여",
            "operational": "최근 6개월간 정기 모임 참여 여부 및 빈도",
            "measurement_level": "명목/서열",
            "items": [
                "참여 여부 (예/아니오)",
                "월평균 참여 횟수 (0회/1-2회/3-4회/5회 이상)",
                "참여 기간 (1개월미만/1-3개월/4-6개월/7개월 이상)"
            ]
        },
        "dependent": {
            "name": "사회적 지지감 / 고립감",
            "operational": "사회적 지지 5점 리커트 척도 평균 (↑), 고립감 5점 리커트 척도 평균 (↓)",
            "measurement_level": "간격",
            "items_support": [
                "어려움이 있을 때 도움을 요청할 사람이 있다",
                "정서적으로 지지를 느낀다",
                "지역사회 내에 나의 소속감을 느낀다"
            ],
            "items_isolation": [
                "일상에서 외로움을 자주 느낀다 (역채점)",
                "대화를 나눌 사람이 부족하다고 느낀다 (역채점)"
            ]
        },
        "control_variables": [
            "1인가구 여부", "배우자 유무", "연령대"
        ],
        "scale_type": "리커트 5점",
        "sample_items": list(range(1, 13)),  # 1-12 (변경 필요)
    }
}

LIKERT_LABELS = {
    1: "매우 그렇지 않다",
    2: "그렇지 않다",
    3: "보통이다",
    4: "그렇다",
    5: "매우 그렇다"
}

COMMON_VARIABLES = {
    "age": {
        "name": "연령대",
        "type": "명목",
        "options": ["40대", "50대", "60대 이상"]
    },
    "gender": {
        "name": "성별",
        "type": "명목",
        "options": ["남성", "여성", "기타/비공개"]
    }
}
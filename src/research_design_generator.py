# -*- coding: utf-8 -*-
"""
연구설계서 자동 생성기
"""

from typing import Dict, List, Optional
from config import TOPICS
from survey_generator import SurveyGenerator

class ResearchDesignGenerator:
    """사회복지조사연구설계서 자동 생성 클래스"""

    def __init__(self, topic_id: int = None, topic_dict: Dict = None, researcher_info: Dict = None):
        """
        Args:
            topic_id: 주제 ID (1, 2, 3)
            topic_dict: 주제 정보 딕셔너리
            researcher_info: 연구자 정보 (학과, 학번, 이름 등)
        """
        self.topic_id = topic_id
        if topic_dict:
            self.topic = topic_dict
        else:
            self.topic = TOPICS[topic_id or 1]
        self.researcher_info = researcher_info or {}
        # SurveyGenerator 초기화 시에도 topic_dict 전달
        self.survey_gen = SurveyGenerator(topic_id=topic_id, topic_dict=self.topic)

    def generate_research_purpose(self) -> Dict[str, str]:
        """연구 목적 및 배경 생성"""
        topic_name = self.topic["name"]
        target = self.topic.get("target", "조사 대상자")
        indep = self.topic["independent"]["name"]
        dep = self.topic["dependent"]["name"]

        purpose_dict = {
            "necessity": f"""현대 사회에서 {target}의 웰빙(well-being)과 사회참여는 중요한 정책적 관심사입니다.
특히 {indep}이 {dep}에 미치는 영향을 이해하는 것은 효과적인 사회서비스 프로그램 개발과
지역사회 복지증진 전략 수립에 핵심적인 정보를 제공합니다.

최근 {target}을 대상으로 한 다양한 프로그램들이 시행되고 있으나,
이러한 프로그램들이 실제로 참여자의 삶의 질이나 건강행동에 어떤 영향을 미치는지
체계적으로 평가한 연구는 제한적입니다.

따라서 본 연구는 {indep}과 {dep} 사이의 관계를 실증적으로 분석하여,
사회복지 실천 및 정책 결정에 기여할 수 있는 기초자료를 제공하고자 합니다.""",
            "background": f"""선행연구에서는 {indep}이 {dep}에 긍정적인 영향을 미칠 가능성을 시사하고 있습니다.
다만, 기존 연구들은 주로 특정 지역이나 제한된 표집을 다루었으며,
{target}을 구체적으로 대상으로 한 연구는 상대적으로 부족한 실정입니다.

본 연구는 기존 연구의 공백을 메우고, 보다 일반화 가능한 결과를 도출함으로써
{f'{target}' if target else '지역사회'}의 복지정책 수립에 기여할 것으로 기대됩니다."""
        }

        return purpose_dict

    def generate_research_questions(self) -> List[str]:
        """연구 문제(RQ) 생성"""
        indep = self.topic["independent"]["name"]
        dep = self.topic["dependent"]["name"]

        rq = f"{indep}은(는) {dep}에 유의미한 영향을 미치는가?"

        # 주제별 추가 연구 문제
        if self.topic_id == 1:
            rq2 = f"{indep}의 참여 빈도에 따라 {dep} 수준에서 차이가 있는가?"
            return [rq, rq2]
        elif self.topic_id == 2:
            rq2 = f"{indep} 이용 경험이 구체적인 건강행동 실천에 어떤 영향을 미치는가?"
            return [rq, rq2]
        elif self.topic_id == 3:
            rq2 = f"{indep}이 사회적 지지감과 고립감에 상반된 영향을 미치는가?"
            return [rq, rq2]

        return [rq]

    def generate_hypotheses(self) -> List[Dict[str, str]]:
        """가설(H) 생성"""
        indep = self.topic["independent"]["name"]
        dep = self.topic["dependent"]["name"]
        rqs = self.generate_research_questions()
        rq = rqs[0]

        if self.topic_id in [1, 2]:
            hypothesis = {
                "H1": f"{indep}에 참여한 집단이 참여하지 않은 집단보다 {dep} 수준이 더 높을 것이다.",
                "direction": "정적",
                "related_rq": rq
            }
        elif self.topic_id == 3:
            hypothesis = {
                "H1": f"{indep}에 참여한 집단은 사회적 지지감이 높고 고립감이 낮을 것이다.",
                "direction": "지지감: 정적, 고립감: 부적",
                "related_rq": rq
            }
        else:
            # 자유 주제용 기본 가설
            hypothesis = {
                "H1": f"{indep}은(는) {dep}에 정적(+)인 영향을 미칠 것이다.",
                "direction": "정적",
                "related_rq": rq
            }

        hypotheses = [hypothesis]

        # 부가설
        if self.topic_id == 1:
            hypotheses.append({
                "H2": f"{indep}의 참여 빈도가 높을수록 {dep} 수준이 더 높을 것이다.",
                "direction": "정적"
            })
        elif self.topic_id == 2:
            hypotheses.append({
                "H2": f"{indep} 이용 횟수가 많을수록 건강행동 실천 정도가 높을 것이다.",
                "direction": "정적"
            })

        return hypotheses

    def generate_variable_definitions(self) -> Dict:
        """변수 정의 및 측정 계획 생성"""
        var_defs = {
            "독립변수": {
                "명칭": self.topic["independent"]["name"],
                "조작적정의": self.topic["independent"].get("operational", "해당 변수의 측정 도구 점수로 정의함"),
                "측정수준": self.topic["independent"].get("measurement_level", "등간척도"),
                "측정지표": {
                    "문항수": len(self.topic["independent"].get("items", [])),
                    "세부항목": self.topic["independent"].get("items", [])
                }
            },
            "종속변수": {
                "명칭": self.topic["dependent"]["name"],
                "조작적정의": self.topic["dependent"].get("operational", "해당 변수의 측정 도구 점수로 정의함"),
                "측정수준": self.topic["dependent"].get("measurement_level", "등간척도"),
                "측정지표": {
                    "문항수": len(self.topic["dependent"].get("items", [])) if "items" in self.topic["dependent"]
                            else len(self.topic["dependent"].get("items_support", [])) + len(self.topic["dependent"].get("items_isolation", [])),
                    "세부항목": self.topic["dependent"].get("items", []) if "items" in self.topic["dependent"]
                            else {"지지감": self.topic["dependent"].get("items_support", []),
                                  "고립감": self.topic["dependent"].get("items_isolation", [])}
                }
            },
            "통제변수": {
                "명칭": self.topic.get("control_variables", ["성별", "연령"]),
                "측정수준": "명목/서열",
                "측정지표": "응답자의 기본 정보를 수집하는 문항"
            }
        }
        return var_defs

    def generate_measurement_plan(self) -> Dict:
        """측정 및 척도 설계 생성"""
        full_survey = self.survey_gen.generate_full_survey()
        return {
            "척도유형": self.topic.get("scale_type", "리커트 척도"),
            "설문구성": {
                "공통문항": "인구통계학적 정보",
                "핵심문항": f"독립변수 측정 문항 {len(self.topic['independent'].get('items', []))}개",
                "종속변수문항": "종속변수 측정 리커트 문항",
                "통제변수문항": f"통제변수 측정 문항 {len(self.topic.get('control_variables', []))}개"
            },
            "총문항수": f"약 {full_survey['total_items']}개",
            "소요시간": "5분 내외",
            "신뢰도계획": "사전 파일럿 (N=10-15)을 통한 Cronbach's α ≥ 0.70 목표",
            "타당도계획": "내용타당도 (전문가/동료 검토), 안면타당도 (파일럿 피드백) 확보"
        }

    def generate_design_type(self) -> Dict:
        """조사설계(디자인) 유형 생성"""
        return {
            "설계유형": "설명적 조사 (Descriptive Survey)",
            "연구방법": "횡단적 설계 (Cross-sectional Design)",
            "데이터수집시점": "단일 시점",
            "인과성고려": {
                "시차": "횡단적 설계로 인과관계 추론에 제한 있음",
                "통제변수": f"{', '.join(self.topic.get('control_variables', []))} 통제",
                "제약사항": "자기보고식 설문으로 인한 공통방법편향 가능성",
                "보완방안": "파일럿 테스트를 통한 문항 정제, 무응답 최소화 방안 강구"
            }
        }

    def generate_sampling_plan(self) -> Dict:
        """표집 계획 생성"""
        target = self.topic.get("target", "조사 대상자")

        if self.topic_id == 1:
            population = f"{target}"
            frame = "지역 평생교육원 등록자 명부, 지역사회 공개 모집"
            method = "비확률 표집 (편의 표집 + 개인 네트워크 활용)"
            sample_size = "최소 80명"
            justification = "t-검정 기준 80% 검정력 확보를 위한 최소 표본 크기"
        elif self.topic_id in [2, 3]:
            population = f"{target}"
            frame = "관련 기관 명부, 지역사회 공개 모집"
            method = "비확률 표집 (편의 표집 + snowball sampling)"
            sample_size = "최소 100-120명"
            justification = "기술통계 및 집단 간 비교에 적합한 표본 크기"
        else:
            population = target
            frame = f"{target} 관련 기관 명부 및 온라인 커뮤니티"
            method = "비확률 표집 (편의 표집 및 임의 표집)"
            sample_size = "최소 100명"
            justification = "일반적인 양적 조사의 신뢰도 확보를 위한 최소 표본"

        return {
            "모집단": population,
            "표집틀(프레임)": frame,
            "표집방법": method,
            "목표표본수": sample_size,
            "근거": justification,
            "예상응답률": "60-70%",
            "확보전략": "소정의 보상 제공, 리마인더 발송, 접근성 높은 장소/시간대 활용"
        }

    def generate_data_collection_plan(self) -> Dict:
        """자료수집 방법과 도구 계획"""
        full_survey = self.survey_gen.generate_full_survey()
        survey_items = full_survey['all_items'][:6]
        sample_q = "\n".join([f"- {q['text']}" for q in survey_items])
        
        return {
            "수집방법": "자기보고식 온라인/오프라인 설문조사",
            "설문도구": "자동 생성된 구조화된 설문지",
            "설문 문항 예시": sample_q,
            "조사기간": "파일럿: 1주, 본조사: 2-3주",
            "절차": [
                "1. 파일럿 조사 (N=10-15): 문항 이해도 점검, 소요시간 측정",
                "2. 문항 수정/보완 (필요시)",
                "3. 본조사 실시",
                "4. 데이터 정리 및 전처리"
            ],
            "윤리적고려": {
                "동의과정": "설문 시작 전 연구 목적, 자발성, 철회 가능성 고지",
                "개인정보": "익명 처리, IP 수집하지 않음, 데이터 암호화 저장",
                "취약집단": "민감 문항 최소화, 참여자 부담 고려"
            }
        }

    def generate_error_bias_management(self) -> Dict:
        """오차와 편향 관리 계획"""
        return {
            "측정오차관리": [
                "문항 이해도 확인을 위한 파일럿 테스트 수행",
                "역문항 최소화 또는 역채점을 통한 일관성 확보",
                "명확하고 간결한 문항 표현 사용"
            ],
            "표본오차관리": [
                "표본 크기 확대 (가능한 범위 내)",
                "층화표집 고려 (연령대, 참여여부 등)"
            ],
            "비응답편향관리": [
                "설문 시작 전 참여 중요성 강조",
                "소정의 인센티브 제공 (기프트카드 등)",
                "리마인더 전송 (온라인), 2-3회",
            ],
            "사회적바람직성편향관리": [
                "익명성 강조",
                "민감 문항을 뒤로 배치",
                "긍정적 표현 균형 유지"
            ]
        }

    def generate_analysis_plan(self) -> Dict:
        """자료 분석 계획 생성"""
        indep = self.topic["independent"]["name"]
        dep = self.topic["dependent"]["name"]

        if self.topic_id in [1, 2]:
            analysis = {
                "기술통계": "빈도, 백분율, 평균, 표준편차",
                "가설검증": f"독립표본 t-검정 (참여 vs 비참여)\n단순회귀분석 (참여 빈도와 결과변수 관계)",
                "추가분석": "공분산분석 (ANCOVA): 통제변수 포함 모델",
                "시각화": "막대 그래프, 상자 그림, 산점도"
            }
        else:
            analysis = {
                "기술통계": "빈도, 백분율, 평균, 표준편차",
                "가설검증": f"상관분석 및 다중회귀분석",
                "추가분석": "인구통계학적 특성에 따른 차이 분석",
                "시각화": "막대 그래프, 히스토그램, 산점도"
            }

        analysis["소프트웨어"] = "SPSS / R / Python (선택)"
        return analysis

    def generate_schedule_resources(self) -> Dict:
        """일정 및 자원 계획 생성"""
        return {
            "주간일정": {
                "1주": "파일럿 조사 설계 및 시행",
                "2주": "파일럿 데이터 분석 및 문항 보완",
                "3-4주": "본조사 실시",
                "5주": "데이터 정리 및 전처리",
                "6주": "자료 분석 및 해석",
                "7주": "보고서 작성 및 검토"
            },
            "필요자원": {
                "설문도구": "온라인 설문 플랫폼 (Google Forms, SurveyMonkey 등) / 종이 설문",
                "조사인력": "연구자 1인 + 보조 인력 (필요시)",
                "분석소프트웨어": "SPSS / R / Python",
                "기타": "소정의 보상 (기프트카드, 커피쿠폰 등, 예산 범위 내)"
            }
        }

    def generate_limitations_effects(self) -> Dict:
        """한계와 기대효과 생성"""
        return {
            "한계": [
                "횡단적 설계로 인해 인과관계 추론에 제한",
                "자기보고식 설문으로 사회적 바람직성 편향 가능성",
                "비확률 표집으로 일반화 가능성 제한",
                "특정 지역 중심의 결과로 지역 외 적용 시 주의 필요"
            ],
            "기대효과": [
                f"{self.topic['name']}의 실증적 근거 제공",
                "지역사회 복지 프로그램 개선 기초자료 활용 가능",
                f"{self.topic.get('target', '조사대상')}의 욕구 파악에 기여",
                "사회복지 실천 현장에 정책/프로그램 개발 참고자료 제공"
            ]
        }

    def generate_full_design(self) -> Dict:
        """전체 연구설계서 생성"""
        survey_data = self.survey_gen.generate_full_survey()

        design = {
            "연구주제": self.topic["name"],
            "연구자정보": self.researcher_info,
            "1_연구주제": {
                "한줄": self.topic["name"]
            },
            "2_연구목적과배경": self.generate_research_purpose(),
            "3_연구문제": self.generate_research_questions(),
            "4_가설": self.generate_hypotheses(),
            "5_변수정의": self.generate_variable_definitions(),
            "6_측정척도설계": self.generate_measurement_plan(),
            "7_조사설계": self.generate_design_type(),
            "8_표집계획": self.generate_sampling_plan(),
            "9_자료수집방법": self.generate_data_collection_plan(),
            "10_오차편향관리": self.generate_error_bias_management(),
            "11_윤리적고려": self.generate_data_collection_plan()["윤리적고려"],
            "12_데이터분석": self.generate_analysis_plan(),
            "13_일정및자원": self.generate_schedule_resources(),
            "14_한계기대효과": self.generate_limitations_effects(),
            "부록_설문지": survey_data
        }

        return design

    def export_to_hwp_format(self) -> str:
        """HWP 포맷용 텍스트 생성"""
        design = self.generate_full_design()

        output = f"""사회복지연구 설계서
제출자 정보: {self.researcher_info.get('department', '')} / {self.researcher_info.get('student_id', '')} / {self.researcher_info.get('name', '')}

1. 연구 주제: {design['1_연구주제']['한줄']}

2. 연구 목적과 배경
가. 필요성: {design['2_연구목적과배경']['necessity']}
나. 배경: {design['2_연구목적과배경']['background']}

3. 연구문제
{chr(10).join(f"RQ{i+1}: {q}" for i, q in enumerate(design['3_연구문제']))}

4. 가설 설정
{chr(10).join(f"H{i+1}: {h['H'+str(i+1)] if 'H'+str(i+1) in h else h.get('H1', '')}" for i, h in enumerate(design['4_가설']))}

5. 변수 정의
가. 독립변수: {design['5_변수정의']['독립변수']['명칭']} (정의: {design['5_변수정의']['독립변수']['조작적정의']})
나. 종속변수: {design['5_변수정의']['종속변수']['명칭']} (정의: {design['5_변수정의']['종속변수']['조작적정의']})
다. 통제변수: {', '.join(design['5_변수정의']['통제변수']['명칭'])}

6. 표집 계획
- 모집단: {design['8_표집계획']['모집단']}
- 방법: {design['8_표집계획']['표집방법']}
- 표본수: {design['8_표집계획']['목표표본수']}

7. 자료수집 및 분석
- 방법: {design['9_자료수집방법']['수집방법']}
- 분석계획: {design['12_데이터분석']['가설검증']}
"""
        return output
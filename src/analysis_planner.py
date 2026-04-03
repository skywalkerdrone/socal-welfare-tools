# -*- coding: utf-8 -*-
"""
통계 분석 계획 자동 생성기
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from config import TOPICS

class AnalysisPlanner:
    """통계 분석 계획 생성 및 기초 분석 지원 클래스"""

    def __init__(self, topic_id: int):
        self.topic_id = topic_id

    def generate_analysis_plan(self) -> Dict:
        """분석 계획서 생성"""
        if self.topic_id in [1, 2]:
            plan = {
                "분석단계": [
                    {
                        "단계": 1,
                        "이름": "전처리 및 기술통계",
                        "내용": [
                            "결측치 확인 및 처리 (평균 대체 또는 완전사례분석)",
                            "변수 정규성 검정 (Shapiro-Wilk, Kolmogorov-Smirnov)",
                            "리커트 척도 역채점 적용 (필요시)",
                            "기술통계: 빈도, 백분율, 평균, 표준편차, 최소-최대값"
                        ]
                    },
                    {
                        "단계": 2,
                        "이름": "신뢰도 분석",
                        "내용": [
                            "종속변수 척도에 대한 Cronbach's α 계산",
                            "α ≥ 0.70 기준 충족 시 척도 점수 합산/평균 활용",
                            "α < 0.70 시 개별 문항 분석 및 제고려"
                        ]
                    },
                    {
                        "단계": 3,
                        "이름": "가설검증 - 집단 간 차이",
                        "내용": [
                            "독립표본 t-검정 (참여 vs 비참여)\n - 등분산 가정 검정 (Levene's test)\n - 등분산/이분산 선택에 따른 t-검정",
                            "조건부: 참여 빈도에 따른 일원분산분석 (ANOVA)\n - 사후검정 (Tukey HSD)",
                            "효과크기 계산 (Cohen's d: 0.2=소, 0.5=중, 0.8=대)"
                        ]
                    },
                    {
                        "단계": 4,
                        "이름": "가설검증 - 관계 분석",
                        "내용": [
                            "Pearson 상관분석 (간격/비율 변수 간)",
                            "단순회귀분석 (연속형 독립변수 → 종속변수)",
                            "다중회귀분석 (통제변수 포함 모델)\n - 회귀모형 적합도 (R², 수정 R²)\n - 회귀계수의 유의성 (t-test, p-value)\n - 다중공선성 검정 (VIF < 10)"
                        ]
                    },
                    {
                        "단계": 5,
                        "이름": "부가 분석",
                        "내용": [
                            "통제변수(성별, 연령)에 따른 하위집단 분석",
                            "성향점수매칭 (PSM) 고려 (선택)",
                            "매개변수/조절변수 분석 (이론적 근거 있을 시)"
                        ]
                    }
                ],
                "결과보고형식": {
                    "t검정": "t(df) = 값, p = 값, d = 값",
                    "상관": "r = 값, p = 값",
                    "회귀": "β = 값, SE = 값, p = 값, R² = 값",
                    "ANOVA": "F(df1, df2) = 값, p = 값, η² = 값"
                }
            }
        else:  # Topic 3 (지지/고립)
            plan = {
                "분석단계": [
                    {
                        "단계": 1,
                        "이름": "전처리 및 기술통계",
                        "내용": [
                            "결측치 확인 및 처리",
                            "리커트 척도 역채점 적용 (고립감 문항)",
                            "지지감 척도, 고립감 척도 각각 평균 계산",
                            "기술통계: 평균, 표준편차, 왜도, 첨도"
                        ]
                    },
                    {
                        "단계": 2,
                        "이름": "신뢰도 분석",
                        "내용": [
                            "지지감 척도 Cronbach's α",
                            "고립감 척도 Cronbach's α",
                            "각 척도별 α ≥ 0.70 확인"
                        ]
                    },
                    {
                        "단계": 3,
                        "이름": "집단 간 차이 분석",
                        "내용": [
                            "독립표본 t-검정 (참여 vs 비참여)\n - 지지감 점수 비교\n - 고립감 점수 비교",
                            "효과크기 (Cohen's d) 보고"
                        ]
                    },
                    {
                        "단계": 4,
                        "이름": "다중회귀분석",
                        "내용": [
                            "모델 1 (지지감): 참여여부 + 통제변수 → 지지감",
                            "모델 2 (고립감): 참여여부 + 통제변수 → 고립감",
                            "회귀계수, 유의성, R² 검토",
                            "다중공선성 (VIF) 확인"
                        ]
                    },
                    {
                        "단계": 5,
                        "이름": "상관 및 부가 분석",
                        "내용": [
                            "주요 변수 간 Pearson 상관Matrix",
                            "참여 빈도와 결과변수 관계 분석 (부분상관)",
                            "매개효과 분석 (Bootstrap, 선택사항)"
                        ]
                    }
                ],
                "결과보고형식": {
                    "t검정": "t(df) = 값, p = 값, d = 값",
                    "상관": "r = 값, p = 값",
                    "회귀": "β = 값, SE = 값, p = 값, R² = 값"
                }
            }

        return plan

    def generate_sample_size_calculation(self, effect_size: str = "medium") -> Dict:
        """표본 크기 계산 가이드"""
        from scipy import stats

        effect_sizes = {
            "small": 0.2,
            "medium": 0.5,
            "large": 0.8
        }

        es = effect_sizes.get(effect_size, 0.5)

        # Cohen's d 기준 표본 크기 (alpha=0.05, power=0.80)
        # 간단한 근사값 사용 (정확한 계산은 power analysis 필요)
        if self.topic_id in [1, 2]:
            if es >= 0.8:
                n_per_group = 26
            elif es >= 0.5:
                n_per_group = 64
            else:
                n_per_group = 393
        else:
            # 다중회귀의 경우 인과관계 수 고려 (N ≥ 15 * predictors)
            n_total = 15 * (2 + len(TOPICS[self.topic_id]["control_variables"]))  # 최소한
            return {
                "검정력분석": f"Cohen's d={es}, α=0.05, 1-β=0.80 기준",
                "t검정표본": f"각 집단별 {n_per_group}명 (총 {2*n_per_group}명)",
                "회귀분석표본": f"최소 {n_total}명 (예측변수 1개당 15명 규칙)",
                "권장표본": f"100-150명 (다양한 분석 대비)"
            }

    def generate_code_templates(self) -> Dict[str, str]:
        """분석 코드 템플릿 생성 (Python/R)"""
        python_template = """import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

# 데이터 로드
df = pd.read_excel('survey_data.xlsx')

# 1. 리커트 척도 역채점 (필요시)
# reverse_code_items = ['isolation_1', 'isolation_2']
# for item in reverse_code_items:
#     df[f'{item}_rev'] = 6 - df[item]

# 2. 척도 점수 계산
# life_satisfaction_cols = [f'life_satisfaction_{i}' for i in range(1, 6)]
# df['life_sat_score'] = df[life_satisfaction_cols].mean(axis=1)

# 3. 기술통계
print(df[['participant', 'life_sat_score']].groupby('participant').describe())

# 4. 신뢰도 분석 (Cronbach's Alpha)
def cronbach_alpha(items):
    items = np.array(items)
    item_vars = items.var(axis=1, ddof=1)
    total_var = items.sum(axis=0).var(ddof=1)
    n_items = items.shape[0]
    alpha = n_items / (n_items - 1) * (1 - (item_vars.sum() / total_var))
    return alpha

# alpha = cronbach_alpha(df[life_satisfaction_cols].values)
# print(f"Cronbach's α = {alpha:.3f}")

# 5. 등분산 검정
# group1 = df[df['participant'] == '예']['life_sat_score']
# group2 = df[df['participant'] == '아니오']['life_sat_score']
# levene_stat, levene_p = stats.levene(group1, group2)
# print(f"Levene's test: F={levene_stat:.3f}, p={levene_p:.3f}")

# 6. 독립표본 t-검정
# equal_var = levene_p > 0.05
# t_stat, t_p = stats.ttest_ind(group1, group2, equal_var=equal_var)
# print(f"t-test: t={t_stat:.3f}, p={t_p:.3f}")

# 7. 효과크기 (Cohen's d)
# pooled_std = np.sqrt(((len(group1)-1)*group1.var() + (len(group2)-1)*group2.var()) / (len(group1)+len(group2)-2))
# cohen_d = (group1.mean() - group2.mean()) / pooled_std
# print(f"Cohen's d = {cohen_d:.3f}")

# 8. 상관분석
# corr_matrix = df[[participants', 'life_sat_score', 'control_var1', 'control_var2']].corr()
# print(corr_matrix)

# 9. 회귀분석
# X = df[['participant_binary', 'control_var1', 'control_var2']]
# X = pd.get_dummies(X, columns=['participant_binary'], drop_first=True)
# X = sm.add_constant(X)
# y = df['life_sat_score']
# model = sm.OLS(y, X).fit()
# print(model.summary())

# 10. 시각화
# import matplotlib.pyplot as plt
# import seaborn as sns
# sns.boxplot(x='participant', y='life_sat_score', data=df)
# plt.title('참여 여부에 따른 삶의 만족도')
# plt.show()
"""

        r_template = """# 패키지 로드
library(tidyverse)
library(psych)
library(effsize)

# 데이터 로드
df <- read_excel('survey_data.xlsx')

# 1. 리커트 척도 점수 계산
life_sat_items <- df %>% select(starts_with('life_satisfaction_'))
df$life_sat_score <- rowMeans(life_sat_items, na.rm = TRUE)

# 2. 기술통계
df %>% group_by(participant) %>% summarise(
  n = n(),
  mean = mean(life_sat_score, na.rm = TRUE),
  sd = sd(life_sat_score, na.rm = TRUE)
)

# 3. Cronbach's Alpha
alpha(life_sat_items)

# 4. 등분산 검정
library(car)
leveneTest(life_sat_score ~ participant, data = df)

# 5. 독립표본 t-검정
t_test_result <- t.test(life_sat_score ~ participant, data = df, var.equal = TRUE)
print(t_test_result)

# 6. 효과크기 (Cohen's d)
cohen_d(life_sat_score ~ participant, data = df)

# 7. 상관분석
cor_matrix <- df %>% select(participant, life_sat_score, control_var1, control_var2) %>% cor(use = 'complete.obs')
print(cor_matrix)

# 8. 회귀분석
model <- lm(life_sat_score ~ participant_binary + control_var1 + control_var2, data = df)
summary(model)

# 9. 시각화
ggplot(df, aes(x = participant, y = life_sat_score, fill = participant)) +
  geom_boxplot() +
  theme_minimal() +
  labs(title = '참여 여부에 따른 삶의 만족도')
"""

        return {
            "python": python_template,
            "r": r_template
        }

    def export_analysis_plan(self, format: str = "markdown") -> str:
        """분석 계획서 내보내기"""
        plan = self.generate_analysis_plan()

        if format == "markdown":
            output = "## 통계 분석 계획\n\n"
            for step in plan["분석단계"]:
                output += f"### {step['단계']}. {step['이름']}\n"
                for item in step["내용"]:
                    output += f"- {item}\n"
                output += "\n"

            output += "### 결과 보고 형식\n"
            for key, val in plan["결과보고형식"].items():
                output += f"- **{key}**: {val}\n"

        else:  # 한글
            output = "## 통계 분석 계획\n\n"
            for step in plan["분석단계"]:
                output += f"### {step['단계']}. {step['이름']}\n"
                for item in step["내용"]:
                    output += f"- {item}\n"
                output += "\n"

            output += "### 결과 보고 형식\n"
            for key, val in plan["결과보고형식"].items():
                output += f"- **{key}**: {val}\n"

        return output
import os
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Optional

class SocialWelfareDB:
    def __init__(self):
        # Streamlit 앱 내에서 호출되므로 st.connection 사용 가능
        try:
            # .streamlit/secrets.toml의 [connections.gsheets] 설정을 자동으로 읽어옵니다.
            self.conn = st.connection("gsheets", type=GSheetsConnection)
        except Exception as e:
            self.conn = None
            st.error(f"⚠️ Google Sheets 연결에 실패했습니다: {e}")

    def _get_all_data(self) -> pd.DataFrame:
        """시트 전체 데이터를 DataFrame으로 읽어오기"""
        if not self.conn:
            return pd.DataFrame()
        try:
            sheet_url = st.secrets["connections"]["gsheets"].get("spreadsheet")
            df = self.conn.read(spreadsheet=sheet_url, ttl=0)
            # 컬럼명 공백 제거 및 대소문자 통일 (매칭 강인성 확보)
            if not df.empty:
                df.columns = [str(c).strip().lower() for c in df.columns]
            return df
        except Exception as e:
            try:
                sheet_url = st.secrets["connections"]["gsheets"].get("spreadsheet")
                df = self.conn.read(url=sheet_url, ttl=0)
                if not df.empty:
                    df.columns = [str(c).strip().lower() for c in df.columns]
                return df
            except:
                print(f"데이터 읽기 오류: {e}")
                return pd.DataFrame()

    def save_generation(self, topic: str, researcher_info: Dict, design: Dict, survey: Dict) -> Optional[int]:
        """생성 결과를 구글 시트에 추가"""
        if not self.conn:
            return None
            
        gen_id = int(datetime.now().timestamp())
        new_row = {
            "id": gen_id,
            "topic": topic,
            "researcher_name": researcher_info.get("name", ""),
            "researcher_id": researcher_info.get("student_id", ""),
            "password": str(researcher_info.get("password", "")), # 명시적 문자열 저장
            "design_json": json.dumps(design, ensure_ascii=False),
            "survey_json": json.dumps(survey, ensure_ascii=False),
            "created_at": datetime.now().strftime("%Y-%m-%d")
            # "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            df = self._get_all_data()
            # 저장 시에는 원래 컬럼명 형식을 따르되, 데이터가 없으면 헤더 생성
            if df.empty:
                df = pd.DataFrame([new_row])
            else:
                # 합칠 때 컬럼명을 맞춰줌
                new_df = pd.DataFrame([new_row])
                new_df.columns = [c.lower() for c in new_df.columns]
                df = pd.concat([df, new_df], ignore_index=True)
            
            sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
            self.conn.update(spreadsheet=sheet_url, data=df)
            return gen_id
        except Exception as e:
            st.error(f"구글 시트 저장 중 오류가 발생했습니다: {e}")
            return None

    def get_all_history(self) -> List[Dict]:
        """모든 생성 이력 조회"""
        df = self._get_all_data()
        if df.empty:
            return []
        
        # 'created_at' 컬럼 확인 (소문자화 됨)
        if "created_at" in df.columns:
            df = df.sort_values(by="created_at", ascending=False)
            
        # 필요한 필드 매칭 (id, topic, researcher_name, created_at)
        return df.to_dict("records")

    def get_generation_detail(self, generation_id: int) -> Optional[Dict]:
        """상세 데이터 조회"""
        df = self._get_all_data()
        if df.empty:
            return None
            
        # ID 매칭 시 숫자형과 문자형 모두 대응
        try:
            target_id = float(generation_id)
            df['id_numeric'] = pd.to_numeric(df['id'], errors='coerce')
            row = df[df['id_numeric'] == target_id]
        except:
            row = df[df["id"].astype(str) == str(generation_id)]
            
        if not row.empty:
            res = row.iloc[0].to_dict()
            # JSON 필드 복원 (디버그: 원본 보존을 위해 design_json/survey_json 사용)
            for field in ["design", "survey"]:
                json_key = f"{field}_json"
                val = res.get(json_key)
                try:
                    if pd.isna(val) or val == "":
                        res[field] = {}
                    elif isinstance(val, (dict, list)):
                        res[field] = val
                    else:
                        res[field] = json.loads(str(val))
                except Exception as e:
                    res[field] = {}
            return res
        return None

    def delete_generation(self, generation_id: int):
        """이력 삭제"""
        if not self.conn:
            return
            
        try:
            df = self._get_all_data()
            if not df.empty:
                # 삭제 시에도 숫자/문자열 모두 대응
                try:
                    target_id = float(generation_id)
                    df['id_numeric'] = pd.to_numeric(df['id'], errors='coerce')
                    df = df[df['id_numeric'] != target_id]
                except:
                    df = df[df["id"].astype(str) != str(generation_id)]
                
                # 임시 컬럼 제거 후 업데이트
                if 'id_numeric' in df.columns:
                    df = df.drop(columns=['id_numeric'])
                    
                sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
                self.conn.update(spreadsheet=sheet_url, data=df)
        except Exception as e:
            st.error(f"구글 시트 삭제 중 오류 발생: {e}")

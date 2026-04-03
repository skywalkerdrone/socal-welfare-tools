# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv

# 프로젝트 루트 경로 추가
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

load_dotenv()

from src.database import SocialWelfareDB

def test_db_password():
    db = SocialWelfareDB("test_welfare.db")
    
    topic = "테스트 연구 주제: 비밀번호 기능 검증"
    researcher_info = {
        "name": "홍길동",
        "student_id": "20240001",
        "password": "4321"
    }
    design = {"name": "Test Design"}
    survey = {"name": "Test Survey"}
    
    # 저장 테스트
    gen_id = db.save_generation(topic, researcher_info, design, survey)
    print(f"Saved generation with ID: {gen_id}")
    
    # 조회 테스트
    detail = db.get_generation_detail(gen_id)
    if detail:
        print(f"Retrieved password: {detail.get('password')}")
        if detail.get('password') == "4321":
            print("Password verification SUCCESS!")
        else:
            print("Password verification FAILED!")
    else:
        print("Detail retrieval FAILED!")
        
    # 정리
    os.remove("test_welfare.db")

if __name__ == "__main__":
    test_db_password()

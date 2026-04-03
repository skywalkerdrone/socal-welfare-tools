# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv

# src 디렉토리를 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ai_engine import AIEngine

def test_connectivity():
    print("OpenRouter 연결 테스트 시작...")
    try:
        engine = AIEngine()
        print(f"사용 모델: {engine.model}")
        print(f"Base URL: {engine.base_url}")
        
        test_topic = "지역사회 노인 외로움 해소를 위한 프로그램"
        print(f"테스트 주제: {test_topic}")
        
        result = engine.analyze_topic(test_topic)
        
        print("\n[분석 결과]")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n연결 테스트 성공!")
        
    except Exception as e:
        import traceback
        print("\n\n=== 상세 오류 정보 ===")
        print(f"오류 유형: {type(e).__name__}")
        print(f"오류 메시지: {e}")
        if hasattr(e, 'response'):
            try:
                print(f"응답 본문: {e.response.text}")
            except:
                pass
        traceback.print_exc()
        print("======================\n")
        sys.exit(1)

if __name__ == "__main__":
    test_connectivity()

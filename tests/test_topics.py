# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv

# 프로젝트 루트 경로 추가
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

load_dotenv()

from src.ai_engine import AIEngine

def test_generate_single_topic():
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("API Key not found in .env")
        return

    engine = AIEngine(api_key=api_key)
    
    print("\n--- Testing Single Topic Generation (Random Category) ---")
    for i in range(3):
        try:
            topic = engine.generate_single_topic()
            print(f"Test {i+1}: {topic}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_generate_single_topic()

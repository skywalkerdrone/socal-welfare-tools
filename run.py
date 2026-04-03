#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
사회복지조사연구설계서 자동 생성기 - 실행 스크립트
"""

import subprocess
import sys
import os

def main():
    """Streamlit 앱 실행"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_app = os.path.join(script_dir, "src", "main.py")

    if not os.path.exists(main_app):
        print(f"Error: {main_app} not found!")
        return

    print("=" * 60)
    print("사회복지조사연구설계서 자동 생성기를 시작합니다...")
    print("=" * 60)
    print("\n브라우저가 자동으로 열리지 않으면 다음 주소로 접속하세요:")
    print("http://localhost:8501\n")
    print("종료하려면 Ctrl+C를 누르세요.")
    print("=" * 60)

    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", main_app], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n오류 발생: {e}")
        print("\n다음 명령어를 수동으로 실행해보세요:")
        print(f"  cd {os.path.dirname(main_app)}")
        print(f"  {sys.executable} -m streamlit run main.py")
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")

if __name__ == "__main__":
    main()
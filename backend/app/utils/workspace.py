import os
import socket
import secrets
from pathlib import Path
from ..config import settings

def create_workspace_directory(user_id: str) -> str:
    """사용자 워크스페이스 디렉토리 생성 (UUID 기반)"""
    workspace_path = settings.get_workspace_path(user_id)
    Path(workspace_path).mkdir(parents=True, exist_ok=True)
    
    # 기본 폴더 생성
    notebooks_path = os.path.join(workspace_path, "notebooks")
    data_path = os.path.join(workspace_path, "data")
    outputs_path = os.path.join(workspace_path, "outputs")
    
    Path(notebooks_path).mkdir(exist_ok=True)
    Path(data_path).mkdir(exist_ok=True)
    Path(outputs_path).mkdir(exist_ok=True)
    
    # 시작 가이드 노트북 생성
    create_welcome_notebook(notebooks_path)
    
    return workspace_path

def create_welcome_notebook(notebooks_path: str):
    """환영 노트북 생성"""
    welcome_content = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Welcome to Your Jupyter Data Platform!\n",
                    "\n",
                    "이곳은 여러분의 개인 워크스페이스입니다. 다음과 같은 기능들을 활용하실 수 있습니다:\n",
                    "\n",
                    "## 주요 기능\n",
                    "- 데이터 분석 및 시각화\n",
                    "- 머신러닝 모델 개발\n",
                    "- 단계별 결과 저장 및 재사용\n",
                    "\n",
                    "## 폴더 구조\n",
                    "- `notebooks/`: 노트북 파일 저장\n",
                    "- `data/`: 데이터 파일 저장\n",
                    "- `outputs/`: 결과 파일 저장"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 기본 라이브러리 import\n",
                    "import pandas as pd\n",
                    "import numpy as np\n",
                    "import matplotlib.pyplot as plt\n",
                    "import seaborn as sns\n",
                    "\n",
                    "print('환영합니다! 모든 라이브러리가 정상적으로 로드되었습니다.')"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    import json
    welcome_path = os.path.join(notebooks_path, "Welcome.ipynb")
    with open(welcome_path, 'w', encoding='utf-8') as f:
        json.dump(welcome_content, f, ensure_ascii=False, indent=2)

def find_available_port() -> int:
    """사용 가능한 포트 찾기"""
    for port in range(settings.jupyter_port_start, settings.jupyter_port_end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    raise Exception("사용 가능한 포트를 찾을 수 없습니다.")

def generate_jupyter_token() -> str:
    """Jupyter 토큰 생성"""
    return secrets.token_urlsafe(32) 
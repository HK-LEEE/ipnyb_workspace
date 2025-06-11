# Jupyter Data Platform

## 개요

Windows 환경에서 Jupyter Lab/Notebook 기능을 웹 기반으로 제공하는 데이터 분석 플랫폼입니다. 사용자별 독립적인 Python 개발 및 데이터 분석 환경을 구축하며, 파일 업로드/다운로드, 단계별 실행 결과 저장 및 재사용 기능을 제공합니다.

## 주요 기능

### ✅ 1단계 완료 (MVP)
- **사용자 인증**: JWT 기반 로그인/회원가입 시스템
- **워크스페이스 관리**: 사용자별 독립적인 작업 공간 생성/삭제
- **Jupyter Lab 통합**: 워크스페이스별 Jupyter Lab 인스턴스 시작/중지
- **파일 관리**: 기본적인 파일 업로드/다운로드 기능

### ✅ 2단계 완료 (기능 확장)
- **고급 파일 관리**: 폴더 생성/삭제, 파일 브라우저 UI
- **워크스페이스 상태 관리**: Jupyter 실행 상태 표시 및 관리
- **사용자 대시보드**: 직관적인 워크스페이스 관리 인터페이스
- **파일 시스템 탐색**: 폴더 구조 탐색 및 파일 관리

### 🚧 3단계 예정 (고급 기능)
- 리소스 사용량 모니터링
- 협업 기능
- 고급 보안 설정
- 배포 최적화

## 시스템 아키텍처

```
Frontend (React + TypeScript)
    ↓ HTTP/REST API (포트 3000/5173)
Backend (FastAPI + Python)
    ↓ Process Management (포트 8000)
Jupyter Lab Instances
    ↓ File System (포트 8888-9000)
User Workspaces (UUID-based)
    ↓ Database
MySQL/SQLite
```

## 기술 스택

### 프론트엔드
- **React 18** + TypeScript
- **Tailwind CSS** (스타일링)
- **React Router** (라우팅)
- **Vite** (빌드 도구)

### 백엔드
- **FastAPI** (웹 프레임워크)
- **SQLAlchemy** (ORM)
- **MySQL/SQLite** (데이터베이스)
- **JWT** (인증)
- **Jupyter Lab** (노트북 환경)

## 설치 및 실행

### 1. 환경 요구사항
- Python 3.9+
- Node.js 16+
- MySQL (또는 SQLite)

### 2. 백엔드 설정

```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
copy .env.example .env
# .env 파일을 편집하여 데이터베이스 설정 등을 구성

# 데이터베이스 초기화
python init_db.py

# 워크스페이스 테이블 마이그레이션
python migrate_workspace.py

# 워크스페이스 폴더 구조 마이그레이션 (기존 시스템 업그레이드 시)
python migrate_workspace_structure.py

# 서버 시작
python main.py
```

### 3. 프론트엔드 설정

```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성 설치
npm install

# 개발 서버 시작
npm run dev
```

### 4. 접속
- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## 사용 방법

### 1. 회원가입 및 로그인
1. 브라우저에서 http://localhost:3000 접속
2. "회원가입" 탭에서 계정 생성
3. 로그인하여 대시보드 접속

### 2. 워크스페이스 생성
1. 대시보드에서 "새 워크스페이스" 버튼 클릭
2. 워크스페이스 이름과 설명 입력
3. 생성 완료 후 워크스페이스 목록에서 확인

### 3. Jupyter Lab 사용
1. 워크스페이스에서 "시작" 버튼 클릭
2. Jupyter Lab이 새 탭에서 열림
3. 노트북 작성 및 데이터 분석 수행
4. 작업 완료 후 "중지" 버튼으로 인스턴스 종료

### 4. 파일 관리
1. 워크스페이스에서 "파일 관리" 버튼 클릭
2. 파일 업로드: "파일 업로드" 버튼으로 로컬 파일 업로드
3. 폴더 생성: "새 폴더" 버튼으로 디렉토리 생성
4. 파일 다운로드: 파일 목록에서 "다운로드" 버튼 클릭

### 5. 단계별 결과 저장 및 재사용
1. 첫 번째 노트북에서 데이터 처리 후 CSV 파일로 저장:
   ```python
   import pandas as pd
   # 데이터 처리
   df.to_csv('processed_data.csv', index=False)
   ```

2. 두 번째 노트북에서 저장된 데이터 불러오기:
   ```python
   import pandas as pd
   df = pd.read_csv('processed_data.csv')
   # 추가 분석 수행
   ```

## 디렉토리 구조

```
jupyter-platform/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── models/         # 데이터베이스 모델
│   │   ├── routers/        # API 라우터
│   │   ├── services/       # 비즈니스 로직
│   │   ├── schemas/        # Pydantic 스키마
│   │   └── utils/          # 유틸리티 함수
│   ├── main.py            # 메인 애플리케이션
│   └── requirements.txt   # Python 의존성
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/    # React 컴포넌트
│   │   ├── pages/         # 페이지 컴포넌트
│   │   └── services/      # API 서비스
│   └── package.json       # Node.js 의존성
├── data/                  # 사용자 워크스페이스 데이터
│   └── users/            # UUID/워크스페이스 ID 기반 폴더
│       └── {user_id}/    # 사용자별 폴더
│           └── {workspace_id}/  # 워크스페이스별 폴더
└── README.md
```

## 워크스페이스 구조 개선

### 📁 새로운 폴더 구조
기존의 `data/users/{user_id}` 구조에서 `data/users/{user_id}/{workspace_id}` 구조로 변경되었습니다.

**변경 전:**
```
data/
└── users/
    ├── user-uuid-1/        # 모든 워크스페이스가 혼재
    │   ├── notebooks/
    │   ├── data/
    │   └── outputs/
    └── user-uuid-2/
        ├── notebooks/
        ├── data/
        └── outputs/
```

**변경 후:**
```
data/
└── users/
    ├── user-uuid-1/
    │   ├── 1/              # 워크스페이스 ID별 분리
    │   │   ├── notebooks/
    │   │   ├── data/
    │   │   └── outputs/
    │   └── 2/
    │       ├── notebooks/
    │       ├── data/
    │       └── outputs/
    └── user-uuid-2/
        └── 1/
            ├── notebooks/
            ├── data/
            └── outputs/
```

### 🔄 마이그레이션 방법
기존 시스템을 업그레이드하는 경우:

1. **Windows 배치 파일 사용:**
   ```cmd
   migrate_workspace_structure.bat
   ```

2. **Python 스크립트 직접 실행:**
   ```bash
   cd backend
   python migrate_workspace_structure.py
   ```

### ✅ 개선 효과
- **워크스페이스 격리**: 각 워크스페이스가 독립적인 폴더를 가짐
- **데이터 정리**: 프로젝트별 데이터 관리가 명확해짐
- **확장성**: 사용자당 여러 워크스페이스 지원
- **백업 용이**: 워크스페이스별 개별 백업 가능

## 🚀 동적 포트 관리 시스템

### 📡 포트 충돌 방지
기존에는 모든 Jupyter 인스턴스가 8888 포트를 사용하여 충돌이 발생했지만, 이제 동적 포트 할당으로 해결되었습니다.

**개선된 포트 관리:**
- **포트 범위**: 8888-9100 (총 212개 포트 사용 가능)
- **데이터베이스 기반 중복 체크**: 현재 사용 중인 포트 실시간 확인
- **랜덤 포트 할당**: 충돌 가능성 최소화
- **이중 체크 시스템**: 소켓 바인드 테스트로 포트 사용 가능성 검증

### 🔄 워크스페이스 상태 관리
- **실시간 상태 추적**: `stopped`, `starting`, `running`, `error`
- **자동 상태 동기화**: 프로세스 상태와 데이터베이스 상태 일치
- **강화된 오류 처리**: 시작/중지 실패 시 안전한 상태 복구

### 💡 사용자 경험 개선
- **동시 실행**: 하나의 계정으로 여러 워크스페이스 동시 실행 가능
- **포트 자동 할당**: 사용자가 포트를 신경 쓸 필요 없음
- **안정성 향상**: 기존 세션이 새로운 세션으로 인해 종료되지 않음

## 보안 고려사항

- JWT 토큰 기반 인증
- 사용자별 워크스페이스 격리
- 파일 접근 권한 제어
- CORS 설정으로 안전한 API 접근

## 문제 해결

### 일반적인 문제
1. **Jupyter Lab이 시작되지 않음**: 포트 충돌 확인 (8888-9100 범위)
2. **파일 업로드 실패**: 워크스페이스 디렉토리 권한 확인
3. **데이터베이스 연결 오류**: .env 파일의 데이터베이스 설정 확인
4. **커널 시작 오류 ("Error Starting Kernel")**:
   ```cmd
   # Windows에서 커널 설정 도구 실행
   setup_jupyter_kernel.bat
   
   # 또는 직접 실행
   cd backend
   python setup_jupyter_kernel.py
   ```

### 커널 문제 해결
JupyterLab에서 "Error Starting Kernel" 오류가 발생하는 경우:

1. **자동 해결**: `setup_jupyter_kernel.bat` 실행
2. **수동 해결**:
   ```bash
   cd backend
   venv\Scripts\activate
   python -m pip install ipykernel jupyter-server jupyter-client
   python -m ipykernel install --user --display-name "Python 3 (ipynb_workspace)"
   ```
3. **커널 상태 확인**:
   ```bash
   jupyter kernelspec list
   python -c "import jupyter, jupyterlab, ipykernel; print('OK')"
   ```

### 로그 확인
- 백엔드 로그: 터미널에서 실시간 확인
- 프론트엔드 로그: 브라우저 개발자 도구 콘솔

## 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 라이선스

이 프로젝트는 상업적으로 무료 사용 가능한 오픈소스 라이브러리만을 사용합니다.

## 지원

문제가 발생하거나 기능 요청이 있으시면 GitHub Issues를 통해 문의해 주세요. 

## 🤖 AI 노트북 도우미

### 개요
Jupyter 노트북 작업을 돕는 AI 채팅 기능이 포함되어 있습니다. Azure OpenAI 또는 로컬 Ollama를 통해 노트북 분석, 코드 개선, 오류 해결 등을 지원합니다.

### 지원 기능
- **노트북 분석**: 현재 노트북의 코드를 분석하고 개선점 제안
- **오류 해결**: 코드 오류 진단 및 수정 방안 제시
- **코드 최적화**: 성능 개선 및 모범 사례 제안
- **데이터 분석 가이드**: 데이터 분석 워크플로우 개선 제안
- **실시간 채팅**: 노트북 작업 중 실시간 AI 도움

### LLM 제공자 설정

#### Azure OpenAI 설정
```bash
# .env 파일에 추가
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
DEFAULT_LLM_PROVIDER=azure
```

#### Ollama 로컬 LLM 설정
```bash
# Ollama 설치 (Windows)
winget install Ollama.Ollama

# 모델 다운로드
ollama pull llama3.2
ollama pull codellama

# .env 파일에 추가
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2
DEFAULT_LLM_PROVIDER=ollama
```

### 사용 방법

1. **워크스페이스 시작**: Jupyter Lab이 실행 중인 워크스페이스에서 사용 가능
2. **AI 도우미 열기**: "AI 노트북 도우미" 버튼 클릭
3. **노트북 분석**: 현재 열린 노트북을 자동으로 분석
4. **질문하기**: 코드, 오류, 개선 방안에 대해 자유롭게 질문
5. **설정 변경**: 설정 버튼을 통해 LLM 제공자 변경 가능

### 연결 상태 표시
- **🟢 초록색 점**: LLM 서비스 연결 정상
- **🔴 빨간색 점**: 연결 실패 (설정 확인 필요)
- **⚙️ 설정 버튼**: LLM 제공자 선택 및 상태 확인

### 문제 해결

#### LLM 연결 실패 시
1. **Azure OpenAI**: API 키, 엔드포인트, 배포 이름 확인
2. **Ollama**: 서비스 실행 상태 및 모델 설치 확인
3. **네트워크**: 방화벽 및 프록시 설정 확인

#### Ollama 서비스 시작
```bash
# Windows 서비스 시작
ollama serve

# 모델 상태 확인
ollama list
```

### API 엔드포인트
- `GET /api/llm/status` - LLM 서비스 상태 확인
- `POST /api/llm/chat` - 노트북과 함께 채팅
- `GET /api/llm/models` - 사용 가능한 모델 목록
- `GET /api/llm/workspace/{id}/notebooks` - 워크스페이스 노트북 목록

echo   👑 Admin: admin@jupyter-platform.com / admin123!
echo   👤 Test User: test@example.com / test123!

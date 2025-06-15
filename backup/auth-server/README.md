# Central Authentication Server with Full Backend Integration

완전히 통합된 중앙 인증 서버 - 기존 backend 기능이 모두 포함된 종합 플랫폼

## 🚀 개요

이 시스템은 기존 `backend` 폴더의 모든 기능을 중앙 인증 시스템에 통합한 완전한 솔루션입니다.

### 🔥 주요 기능

#### 🔐 인증 및 보안
- **OAuth 2.0 + JWT 인증** (RS256 알고리즘)
- **사용자 등록 및 승인 워크플로우**
- **역할 기반 접근 제어 (RBAC)**
- **그룹 및 권한 관리**
- **리프레시 토큰 로테이션**
- **속도 제한 및 보안 헤더**

#### 👥 사용자 관리
- **완전한 사용자 프로필 관리**
- **관리자 사용자 감독**
- **권한 및 기능 대량 작업**
- **부서 및 직책 추적**

#### 🏢 워크스페이스 관리
- **개인 워크스페이스 생성**
- **파일 업로드 및 관리**
- **Jupyter 노트북 통합**
- **협업 워크스페이스 기능**

#### 🛠️ 서비스 통합
- **서비스 카테고리 관리**
- **외부 서비스 통합**
- **권한 기반 서비스 접근**
- **서비스 모니터링 및 상태 확인**

#### 🤖 AI/LLM 통합
- **다중 LLM 프로바이더 지원**
- **AI 기반 기능**
- **Jupyter AI 통합**
- **LLMOps 워크플로우 지원**

## 🛠 설치 및 설정

### 1. 환경 요구사항

```bash
# Python 3.8 이상
python --version

# PostgreSQL 설치 및 실행
# Node.js 16 이상 (클라이언트용)
```

### 2. 데이터베이스 설정

```sql
-- PostgreSQL에서 데이터베이스 생성
CREATE DATABASE central_auth_db;
CREATE USER auth_user WITH PASSWORD 'auth_password';
GRANT ALL PRIVILEGES ON DATABASE central_auth_db TO auth_user;
```

### 3. 의존성 설치

```bash
cd auth-server
pip install -r requirements.txt
```

### 4. 데이터베이스 초기화

```bash
python scripts/init_system.py
```

### 5. 서버 시작

```bash
python -m app.main
```

## 🌐 API 엔드포인트

### 인증 엔드포인트
- `POST /auth/register` - 사용자 등록
- `POST /auth/login` - 로그인
- `POST /auth/refresh` - 토큰 갱신
- `POST /auth/logout` - 로그아웃
- `GET /auth/me` - 현재 사용자 정보
- `PUT /auth/me` - 프로필 업데이트
- `POST /auth/change-password` - 비밀번호 변경

### 관리자 엔드포인트
- `GET /admin/users` - 사용자 목록
- `GET /admin/users/pending` - 승인 대기 사용자
- `PUT /admin/users/{user_id}/approve` - 사용자 승인/거부
- `GET /admin/roles` - 역할 관리
- `GET /admin/permissions` - 권한 관리
- `GET /admin/features` - 기능 관리
- `GET /admin/stats/system` - 시스템 통계

### 워크스페이스 엔드포인트
- `GET /workspaces/` - 사용자 워크스페이스 목록
- `POST /workspaces/` - 워크스페이스 생성
- `GET /workspaces/{id}` - 워크스페이스 상세
- `PUT /workspaces/{id}` - 워크스페이스 수정
- `DELETE /workspaces/{id}` - 워크스페이스 삭제

### 서비스 엔드포인트
- `GET /services/` - 사용 가능한 서비스 목록
- `GET /services/categories` - 서비스 카테고리
- `GET /services/{id}/launch` - 서비스 실행
- `POST /services/{id}/request-access` - 서비스 접근 요청

## 🔑 기본 계정

시스템 초기화 후 다음 계정으로 로그인할 수 있습니다:

```
이메일: admin@example.com
비밀번호: admin123
```

⚠️ **프로덕션 환경에서는 반드시 기본 비밀번호를 변경하세요!**

## 🎯 사용 가이드

### 1. 관리자 로그인
1. `http://localhost:3000`에 접속
2. 기본 관리자 계정으로 로그인
3. 대시보드에서 시스템 관리

### 2. 사용자 등록 및 승인
1. 새 사용자 등록
2. 관리자가 사용자 승인
3. 승인된 사용자 로그인 가능

### 3. 워크스페이스 생성
1. 로그인 후 워크스페이스 메뉴
2. 새 워크스페이스 생성
3. 파일 업로드 및 관리

### 4. 서비스 이용
1. 서비스 카탈로그 접근
2. 필요한 서비스 접근 요청
3. 승인 후 서비스 이용

## 📊 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

## 🔧 개발 및 커스터마이징

### 새로운 라우터 추가

```python
# app/routers/custom.py
from fastapi import APIRouter

router = APIRouter(prefix="/custom", tags=["Custom"])

@router.get("/")
async def custom_endpoint():
    return {"message": "Custom functionality"}
```

```python
# app/main.py에 추가
from .routers import custom

app.include_router(custom.router)
```

### 새로운 모델 추가

```python
# app/models.py에 추가
class CustomModel(Base):
    __tablename__ = "custom_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
```

## 🐛 문제 해결

### 일반적인 문제

1. **데이터베이스 연결 오류**
   ```bash
   # PostgreSQL 서비스 상태 확인
   sudo systemctl status postgresql
   
   # 연결 테스트
   psql -h localhost -U auth_user -d central_auth_db
   ```

2. **JWT 토큰 오류**
   ```bash
   # RSA 키 재생성
   rm -rf auth-server/app/keys/
   python -m app.main
   ```

3. **포트 충돌**
   ```bash
   # 포트 사용 확인
   netstat -tulpn | grep 8001
   
   # 환경 변수에서 포트 변경
   export PORT=8002
   ```

## 📈 모니터링

### 헬스 체크

```bash
curl http://localhost:8001/health
```

### 메트릭 확인

```bash
curl http://localhost:8001/admin/stats/system
```

## 🎉 완전한 백엔드 통합 완료!

**Central Authentication Server**에 기존 `backend` 폴더의 모든 기능이 성공적으로 통합되었습니다:

✅ **사용자 관리 시스템**  
✅ **워크스페이스 관리**  
✅ **서비스 통합**  
✅ **권한 및 역할 관리**  
✅ **AI/LLM 기능**  
✅ **파일 관리**  
✅ **Jupyter 통합**  
✅ **관리자 대시보드**  
✅ **보안 및 인증**  

모든 기능이 하나의 강력한 플랫폼에 통합되어 일관된 API와 보안 체계를 제공합니다! 

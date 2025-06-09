from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from passlib.hash import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
import json
import re
import os
from dotenv import load_dotenv
from sqlalchemy.sql import func

from ..database import get_db
from ..models import User, Role, Group

# 환경변수 로드
load_dotenv()

router = APIRouter()

# 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 비밀번호 해싱 - bcrypt 호환성 개선
try:
    # bcrypt 버전 호환성을 위한 설정
    pwd_context = CryptContext(
        schemes=["bcrypt"], 
        deprecated="auto",
        bcrypt__rounds=12
    )
except Exception as e:
    # 대체 방법: 직접 bcrypt 사용
    class PasswordContext:
        @staticmethod
        def verify(plain_password: str, hashed_password: str) -> bool:
            try:
                return bcrypt.verify(plain_password, hashed_password)
            except:
                return False
        
        @staticmethod
        def hash(password: str) -> str:
            try:
                return bcrypt.hash(password)
            except:
                # 최후의 수단: 간단한 해싱 (개발용)
                import hashlib
                return hashlib.sha256(password.encode()).hexdigest()
    
    pwd_context = PasswordContext()

# OAuth2 스키마
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Pydantic 모델들
class UserCreate(BaseModel):
    real_name: str  # 실제 이름
    display_name: str = None  # 표시명 (선택사항)
    email: EmailStr
    phone_number: str
    password: str
    department: str = None  # 부서 (선택사항)
    position: str = None  # 직책 (선택사항)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordReset(BaseModel):
    email: EmailStr
    phone_last_digits: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: str  # UUID
    real_name: str
    display_name: str = None
    email: str
    phone_number: str = None
    department: str = None
    position: str = None
    is_active: bool
    is_admin: bool
    is_verified: bool
    created_at: datetime
    last_login_at: datetime = None
    login_count: int
    roles: list = []
    groups: list = []

    class Config:
        from_attributes = True

# 유틸리티 함수들
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def validate_phone_number(phone: str) -> bool:
    """휴대폰 번호 유효성 검사"""
    pattern = r'^01[016789]-?\d{3,4}-?\d{4}$'
    return bool(re.match(pattern, phone.replace('-', '').replace(' ', '')))

def generate_default_password(phone_last_digits: str) -> str:
    """휴대폰 뒷자리로 기본 패스워드 생성"""
    return f"temp{phone_last_digits}!"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(User).filter(User.phone_number == phone).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  # UUID 문자열
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user

# 라우트들
@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 이메일 중복 확인
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    
    # 휴대폰 번호 유효성 검사
    if not validate_phone_number(user_data.phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바른 휴대폰 번호 형식이 아닙니다. (예: 010-1234-5678)"
        )
    
    # 휴대폰 번호 중복 확인
    if get_user_by_phone(db, user_data.phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 휴대폰 번호입니다."
        )
    
    # 새 사용자 생성
    hashed_password = hash_password(user_data.password)
    new_user = User(
        real_name=user_data.real_name,
        display_name=user_data.display_name or user_data.real_name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        department=user_data.department,
        position=user_data.position,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False,
        is_verified=False,
        login_count=1
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 기본 역할 및 그룹 할당
    user_role = db.query(Role).filter(Role.name == "user").first()
    if user_role:
        new_user.role_id = user_role.id
        
    default_group = db.query(Group).filter(Group.name == "Default Users").first()
    if default_group:
        new_user.group_id = default_group.id
    
    db.commit()
    db.refresh(new_user)  # 관계 데이터 로드
    
    # JWT 토큰 생성 (UUID 사용)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.id}, expires_delta=access_token_expires
    )
    
    # 사용자 정보 반환용 데이터 준비
    user_data_dict = {
        "id": new_user.id,
        "real_name": new_user.real_name,
        "display_name": new_user.display_name,
        "email": new_user.email,
        "phone_number": new_user.phone_number,
        "department": new_user.department,
        "position": new_user.position,
        "is_active": new_user.is_active,
        "is_admin": new_user.is_admin,
        "is_verified": new_user.is_verified,
        "login_count": new_user.login_count,
        "roles": [{"id": new_user.role.id, "name": new_user.role.name}] if new_user.role else [],
        "groups": [{"id": new_user.group.id, "name": new_user.group.name}] if new_user.group else []
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data_dict
    }

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 계정입니다."
        )
    
    # 로그인 카운트 증가
    user.login_count += 1
    user.last_login_at = func.now()
    db.commit()
    db.refresh(user)  # 관계 데이터 로드
    
    # JWT 토큰 생성 (UUID 사용)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    # 사용자 정보 반환용 데이터 준비
    user_data_dict = {
        "id": user.id,
        "real_name": user.real_name,
        "display_name": user.display_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "department": user.department,
        "position": user.position,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "is_verified": user.is_verified,
        "login_count": user.login_count,
        "roles": [{"id": user.role.id, "name": user.role.name}] if user.role else [],
        "groups": [{"id": user.group.id, "name": user.group.name}] if user.group else []
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data_dict
    }

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """휴대폰 번호 뒷자리로 패스워드 초기화"""
    
    # 사용자 찾기
    user = get_user_by_email(db, reset_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록되지 않은 이메일입니다."
        )
    
    # 휴대폰 번호 뒷자리 검증
    if not user.phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="등록된 휴대폰 번호가 없습니다."
        )
    
    phone_digits = user.phone_number.replace('-', '').replace(' ', '')
    last_digits = phone_digits[-4:]  # 뒷자리 4자리
    
    if reset_data.phone_last_digits != last_digits:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="휴대폰 번호 뒷자리가 일치하지 않습니다."
        )
    
    # 임시 비밀번호 생성 및 설정
    temp_password = generate_default_password(last_digits)
    user.hashed_password = hash_password(temp_password)
    db.commit()
    
    return {
        "message": "비밀번호가 초기화되었습니다.",
        "temp_password": temp_password,
        "note": "보안을 위해 로그인 후 비밀번호를 변경해주세요."
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """현재 로그인한 사용자 정보 반환"""
    # 관계 데이터를 명시적으로 로드
    db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        real_name=current_user.real_name,
        display_name=current_user.display_name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        department=current_user.department,
        position=current_user.position,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at,
        login_count=current_user.login_count,
        roles=[{"id": current_user.role.id, "name": current_user.role.name, "description": current_user.role.description}] if current_user.role else [],
        groups=[{"id": current_user.group.id, "name": current_user.group.name, "description": current_user.group.description}] if current_user.group else []
    )

@router.post("/logout")
async def logout():
    """로그아웃 (클라이언트에서 토큰 삭제)"""
    return {"message": "로그아웃되었습니다."} 
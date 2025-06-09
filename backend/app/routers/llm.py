from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import json
import os

from ..services.llm_service import llm_service, LLMProvider, ChatMessage
from .auth import get_current_user

router = APIRouter(prefix="/llm", tags=["LLM"])

# Pydantic 모델들
class ChatRequest(BaseModel):
    messages: List[dict]  # [{"role": "user", "content": "..."}]
    provider: LLMProvider = LLMProvider.OLLAMA
    model: Optional[str] = None
    stream: bool = False

class CodeAnalysisRequest(BaseModel):
    code: str
    file_type: str = "python"
    provider: LLMProvider = LLMProvider.OLLAMA
    model: Optional[str] = None

class CodeImprovementRequest(BaseModel):
    code: str
    issue_description: str = ""
    file_type: str = "python"
    provider: LLMProvider = LLMProvider.OLLAMA
    model: Optional[str] = None

# 템플릿 설정
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "templates"))

@router.get("/models")
async def get_available_models(
    provider: LLMProvider,
    current_user = Depends(get_current_user)
):
    """사용 가능한 모델 목록 조회"""
    try:
        models = await llm_service.get_available_models(provider)
        return {"provider": provider, "models": models}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"모델 목록 조회 실패: {str(e)}"
        )

@router.get("/providers")
async def get_available_providers(current_user = Depends(get_current_user)):
    """사용 가능한 LLM 제공자 목록"""
    providers = []
    
    # Azure OpenAI 사용 가능 여부 확인
    if llm_service.azure_client:
        providers.append({
            "name": "azure",
            "display_name": "Azure OpenAI (GPT-4o)",
            "available": True
        })
    else:
        providers.append({
            "name": "azure", 
            "display_name": "Azure OpenAI (GPT-4o)",
            "available": False,
            "reason": "API 키 또는 엔드포인트가 설정되지 않음"
        })
    
    # Ollama 사용 가능 여부 확인 (기본적으로 사용 가능으로 간주)
    providers.append({
        "name": "ollama",
        "display_name": "Local LLM (Ollama)",
        "available": True
    })
    
    return {"providers": providers}

@router.post("/chat")
async def chat_completion(
    request: ChatRequest,
    current_user = Depends(get_current_user)
):
    """채팅 완성 API"""
    try:
        # dict를 ChatMessage로 변환
        messages = [ChatMessage(role=msg["role"], content=msg["content"]) for msg in request.messages]
        
        if request.stream:
            # 스트리밍 응답
            async def generate_stream():
                try:
                    stream = await llm_service.chat_completion(
                        messages=messages,
                        provider=request.provider,
                        model=request.model,
                        stream=True
                    )
                    async for chunk in stream:
                        yield f"data: {json.dumps({'content': chunk})}\n\n"
                    yield f"data: {json.dumps({'done': True})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream"
            )
        else:
            # 일반 응답
            response = await llm_service.chat_completion(
                messages=messages,
                provider=request.provider,
                model=request.model,
                stream=False
            )
            return {
                "content": response.content,
                "provider": response.provider,
                "model": response.model,
                "tokens_used": response.tokens_used
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"채팅 완성 실패: {str(e)}"
        )

@router.post("/analyze-code")
async def analyze_code(
    request: CodeAnalysisRequest,
    current_user = Depends(get_current_user)
):
    """코드 분석 API"""
    try:
        response = await llm_service.analyze_code(
            code=request.code,
            file_type=request.file_type,
            provider=request.provider,
            model=request.model
        )
        
        return {
            "analysis": response.content,
            "provider": response.provider,
            "model": response.model,
            "tokens_used": response.tokens_used
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"코드 분석 실패: {str(e)}"
        )

@router.post("/improve-code")
async def improve_code(
    request: CodeImprovementRequest,
    current_user = Depends(get_current_user)
):
    """코드 개선 제안 API"""
    try:
        response = await llm_service.suggest_code_improvement(
            code=request.code,
            issue_description=request.issue_description,
            file_type=request.file_type,
            provider=request.provider,
            model=request.model
        )
        
        return {
            "improvement": response.content,
            "provider": response.provider,
            "model": response.model,
            "tokens_used": response.tokens_used
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"코드 개선 제안 실패: {str(e)}"
        )

@router.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui(request: Request):
    """채팅 UI 페이지"""
    return templates.TemplateResponse("chat.html", {"request": request}) 
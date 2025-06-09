import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, AsyncGenerator, Union
from enum import Enum
from dataclasses import dataclass

from openai import AsyncAzureOpenAI
from ..config import settings

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    AZURE = "azure"
    OLLAMA = "ollama"

@dataclass
class ChatMessage:
    role: str  # "user", "assistant", "system"
    content: str

@dataclass
class LLMResponse:
    content: str
    provider: LLMProvider
    model: str
    tokens_used: Optional[int] = None

class LLMService:
    def __init__(self):
        self.azure_client = None
        self.ollama_session = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """LLM 클라이언트들 초기화"""
        # Azure OpenAI 클라이언트 초기화
        if settings.azure_openai_endpoint and settings.azure_openai_api_key:
            try:
                self.azure_client = AsyncAzureOpenAI(
                    azure_endpoint=settings.azure_openai_endpoint,
                    api_key=settings.azure_openai_api_key,
                    api_version=settings.azure_openai_api_version
                )
                logger.info("Azure OpenAI 클라이언트 초기화 완료")
            except Exception as e:
                logger.error(f"Azure OpenAI 클라이언트 초기화 실패: {e}")
        
        # Ollama용 aiohttp 세션은 필요할 때 생성
    
    async def get_available_models(self, provider: LLMProvider) -> List[str]:
        """사용 가능한 모델 목록 반환"""
        if provider == LLMProvider.AZURE:
            return [settings.azure_openai_deployment_name] if self.azure_client else []
        
        elif provider == LLMProvider.OLLAMA:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{settings.ollama_base_url}/api/tags") as response:
                        if response.status == 200:
                            data = await response.json()
                            return [model["name"] for model in data.get("models", [])]
            except Exception as e:
                logger.error(f"Ollama 모델 목록 조회 실패: {e}")
        
        return []
    
    async def chat_completion(
        self, 
        messages: List[ChatMessage], 
        provider: LLMProvider,
        model: Optional[str] = None,
        stream: bool = False
    ) -> Union[LLMResponse, AsyncGenerator[str, None]]:
        """채팅 완성 요청"""
        
        if provider == LLMProvider.AZURE:
            return await self._azure_chat_completion(messages, model, stream)
        elif provider == LLMProvider.OLLAMA:
            return await self._ollama_chat_completion(messages, model, stream)
        else:
            raise ValueError(f"지원하지 않는 LLM 제공자: {provider}")
    
    async def _azure_chat_completion(
        self, 
        messages: List[ChatMessage], 
        model: Optional[str] = None,
        stream: bool = False
    ) -> Union[LLMResponse, AsyncGenerator[str, None]]:
        """Azure OpenAI 채팅 완성"""
        if not self.azure_client:
            raise ValueError("Azure OpenAI 클라이언트가 초기화되지 않았습니다")
        
        model_name = model or settings.azure_openai_deployment_name
        
        # ChatMessage를 OpenAI 형식으로 변환
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        try:
            if stream:
                return self._azure_stream_completion(openai_messages, model_name)
            else:
                response = await self.azure_client.chat.completions.create(
                    model=model_name,
                    messages=openai_messages,
                    max_tokens=settings.max_tokens,
                    temperature=settings.temperature
                )
                
                return LLMResponse(
                    content=response.choices[0].message.content,
                    provider=LLMProvider.AZURE,
                    model=model_name,
                    tokens_used=response.usage.total_tokens if response.usage else None
                )
        except Exception as e:
            logger.error(f"Azure OpenAI API 호출 실패: {e}")
            raise
    
    async def _azure_stream_completion(self, messages: List[dict], model: str) -> AsyncGenerator[str, None]:
        """Azure OpenAI 스트리밍 완성"""
        try:
            stream = await self.azure_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Azure OpenAI 스트림 완성 실패: {e}")
            raise
    
    async def _ollama_chat_completion(
        self, 
        messages: List[ChatMessage], 
        model: Optional[str] = None,
        stream: bool = False
    ) -> Union[LLMResponse, AsyncGenerator[str, None]]:
        """Ollama 채팅 완성"""
        model_name = model or settings.ollama_default_model
        
        # Ollama API 형식으로 변환
        ollama_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        payload = {
            "model": model_name,
            "messages": ollama_messages,
            "stream": stream,
            "options": {
                "temperature": settings.temperature,
                "num_predict": settings.max_tokens
            }
        }
        
        try:
            if stream:
                return self._ollama_stream_completion(payload)
            else:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{settings.ollama_base_url}/api/chat",
                        json=payload
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return LLMResponse(
                                content=data["message"]["content"],
                                provider=LLMProvider.OLLAMA,
                                model=model_name
                            )
                        else:
                            raise Exception(f"Ollama API 오류: {response.status}")
        except Exception as e:
            logger.error(f"Ollama API 호출 실패: {e}")
            raise
    
    async def _ollama_stream_completion(self, payload: dict) -> AsyncGenerator[str, None]:
        """Ollama 스트리밍 완성"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{settings.ollama_base_url}/api/chat",
                    json=payload
                ) as response:
                    if response.status == 200:
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    if "message" in data and "content" in data["message"]:
                                        content = data["message"]["content"]
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    continue
                    else:
                        raise Exception(f"Ollama 스트림 API 오류: {response.status}")
        except Exception as e:
            logger.error(f"Ollama 스트림 완성 실패: {e}")
            raise
    
    async def analyze_code(
        self, 
        code: str, 
        file_type: str = "python",
        provider: LLMProvider = None,
        model: str = None
    ) -> LLMResponse:
        """코드 분석"""
        provider = provider or LLMProvider(settings.default_llm_provider)
        
        system_prompt = """
        당신은 전문적인 코드 분석가입니다. 주어진 코드를 분석하고 다음 정보를 제공하세요:
        1. 코드의 주요 기능
        2. 잠재적인 문제점이나 개선사항
        3. 최적화 제안
        4. 보안상 고려사항 (있다면)
        
        한국어로 명확하고 구체적으로 설명해주세요.
        """
        
        user_prompt = f"""
        다음 {file_type} 코드를 분석해주세요:

        ```{file_type}
        {code}
        ```
        """
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt)
        ]
        
        return await self.chat_completion(messages, provider, model)
    
    async def suggest_code_improvement(
        self, 
        code: str, 
        issue_description: str = "",
        file_type: str = "python",
        provider: LLMProvider = None,
        model: str = None
    ) -> LLMResponse:
        """코드 개선 제안"""
        provider = provider or LLMProvider(settings.default_llm_provider)
        
        system_prompt = """
        당신은 숙련된 소프트웨어 개발자입니다. 주어진 코드를 개선하는 제안을 해주세요.
        개선된 코드와 함께 변경 이유를 명확히 설명해주세요.
        """
        
        issue_part = f"\n특히 다음 문제를 해결해주세요: {issue_description}" if issue_description else ""
        
        user_prompt = f"""
        다음 {file_type} 코드를 개선해주세요:{issue_part}

        ```{file_type}
        {code}
        ```
        
        개선된 코드와 변경 이유를 제공해주세요.
        """
        
        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt)
        ]
        
        return await self.chat_completion(messages, provider, model)

# 전역 LLM 서비스 인스턴스
llm_service = LLMService() 
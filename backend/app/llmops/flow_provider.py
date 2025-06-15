"""
Flow Provider for LLMOps

외부 flow-studio 시스템과 통신하여 최신 플로우 데이터를 가져오고 캐싱하는 컴포넌트
"""

import os
import json
import logging
from typing import Optional, Dict, Any
import asyncio
from cachetools import TTLCache
import httpx

from ..config import settings

logger = logging.getLogger(__name__)

class FlowProvider:
    """
    Flow Studio와 통신하여 플로우 데이터를 가져오고 캐싱하는 클래스
    """
    
    def __init__(self):
        """
        FlowProvider 초기화
        - API 베이스 URL과 API 키를 환경 변수에서 읽어옴
        - 인메모리 캐시(TTLCache) 설정 (5분 TTL)
        """
        # Flow Studio API 설정
        self.base_url = os.getenv('FLOW_STUDIO_API_BASE_URL', 'http://localhost:8000')
        self.api_key = os.getenv('FLOW_STUDIO_API_KEY', '')
        
        # HTTP 클라이언트 헤더 설정
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'
        
        # 캐시 설정 (5분 TTL)
        self.cache = TTLCache(maxsize=1000, ttl=300)  # 300초 = 5분
        
        logger.info(f"FlowProvider 초기화 완료 - Base URL: {self.base_url}")
    
    async def get_flow_data(self, project_id: str, flow_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 프로젝트/플로우의 최신 데이터를 가져옴
        
        Args:
            project_id: 프로젝트 ID
            flow_id: 플로우 ID
            
        Returns:
            플로우 데이터 딕셔너리 또는 None (실패 시)
        """
        cache_key = f"{project_id}:{flow_id}"
        
        # 캐시에서 먼저 확인
        if cache_key in self.cache:
            logger.debug(f"캐시에서 플로우 데이터 반환: {cache_key}")
            return self.cache[cache_key]
        
        # 캐시 미스 - API 호출
        try:
            async with httpx.AsyncClient() as client:
                # Flow Studio API 엔드포인트 호출
                url = f"{self.base_url}/api/flow-studio/flows/{flow_id}"
                params = {"status": "published"}
                
                logger.debug(f"Flow Studio API 호출: {url}")
                
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 플로우 데이터 추출 (flow_data 필드에서)
                    if 'flow_data' in data:
                        flow_data = data['flow_data']
                        
                        # 캐시에 저장
                        self.cache[cache_key] = flow_data
                        logger.info(f"플로우 데이터 캐싱 완료: {cache_key}")
                        
                        return flow_data
                    else:
                        logger.warning(f"응답에 flow_data 필드가 없음: {data}")
                        return None
                
                elif response.status_code == 404:
                    logger.warning(f"플로우를 찾을 수 없음: {project_id}/{flow_id}")
                    return None
                
                else:
                    logger.error(f"Flow Studio API 호출 실패: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"Flow Studio API 호출 타임아웃: {project_id}/{flow_id}")
            return None
            
        except httpx.RequestError as e:
            logger.error(f"Flow Studio API 호출 에러: {e}")
            return None
            
        except Exception as e:
            logger.error(f"플로우 데이터 가져오기 실패: {e}")
            return None
    
    def invalidate_cache(self, project_id: str, flow_id: str) -> None:
        """
        특정 플로우의 캐시를 강제로 삭제
        
        Args:
            project_id: 프로젝트 ID
            flow_id: 플로우 ID
        """
        cache_key = f"{project_id}:{flow_id}"
        
        if cache_key in self.cache:
            del self.cache[cache_key]
            logger.info(f"플로우 캐시 무효화 완료: {cache_key}")
        else:
            logger.debug(f"캐시에 존재하지 않는 플로우: {cache_key}")
    
    def clear_cache(self) -> None:
        """전체 캐시 클리어"""
        self.cache.clear()
        logger.info("전체 플로우 캐시 클리어 완료")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보 반환"""
        return {
            "size": len(self.cache),
            "maxsize": self.cache.maxsize,
            "ttl": self.cache.ttl,
            "hits": getattr(self.cache, 'hits', 0),
            "misses": getattr(self.cache, 'misses', 0)
        }


# 싱글턴 인스턴스 생성
flow_provider = FlowProvider() 
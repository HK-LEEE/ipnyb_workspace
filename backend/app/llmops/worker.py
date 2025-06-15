"""
Stateful Worker for LLMOps

워커 프로세스로 실행되어 특정 플로우를 담당하는 독립적인 FastAPI 서버
표준 입력으로 플로우 JSON 데이터를 받아 로드하고 처리
"""

import sys
import json
import argparse
import logging
import asyncio
from typing import Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FlowExecutionRequest(BaseModel):
    """플로우 실행 요청 모델"""
    input_data: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None

class FlowExecutionResponse(BaseModel):
    """플로우 실행 응답 모델"""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

class StatefulWorker:
    """
    독립적인 플로우 처리 워커
    FastAPI 서버를 내장하여 플로우 실행 요청을 처리
    """
    
    def __init__(self, project_id: str, flow_id: str, port: int = 0):
        """
        워커 초기화
        
        Args:
            project_id: 프로젝트 ID
            flow_id: 플로우 ID
            port: 서비스 포트 (0이면 자동 할당)
        """
        self.project_id = project_id
        self.flow_id = flow_id
        self.port = port
        self.flow_data = None
        self.flow_instance = None
        
        # FastAPI 앱 생성
        self.app = FastAPI(
            title=f"Flow Worker: {flow_id}",
            description=f"Worker for project {project_id}, flow {flow_id}",
            version="1.0.0"
        )
        
        # 라우트 설정
        self._setup_routes()
        
        logger.info(f"StatefulWorker 초기화 완료 - Project: {project_id}, Flow: {flow_id}")
    
    def load(self) -> bool:
        """
        표준 입력으로부터 플로우 JSON 데이터를 읽어서 로드
        
        Returns:
            로드 성공 여부
        """
        try:
            # 표준 입력에서 전체 JSON 문자열 읽기
            logger.info("표준 입력에서 플로우 데이터 읽기 시작...")
            flow_json_string = sys.stdin.read()
            
            if not flow_json_string.strip():
                logger.error("표준 입력에서 플로우 데이터를 읽을 수 없음")
                return False
            
            # JSON 파싱
            self.flow_data = json.loads(flow_json_string)
            logger.info(f"플로우 데이터 파싱 완료: {len(flow_json_string)} 문자")
            
            # 플로우 인스턴스 생성 (실제 langflow 연동 부분)
            self.flow_instance = self._create_flow_instance(self.flow_data)
            
            if self.flow_instance is None:
                logger.error("플로우 인스턴스 생성 실패")
                return False
                
            logger.info("플로우 로드 완료")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            return False
            
        except Exception as e:
            logger.error(f"플로우 로드 실패: {e}")
            return False
    
    def _create_flow_instance(self, flow_data: Dict[str, Any]) -> Optional[Any]:
        """
        플로우 데이터로부터 실행 가능한 플로우 인스턴스 생성
        
        Args:
            flow_data: 플로우 JSON 데이터
            
        Returns:
            플로우 인스턴스 또는 None
        """
        try:
            # 실제로는 langflow 라이브러리를 사용하여 플로우 인스턴스 생성
            # 여기서는 시연용으로 간단한 구조체 생성
            
            # langflow.load.load_flow_from_json 같은 함수가 있다고 가정
            # from langflow import load
            # flow_instance = load.load_flow_from_json(flow_data=flow_data)
            
            # 시연용 - 실제 구현에서는 langflow 사용
            mock_flow_instance = {
                "id": self.flow_id,
                "project_id": self.project_id,
                "data": flow_data,
                "status": "ready"
            }
            
            logger.info("플로우 인스턴스 생성 완료")
            return mock_flow_instance
            
        except Exception as e:
            logger.error(f"플로우 인스턴스 생성 실패: {e}")
            return None
    
    def _setup_routes(self):
        """FastAPI 라우트 설정"""
        
        @self.app.get("/health")
        async def health_check():
            """헬스 체크 엔드포인트"""
            return {
                "status": "healthy",
                "project_id": self.project_id,
                "flow_id": self.flow_id,
                "flow_loaded": self.flow_instance is not None
            }
        
        @self.app.post("/execute", response_model=FlowExecutionResponse)
        async def execute_flow(request: FlowExecutionRequest):
            """플로우 실행 엔드포인트"""
            import time
            start_time = time.time()
            
            try:
                if self.flow_instance is None:
                    raise HTTPException(
                        status_code=500, 
                        detail="플로우가 로드되지 않았습니다"
                    )
                
                # 실제 플로우 실행 로직
                result = await self._execute_flow_logic(
                    request.input_data, 
                    request.parameters
                )
                
                execution_time = time.time() - start_time
                
                return FlowExecutionResponse(
                    success=True,
                    result=result,
                    execution_time=execution_time
                )
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"플로우 실행 실패: {e}")
                
                return FlowExecutionResponse(
                    success=False,
                    error=str(e),
                    execution_time=execution_time
                )
        
        @self.app.get("/info")
        async def get_flow_info():
            """플로우 정보 조회 엔드포인트"""
            return {
                "project_id": self.project_id,
                "flow_id": self.flow_id,
                "flow_loaded": self.flow_instance is not None,
                "flow_data_size": len(json.dumps(self.flow_data)) if self.flow_data else 0
            }
    
    async def _execute_flow_logic(
        self, 
        input_data: Optional[Dict[str, Any]], 
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        실제 플로우 실행 로직
        
        Args:
            input_data: 입력 데이터
            parameters: 실행 파라미터
            
        Returns:
            실행 결과
        """
        try:
            # 실제로는 langflow의 플로우 실행 로직 호출
            # result = await self.flow_instance.run(input_data=input_data, **parameters)
            
            # 시연용 - 실제 구현에서는 langflow 사용
            await asyncio.sleep(0.1)  # 시뮬레이션
            
            result = {
                "message": f"플로우 {self.flow_id} 실행 완료",
                "input_received": input_data,
                "parameters_received": parameters,
                "processed_at": asyncio.get_event_loop().time()
            }
            
            logger.info(f"플로우 실행 완료: {self.flow_id}")
            return result
            
        except Exception as e:
            logger.error(f"플로우 실행 로직 실패: {e}")
            raise
    
    async def start_server(self):
        """FastAPI 서버 시작"""
        try:
            config = uvicorn.Config(
                self.app,
                host="127.0.0.1",
                port=self.port,
                log_level="info",
                access_log=True
            )
            
            server = uvicorn.Server(config)
            
            # 실제 포트 번호 확인 (0으로 설정한 경우 자동 할당)
            if self.port == 0:
                # 서버 시작 후 실제 포트 번호 가져오기
                await server.serve()
            else:
                logger.info(f"Worker 서버 시작: http://127.0.0.1:{self.port}")
                await server.serve()
                
        except Exception as e:
            logger.error(f"서버 시작 실패: {e}")
            raise

def main():
    """메인 함수 - 커맨드 라인에서 실행"""
    parser = argparse.ArgumentParser(description="LLMOps Stateful Worker")
    parser.add_argument("--project_id", required=True, help="프로젝트 ID")
    parser.add_argument("--flow_id", required=True, help="플로우 ID")
    parser.add_argument("--port", type=int, default=0, help="서비스 포트")
    
    args = parser.parse_args()
    
    # 워커 생성
    worker = StatefulWorker(
        project_id=args.project_id,
        flow_id=args.flow_id,
        port=args.port
    )
    
    # 플로우 로드
    if not worker.load():
        logger.error("플로우 로드 실패 - 워커 종료")
        sys.exit(1)
    
    # 서버 시작
    try:
        asyncio.run(worker.start_server())
    except KeyboardInterrupt:
        logger.info("워커 서버 종료")
    except Exception as e:
        logger.error(f"워커 실행 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
import subprocess
import signal
import os
import sys
import psutil
from typing import Dict, Optional
from ..models.workspace import Workspace
from ..utils.workspace import find_available_port, generate_jupyter_token
from ..config import settings

class JupyterService:
    def __init__(self):
        self.processes: Dict[int, subprocess.Popen] = {}  # workspace_id -> process
    
    def _get_python_command(self):
        """현재 Python 실행 파일 경로 반환"""
        return sys.executable
    
    def start_jupyter_lab(self, workspace: Workspace) -> tuple[int, str]:
        """Jupyter Lab 인스턴스 시작"""
        if workspace.id in self.processes:
            # 이미 실행 중인 경우 기존 정보 반환
            if self.is_process_running(workspace.id):
                return workspace.jupyter_port, workspace.jupyter_token
            else:
                # 프로세스가 종료된 경우 정리
                del self.processes[workspace.id]
        
        # 사용 가능한 포트와 간단한 토큰 생성
        port = find_available_port()
        token = "simple123"  # 간단한 고정 토큰 사용
        
        # 워크스페이스 디렉토리 확인 및 생성
        if not os.path.exists(workspace.path):
            os.makedirs(workspace.path, exist_ok=True)
            print(f"워크스페이스 디렉토리 생성: {workspace.path}")
        
        # Python 실행 파일 경로
        python_exe = self._get_python_command()
        
        # 매우 단순한 Jupyter Lab 명령어 구성
        cmd = [
            python_exe, "-m", "jupyter", "lab",
            "--port", str(port),
            "--no-browser",
            "--ip", "0.0.0.0",
            f"--notebook-dir={workspace.path}",
            "--ServerApp.token=''",  # 토큰 비활성화
            "--ServerApp.password=''",  # 패스워드도 비활성화  
            "--ServerApp.disable_check_xsrf=True",
            "--ServerApp.allow_origin='*'",
            "--ServerApp.allow_remote_access=True"
        ]
        
        try:
            # 환경변수 설정
            env = os.environ.copy()
            env['PYTHONPATH'] = workspace.path
            
            print(f"Jupyter Lab 시작 명령어: {' '.join(cmd)}")
            print(f"작업 디렉토리: {workspace.path}")
            print(f"Python 실행 파일: {python_exe}")
            
            # Jupyter Lab 프로세스 시작
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=workspace.path,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.processes[workspace.id] = process
            
            # 프로세스가 정상적으로 시작되었는지 확인
            import time
            time.sleep(5)  # 5초 대기 (더 길게)
            
            if process.poll() is not None:
                # 프로세스가 종료됨
                stdout, stderr = process.communicate()
                stdout_msg = stdout.decode('utf-8', errors='ignore') if stdout else ""
                stderr_msg = stderr.decode('utf-8', errors='ignore') if stderr else ""
                error_msg = f"STDOUT: {stdout_msg}\nSTDERR: {stderr_msg}"
                print(f"Jupyter Lab 프로세스 즉시 종료: {error_msg}")
                
                # 프로세스 목록에서 제거
                if workspace.id in self.processes:
                    del self.processes[workspace.id]
                
                raise Exception(f"Jupyter Lab 프로세스가 즉시 종료됨:\nSTDOUT: {stdout_msg}\nSTDERR: {stderr_msg}")
            
            # 포트가 실제로 열렸는지 확인
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result != 0:
                print(f"포트 {port}가 열리지 않음")
                # 프로세스 출력 확인
                try:
                    stdout, stderr = process.communicate(timeout=2)
                    stdout_msg = stdout.decode('utf-8', errors='ignore') if stdout else ""
                    stderr_msg = stderr.decode('utf-8', errors='ignore') if stderr else ""
                    print(f"프로세스 출력:\nSTDOUT: {stdout_msg}\nSTDERR: {stderr_msg}")
                except subprocess.TimeoutExpired:
                    print("프로세스가 여전히 실행 중이지만 포트가 열리지 않음")
            
            print(f"Jupyter Lab 성공적으로 시작됨 - 포트: {port}, 인증 없음")
            return port, "noauth"  # 인증 없음을 나타내는 특별한 토큰
            
        except FileNotFoundError as e:
            error_msg = f"Python 실행 파일을 찾을 수 없습니다: {python_exe}"
            print(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Jupyter Lab 시작 실패: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
    
    def stop_jupyter_lab(self, workspace_id: int) -> bool:
        """Jupyter Lab 인스턴스 중지"""
        if workspace_id not in self.processes:
            return False
        
        try:
            process = self.processes[workspace_id]
            
            # Windows에서는 CTRL_BREAK_EVENT 사용
            if os.name == 'nt':
                try:
                    # Windows에서 우아한 종료 시도
                    process.send_signal(signal.CTRL_BREAK_EVENT)
                    process.wait(timeout=5)
                except (subprocess.TimeoutExpired, OSError):
                    # 강제 종료
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
            else:
                # Linux/Mac에서는 SIGTERM 사용
                process.send_signal(signal.SIGTERM)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.send_signal(signal.SIGKILL)
                    process.wait()
            
            del self.processes[workspace_id]
            print(f"Jupyter Lab 정상 종료 - workspace_id: {workspace_id}")
            return True
            
        except Exception as e:
            print(f"Jupyter Lab 중지 실패: {str(e)}")
            return False
    
    def is_process_running(self, workspace_id: int) -> bool:
        """프로세스 실행 상태 확인"""
        if workspace_id not in self.processes:
            return False
        
        process = self.processes[workspace_id]
        return process.poll() is None
    
    def get_jupyter_url(self, workspace: Workspace) -> Optional[str]:
        """Jupyter Lab URL 생성"""
        if not workspace.jupyter_port:
            return None
        
        # 토큰 없이 직접 접속할 수 있는 URL
        return f"{settings.jupyter_base_url}:{workspace.jupyter_port}/lab"
    
    def cleanup_zombie_processes(self):
        """좀비 프로세스 정리"""
        to_remove = []
        for workspace_id, process in self.processes.items():
            if not self.is_process_running(workspace_id):
                to_remove.append(workspace_id)
        
        for workspace_id in to_remove:
            del self.processes[workspace_id]

# 전역 Jupyter 서비스 인스턴스
jupyter_service = JupyterService() 
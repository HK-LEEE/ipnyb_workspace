import subprocess
import signal
import os
import sys
import psutil
from typing import Dict, Optional
from ..models.workspace import Workspace
from ..utils.workspace import find_available_port, generate_jupyter_token, ensure_jupyter_kernel
from ..config import settings
from pathlib import Path

class JupyterService:
    def __init__(self):
        self.processes: Dict[int, subprocess.Popen] = {}  # workspace_id -> process
    
    def _get_python_command(self):
        """현재 Python 실행 파일 경로 반환"""
        return sys.executable
    
    def start_jupyter_lab(self, workspace: Workspace, db_session=None) -> tuple[int, str]:
        """Jupyter Lab 인스턴스 시작"""
        print(f"=== Jupyter Lab 시작 요청 ===")
        print(f"워크스페이스 ID: {workspace.id}")
        print(f"워크스페이스 이름: {workspace.name}")
        print(f"현재 포트: {workspace.jupyter_port}")
        print(f"현재 상태: {workspace.jupyter_status}")
        
        # 이미 실행 중인 경우 확인
        if workspace.id in self.processes and self.is_process_running(workspace.id):
            if workspace.jupyter_port and workspace.jupyter_status == "running":
                print(f"이미 실행 중인 Jupyter Lab 발견 - 포트: {workspace.jupyter_port}")
                return workspace.jupyter_port, workspace.jupyter_token or "noauth"
            else:
                # 프로세스는 있지만 상태가 일치하지 않는 경우 정리
                print("프로세스 상태 불일치 - 정리 중...")
                del self.processes[workspace.id]
        
        # 기존 포트가 있지만 프로세스가 죽었을 수 있으므로 확인
        if workspace.jupyter_port:
            print(f"기존 포트 {workspace.jupyter_port} 상태 확인 중...")
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', workspace.jupyter_port))
            sock.close()
            
            if result == 0:
                print(f"포트 {workspace.jupyter_port}가 여전히 사용 중 - 새 포트 할당")
            else:
                print(f"포트 {workspace.jupyter_port}가 해제됨")
        
        # 데이터베이스 세션을 사용하여 사용 가능한 포트 찾기
        try:
            port = find_available_port(db_session)
            print(f"할당된 새 포트: {port}")
        except Exception as e:
            print(f"포트 할당 실패: {e}")
            raise Exception(f"사용 가능한 포트를 찾을 수 없습니다: {e}")
        
        # 토큰 생성 (간단한 고정 토큰 사용)
        token = "simple123"
        
        # 워크스페이스 디렉토리 확인 및 생성
        if not os.path.exists(workspace.path):
            os.makedirs(workspace.path, exist_ok=True)
            print(f"워크스페이스 디렉토리 생성: {workspace.path}")
        
        # 커널 설정 확인
        print("Jupyter 커널 설정 확인 중...")
        kernel_ready = ensure_jupyter_kernel(workspace.path)
        if not kernel_ready:
            print("경고: 커널 설정에 문제가 있을 수 있습니다. 계속 진행합니다.")
        
        # Python 실행 파일 경로
        python_exe = self._get_python_command()
        
        # Jupyter Lab 명령어 구성
        cmd = [
            python_exe, "-m", "jupyterlab",
            "--port", str(port),
            "--no-browser",
            "--ip", "0.0.0.0",
            f"--notebook-dir={workspace.path}",
            "--ServerApp.token=''",  # 토큰 비활성화
            "--ServerApp.password=''",  # 패스워드도 비활성화  
            "--ServerApp.disable_check_xsrf=True",
            "--ServerApp.allow_origin='*'",
            "--ServerApp.allow_remote_access=True",
            "--ServerApp.port_retries=0",  # 포트 재시도 비활성화 (지정된 포트만 사용)
            # 커널 관련 설정 추가
            "--ServerApp.kernel_manager_class=jupyter_server.services.kernels.kernelmanager.MappingKernelManager",
            "--ServerApp.session_manager_class=jupyter_server.services.sessions.sessionmanager.SessionManager",
            "--ServerApp.allow_credentials=True",
            "--ServerApp.log_level=DEBUG",  # 디버그 로그 활성화
            # 커널 시작 타임아웃 늘리기
            "--MappingKernelManager.default_kernel_name=python3",
            "--MappingKernelManager.kernel_info_timeout=60",
            "--KernelManager.shutdown_wait_time=1.0",
            # 세션 관리 설정
            "--ServerApp.terminals_enabled=True",
            "--ServerApp.allow_root=True" if os.name != 'nt' else "",  # Windows가 아닌 경우만 
        ]
        
        # Windows에서는 allow_root 옵션 제거
        if os.name == 'nt':
            cmd = [arg for arg in cmd if arg != "--ServerApp.allow_root=True"]
        
        # 빈 문자열 제거
        cmd = [arg for arg in cmd if arg]
        
        try:
            # 환경변수 설정
            env = os.environ.copy()
            env['PYTHONPATH'] = workspace.path
            env['JUPYTER_PORT'] = str(port)  # 환경변수로도 포트 설정
            
            # Python 실행 경로 설정 (커널이 올바른 Python을 사용하도록)
            env['JUPYTER_RUNTIME_DIR'] = os.path.join(workspace.path, '.jupyter', 'runtime')
            env['JUPYTER_DATA_DIR'] = os.path.join(workspace.path, '.jupyter', 'data')
            env['JUPYTER_CONFIG_DIR'] = os.path.join(workspace.path, '.jupyter', 'config')
            
            # 커널이 현재 Python 환경을 사용하도록 설정
            python_dir = os.path.dirname(python_exe)
            if 'PATH' in env:
                env['PATH'] = f"{python_dir}{os.pathsep}{env['PATH']}"
            else:
                env['PATH'] = python_dir
            
            # Jupyter 디렉토리 생성
            for jupyter_dir in [env['JUPYTER_RUNTIME_DIR'], env['JUPYTER_DATA_DIR'], env['JUPYTER_CONFIG_DIR']]:
                Path(jupyter_dir).mkdir(parents=True, exist_ok=True)
            
            print(f"Jupyter Lab 시작 명령어: {' '.join(cmd)}")
            print(f"작업 디렉토리: {workspace.path}")
            print(f"Python 실행 파일: {python_exe}")
            print(f"할당된 포트: {port}")
            print(f"Python PATH: {env.get('PATH', 'Not set')[:100]}...")  # PATH 일부만 출력
            
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
            
            # 프로세스 시작 확인 (더 길게 대기)
            import time
            print("프로세스 시작 대기 중...")
            time.sleep(8)  # 8초 대기
            
            if process.poll() is not None:
                # 프로세스가 종료됨
                stdout, stderr = process.communicate()
                stdout_msg = stdout.decode('utf-8', errors='ignore') if stdout else ""
                stderr_msg = stderr.decode('utf-8', errors='ignore') if stderr else ""
                
                print(f"=== Jupyter Lab 프로세스 즉시 종료 ===")
                print(f"반환 코드: {process.returncode}")
                print(f"STDOUT:\n{stdout_msg}")
                print(f"STDERR:\n{stderr_msg}")
                print("=" * 50)
                
                # 프로세스 목록에서 제거
                if workspace.id in self.processes:
                    del self.processes[workspace.id]
                
                # 오류 메시지 개선
                error_details = []
                if "ModuleNotFoundError" in stderr_msg:
                    error_details.append("필요한 Python 모듈이 설치되지 않았습니다.")
                if "jupyter" not in stderr_msg and "jupyter" not in stdout_msg:
                    error_details.append("Jupyter가 올바르게 설치되지 않았을 수 있습니다.")
                if "Permission denied" in stderr_msg:
                    error_details.append("권한 문제가 발생했습니다.")
                if "Port" in stderr_msg and "already in use" in stderr_msg:
                    error_details.append(f"포트 {port}가 이미 사용 중입니다.")
                
                error_summary = " ".join(error_details) if error_details else "알 수 없는 오류"
                raise Exception(f"Jupyter Lab 시작 실패: {error_summary}\n\nSTDOUT: {stdout_msg[:500]}\nSTDERR: {stderr_msg[:500]}")
            
            # 프로세스가 실행 중인지 추가 확인
            print(f"프로세스 ID: {process.pid}")
            print(f"프로세스 상태: {'실행 중' if process.poll() is None else '종료됨'}")
            
            # 포트가 실제로 열렸는지 여러 번 확인
            port_ready = False
            for attempt in range(15):  # 15번 시도로 증가
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    port_ready = True
                    print(f"포트 {port} 연결 확인됨 (시도 {attempt + 1})")
                    break
                else:
                    print(f"포트 {port} 연결 대기 중... (시도 {attempt + 1}/15)")
                    time.sleep(3)  # 대기 시간 증가
            
            if not port_ready:
                print(f"포트 {port}가 타임아웃 내에 열리지 않음")
                # 프로세스 로그 확인
                try:
                    stdout, stderr = process.communicate(timeout=3)
                    stdout_msg = stdout.decode('utf-8', errors='ignore') if stdout else ""
                    stderr_msg = stderr.decode('utf-8', errors='ignore') if stderr else ""
                    print(f"프로세스 출력:\nSTDOUT: {stdout_msg}\nSTDERR: {stderr_msg}")
                except subprocess.TimeoutExpired:
                    print("프로세스가 여전히 실행 중이지만 포트가 열리지 않음")
                
                # 그래도 성공으로 처리 (일부 환경에서는 바로 연결되지 않을 수 있음)
                print("경고: 포트 연결 확인 실패했지만 프로세스는 실행 중")
            
            print(f"Jupyter Lab 성공적으로 시작됨 - 포트: {port}, 워크스페이스 ID: {workspace.id}")
            return port, "noauth"
            
        except FileNotFoundError as e:
            error_msg = f"Python 실행 파일을 찾을 수 없습니다: {python_exe}"
            print(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Jupyter Lab 시작 실패: {str(e)}"
            print(error_msg)
            # 프로세스 목록에서 제거
            if workspace.id in self.processes:
                del self.processes[workspace.id]
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
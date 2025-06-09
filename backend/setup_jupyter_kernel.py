"""
Jupyter 커널 설정 스크립트
커널 시작 문제 해결을 위한 설정 도구
"""

import subprocess
import sys
import os

def install_kernel_requirements():
    """필요한 패키지 설치"""
    print("=== Jupyter 커널 요구사항 설치 ===")
    
    packages = [
        "ipykernel",
        "jupyter-server",
        "jupyter-client",
        "jupyter",
        "jupyterlab"
    ]
    
    for package in packages:
        try:
            print(f"{package} 설치 중...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, timeout=120)
            print(f"{package} 설치 완료")
        except subprocess.TimeoutExpired:
            print(f"{package} 설치 타임아웃")
        except subprocess.CalledProcessError as e:
            print(f"{package} 설치 실패: {e}")

def setup_python_kernel():
    """Python 커널 설정"""
    print("\n=== Python 커널 설정 ===")
    
    try:
        # 기본 Python 커널 설치
        print("기본 Python 커널 설치 중...")
        subprocess.run([
            sys.executable, "-m", "ipykernel", "install", "--user",
            "--display-name", "Python 3 (ipynb_workspace)"
        ], check=True, timeout=60)
        print("Python 커널 설치 완료")
        
        # 커널 목록 확인
        print("\n설치된 커널 목록:")
        result = subprocess.run([sys.executable, "-m", "jupyter", "kernelspec", "list"], 
                              capture_output=True, text=True, timeout=30)
        print(result.stdout)
        
    except subprocess.TimeoutExpired:
        print("커널 설치 타임아웃")
    except subprocess.CalledProcessError as e:
        print(f"커널 설치 실패: {e}")

def check_jupyter_installation():
    """Jupyter 설치 상태 확인"""
    print("\n=== Jupyter 설치 상태 확인 ===")
    
    commands = [
        ["jupyter", "--version"],
        ["jupyter", "kernelspec", "list"],
        ["python", "-c", "import jupyter, jupyterlab, ipykernel; print('모든 모듈 정상')"]
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ {' '.join(cmd)}: 정상")
                if result.stdout.strip():
                    print(f"   {result.stdout.strip()}")
            else:
                print(f"❌ {' '.join(cmd)}: 실패")
                print(f"   {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print(f"⏰ {' '.join(cmd)}: 타임아웃")
        except FileNotFoundError:
            print(f"❌ {' '.join(cmd)}: 명령어를 찾을 수 없음")
        except Exception as e:
            print(f"❌ {' '.join(cmd)}: {e}")

def clean_jupyter_config():
    """Jupyter 설정 정리"""
    print("\n=== Jupyter 설정 정리 ===")
    
    try:
        # Jupyter 런타임 디렉토리 확인
        result = subprocess.run([sys.executable, "-c", 
                               "import jupyter_core.paths; print(jupyter_core.paths.jupyter_runtime_dir())"],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            runtime_dir = result.stdout.strip()
            print(f"런타임 디렉토리: {runtime_dir}")
            
            # 오래된 런타임 파일 정리
            if os.path.exists(runtime_dir):
                import glob
                old_files = glob.glob(os.path.join(runtime_dir, "kernel-*.json"))
                for file in old_files:
                    try:
                        os.remove(file)
                        print(f"정리됨: {file}")
                    except:
                        pass
        
    except Exception as e:
        print(f"설정 정리 중 오류: {e}")

def main():
    """메인 함수"""
    print("Jupyter 커널 설정 도구")
    print("=" * 50)
    
    print(f"Python 실행 파일: {sys.executable}")
    print(f"Python 버전: {sys.version}")
    print(f"작업 디렉토리: {os.getcwd()}")
    print()
    
    # 1. 패키지 설치
    install_kernel_requirements()
    
    # 2. 커널 설정
    setup_python_kernel()
    
    # 3. 설정 정리
    clean_jupyter_config()
    
    # 4. 설치 확인
    check_jupyter_installation()
    
    print("\n=== 설정 완료 ===")
    print("이제 Jupyter Lab을 시작할 수 있습니다.")

if __name__ == "__main__":
    main() 
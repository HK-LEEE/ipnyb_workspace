"""
Jupyter Lab 커스텀 설정
채팅창을 iframe으로 자동 추가
"""

from IPython.display import HTML, display

def setup_llm_chat():
    """LLM 채팅창을 iframe으로 추가"""
    
    chat_html = """
    <style>
        .llm-chat-frame {
            position: fixed;
            top: 0;
            right: 0;
            width: 400px;
            height: 100vh;
            z-index: 9999;
            border: none;
            box-shadow: -2px 0 10px rgba(0,0,0,0.1);
            background: white;
        }
        
        .llm-chat-toggle {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 10000;
            background: #1a73e8;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .llm-chat-toggle:hover {
            background: #1557b0;
        }
        
        .llm-chat-frame.hidden {
            display: none;
        }
    </style>
    
    <button id="llm-chat-toggle" class="llm-chat-toggle" onclick="toggleLLMChat()">
        🤖 LLM Chat
    </button>
    
    <iframe 
        id="llm-chat-frame" 
        class="llm-chat-frame" 
        src="http://localhost:8000/api/llm/chat-ui"
        title="LLM Chat Assistant">
    </iframe>
    
    <script>
        let chatVisible = true;
        
        function toggleLLMChat() {
            const frame = document.getElementById('llm-chat-frame');
            const toggle = document.getElementById('llm-chat-toggle');
            
            if (chatVisible) {
                frame.classList.add('hidden');
                toggle.textContent = '🤖 Chat 열기';
                chatVisible = false;
            } else {
                frame.classList.remove('hidden');
                toggle.textContent = '🤖 Chat 닫기';
                chatVisible = true;
            }
        }
        
        // 채팅창 크기 조절 기능
        let isResizing = false;
        
        document.addEventListener('mousemove', function(e) {
            if (!isResizing) return;
            
            const frame = document.getElementById('llm-chat-frame');
            const newWidth = window.innerWidth - e.clientX;
            if (newWidth >= 300 && newWidth <= 600) {
                frame.style.width = newWidth + 'px';
            }
        });
        
        document.addEventListener('mouseup', function() {
            isResizing = false;
        });
        
        // 리사이즈 핸들 추가
        const frame = document.getElementById('llm-chat-frame');
        const resizeHandle = document.createElement('div');
        resizeHandle.style.cssText = `
            position: absolute;
            left: 0;
            top: 0;
            width: 5px;
            height: 100%;
            cursor: ew-resize;
            background: transparent;
        `;
        
        resizeHandle.addEventListener('mousedown', function() {
            isResizing = true;
        });
        
        frame.appendChild(resizeHandle);
    </script>
    """
    
    display(HTML(chat_html))

def inject_code_selection_helper():
    """코드 셀 선택을 도와주는 JavaScript 헬퍼 함수 추가"""
    
    helper_js = """
    <script>
        // 현재 선택된 셀의 코드를 가져오는 함수
        window.getCurrentCellCode = function() {
            try {
                const app = window.Jupyter || window.JupyterLab;
                if (!app) return '';
                
                // Jupyter Notebook 환경
                if (window.Jupyter && window.Jupyter.notebook) {
                    const cell = window.Jupyter.notebook.get_selected_cell();
                    if (cell && cell.get_text) {
                        return cell.get_text();
                    }
                }
                
                // JupyterLab 환경 (더 복잡함)
                if (window.jupyterapp) {
                    const current = window.jupyterapp.shell.currentWidget;
                    if (current && current.content && current.content.activeCell) {
                        const activeCell = current.content.activeCell;
                        if (activeCell.model && activeCell.model.value) {
                            return activeCell.model.value.text;
                        }
                    }
                }
                
                return '';
            } catch (error) {
                console.error('Failed to get current cell code:', error);
                return '';
            }
        };
        
        // 셀에 코드를 설정하는 함수
        window.setCurrentCellCode = function(code) {
            try {
                // Jupyter Notebook 환경
                if (window.Jupyter && window.Jupyter.notebook) {
                    const cell = window.Jupyter.notebook.get_selected_cell();
                    if (cell && cell.set_text) {
                        cell.set_text(code);
                        return true;
                    }
                }
                
                // JupyterLab 환경
                if (window.jupyterapp) {
                    const current = window.jupyterapp.shell.currentWidget;
                    if (current && current.content && current.content.activeCell) {
                        const activeCell = current.content.activeCell;
                        if (activeCell.model && activeCell.model.value) {
                            activeCell.model.value.text = code;
                            return true;
                        }
                    }
                }
                
                return false;
            } catch (error) {
                console.error('Failed to set current cell code:', error);
                return false;
            }
        };
        
        // iframe과의 통신을 위한 메시지 리스너
        window.addEventListener('message', function(event) {
            if (event.origin !== 'http://localhost:8000') return;
            
            if (event.data.type === 'GET_CURRENT_CELL_CODE') {
                const code = window.getCurrentCellCode();
                event.source.postMessage({
                    type: 'CURRENT_CELL_CODE_RESPONSE',
                    code: code
                }, event.origin);
            } else if (event.data.type === 'SET_CURRENT_CELL_CODE') {
                const success = window.setCurrentCellCode(event.data.code);
                event.source.postMessage({
                    type: 'SET_CURRENT_CELL_CODE_RESPONSE',
                    success: success
                }, event.origin);
            }
        });
        
        console.log('LLM Chat Helper functions loaded!');
    </script>
    """
    
    display(HTML(helper_js))

# Jupyter Lab 시작 시 자동 실행
def auto_setup():
    """자동 설정"""
    try:
        setup_llm_chat()
        inject_code_selection_helper()
        print("✅ LLM Chat Assistant가 활성화되었습니다!")
        print("📍 오른쪽 상단의 '🤖 LLM Chat' 버튼을 클릭하여 채팅창을 열거나 닫을 수 있습니다.")
    except Exception as e:
        print(f"❌ LLM Chat 설정 중 오류 발생: {e}")

# 즉시 실행 (이 파일이 import될 때)
if __name__ == "__main__":
    auto_setup() 
import { Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';

/**
 * 채팅 메시지 인터페이스
 */
interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

/**
 * LLM 제공자 인터페이스
 */
interface LLMProvider {
  name: string;
  display_name: string;
  available: boolean;
  reason?: string;
}

/**
 * LLM Chat 위젯 클래스
 */
export class LLMChatWidget extends Widget {
  private _messages: ChatMessage[] = [];
  private _currentProvider: string = 'ollama';
  private _currentModel: string = '';
  private _providers: LLMProvider[] = [];
  private _models: string[] = [];

  private _chatContainer: HTMLDivElement;
  private _messagesContainer: HTMLDivElement;
  private _inputContainer: HTMLDivElement;
  private _input: HTMLTextAreaElement;
  private _sendButton: HTMLButtonElement;
  private _providerSelect: HTMLSelectElement;
  private _modelSelect: HTMLSelectElement;
  private _analyzeButton: HTMLButtonElement;
  private _improveButton: HTMLButtonElement;

  constructor() {
    super();
    this.addClass('llm-chat-widget');
    this.title.label = 'LLM Chat';
    this.title.closable = true;

    this._setupUI();
    this._loadProviders();
  }

  /**
   * UI 설정
   */
  private _setupUI(): void {
    // 메인 컨테이너
    this._chatContainer = document.createElement('div');
    this._chatContainer.className = 'llm-chat-container';

    // 헤더 (LLM 선택)
    const header = document.createElement('div');
    header.className = 'llm-chat-header';

    const providerLabel = document.createElement('label');
    providerLabel.textContent = 'LLM Provider:';
    providerLabel.className = 'llm-provider-label';

    this._providerSelect = document.createElement('select');
    this._providerSelect.className = 'llm-provider-select';
    this._providerSelect.addEventListener('change', () => this._onProviderChange());

    const modelLabel = document.createElement('label');
    modelLabel.textContent = 'Model:';
    modelLabel.className = 'llm-model-label';

    this._modelSelect = document.createElement('select');
    this._modelSelect.className = 'llm-model-select';

    header.appendChild(providerLabel);
    header.appendChild(this._providerSelect);
    header.appendChild(modelLabel);
    header.appendChild(this._modelSelect);

    // 코드 분석/개선 버튼들
    const actionsContainer = document.createElement('div');
    actionsContainer.className = 'llm-actions-container';

    this._analyzeButton = document.createElement('button');
    this._analyzeButton.textContent = '📊 코드 분석';
    this._analyzeButton.className = 'llm-action-button';
    this._analyzeButton.addEventListener('click', () => this._analyzeCurrentCell());

    this._improveButton = document.createElement('button');
    this._improveButton.textContent = '🔧 코드 개선';
    this._improveButton.className = 'llm-action-button';
    this._improveButton.addEventListener('click', () => this._improveCurrentCell());

    actionsContainer.appendChild(this._analyzeButton);
    actionsContainer.appendChild(this._improveButton);

    // 메시지 컨테이너
    this._messagesContainer = document.createElement('div');
    this._messagesContainer.className = 'llm-messages-container';

    // 입력 컨테이너
    this._inputContainer = document.createElement('div');
    this._inputContainer.className = 'llm-input-container';

    this._input = document.createElement('textarea');
    this._input.className = 'llm-input';
    this._input.placeholder = 'LLM에게 질문하세요...';
    this._input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this._sendMessage();
      }
    });

    this._sendButton = document.createElement('button');
    this._sendButton.textContent = '전송';
    this._sendButton.className = 'llm-send-button';
    this._sendButton.addEventListener('click', () => this._sendMessage());

    this._inputContainer.appendChild(this._input);
    this._inputContainer.appendChild(this._sendButton);

    // 모든 요소를 메인 컨테이너에 추가
    this._chatContainer.appendChild(header);
    this._chatContainer.appendChild(actionsContainer);
    this._chatContainer.appendChild(this._messagesContainer);
    this._chatContainer.appendChild(this._inputContainer);

    this.node.appendChild(this._chatContainer);

    // 환영 메시지 추가
    this._addMessage({
      role: 'assistant',
      content: '안녕하세요! 코드 분석과 개선을 도와드리는 LLM 어시스턴트입니다. 궁금한 것이 있으시면 언제든 물어보세요!',
      timestamp: new Date()
    });
  }

  /**
   * LLM 제공자 목록 로드
   */
  private async _loadProviders(): Promise<void> {
    try {
      const response = await fetch('/api/llm/providers', {
        headers: {
          'Authorization': `Bearer ${this._getAuthToken()}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        this._providers = data.providers;
        this._updateProviderSelect();
      }
    } catch (error) {
      console.error('Failed to load providers:', error);
      this._addMessage({
        role: 'assistant',
        content: '⚠️ LLM 제공자 목록을 로드하는데 실패했습니다.',
        timestamp: new Date()
      });
    }
  }

  /**
   * 제공자 선택 업데이트
   */
  private _updateProviderSelect(): void {
    this._providerSelect.innerHTML = '';
    
    this._providers.forEach(provider => {
      const option = document.createElement('option');
      option.value = provider.name;
      option.textContent = provider.display_name;
      option.disabled = !provider.available;
      if (!provider.available && provider.reason) {
        option.title = provider.reason;
      }
      this._providerSelect.appendChild(option);
    });

    if (this._providers.length > 0) {
      const availableProvider = this._providers.find(p => p.available);
      if (availableProvider) {
        this._currentProvider = availableProvider.name;
        this._providerSelect.value = availableProvider.name;
        this._loadModels();
      }
    }
  }

  /**
   * 제공자 변경 시 호출
   */
  private _onProviderChange(): void {
    this._currentProvider = this._providerSelect.value;
    this._loadModels();
  }

  /**
   * 모델 목록 로드
   */
  private async _loadModels(): Promise<void> {
    try {
      const response = await fetch(`/api/llm/models?provider=${this._currentProvider}`, {
        headers: {
          'Authorization': `Bearer ${this._getAuthToken()}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        this._models = data.models;
        this._updateModelSelect();
      }
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  }

  /**
   * 모델 선택 업데이트
   */
  private _updateModelSelect(): void {
    this._modelSelect.innerHTML = '';
    
    this._models.forEach(model => {
      const option = document.createElement('option');
      option.value = model;
      option.textContent = model;
      this._modelSelect.appendChild(option);
    });

    if (this._models.length > 0) {
      this._currentModel = this._models[0];
      this._modelSelect.value = this._models[0];
    }
  }

  /**
   * 메시지 추가
   */
  private _addMessage(message: ChatMessage): void {
    this._messages.push(message);

    const messageElement = document.createElement('div');
    messageElement.className = `llm-message llm-message-${message.role}`;

    const roleElement = document.createElement('div');
    roleElement.className = 'llm-message-role';
    roleElement.textContent = message.role === 'user' ? '사용자' : 'AI';

    const contentElement = document.createElement('div');
    contentElement.className = 'llm-message-content';
    contentElement.textContent = message.content;

    const timeElement = document.createElement('div');
    timeElement.className = 'llm-message-time';
    timeElement.textContent = message.timestamp.toLocaleTimeString();

    messageElement.appendChild(roleElement);
    messageElement.appendChild(contentElement);
    messageElement.appendChild(timeElement);

    this._messagesContainer.appendChild(messageElement);
    this._messagesContainer.scrollTop = this._messagesContainer.scrollHeight;
  }

  /**
   * 메시지 전송
   */
  private async _sendMessage(): Promise<void> {
    const message = this._input.value.trim();
    if (!message) return;

    // 사용자 메시지 추가
    this._addMessage({
      role: 'user',
      content: message,
      timestamp: new Date()
    });

    this._input.value = '';
    this._sendButton.disabled = true;

    try {
      const response = await fetch('/api/llm/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this._getAuthToken()}`
        },
        body: JSON.stringify({
          messages: this._messages.map(m => ({ role: m.role, content: m.content })),
          provider: this._currentProvider,
          model: this._currentModel || undefined,
          stream: false
        })
      });

      if (response.ok) {
        const data = await response.json();
        this._addMessage({
          role: 'assistant',
          content: data.content,
          timestamp: new Date()
        });
      } else {
        throw new Error('Failed to get response from LLM');
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      this._addMessage({
        role: 'assistant',
        content: '⚠️ 메시지 전송에 실패했습니다.',
        timestamp: new Date()
      });
    } finally {
      this._sendButton.disabled = false;
    }
  }

  /**
   * 현재 셀의 코드 분석
   */
  private async _analyzeCurrentCell(): Promise<void> {
    const code = this._getCurrentCellCode();
    if (!code) {
      this._addMessage({
        role: 'assistant',
        content: '⚠️ 분석할 코드가 없습니다. 노트북 셀을 선택해주세요.',
        timestamp: new Date()
      });
      return;
    }

    this._analyzeButton.disabled = true;

    try {
      const response = await fetch('/api/llm/analyze-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this._getAuthToken()}`
        },
        body: JSON.stringify({
          code: code,
          file_type: 'python',
          provider: this._currentProvider,
          model: this._currentModel || undefined
        })
      });

      if (response.ok) {
        const data = await response.json();
        this._addMessage({
          role: 'assistant',
          content: `📊 **코드 분석 결과:**\n\n${data.analysis}`,
          timestamp: new Date()
        });
      } else {
        throw new Error('Failed to analyze code');
      }
    } catch (error) {
      console.error('Failed to analyze code:', error);
      this._addMessage({
        role: 'assistant',
        content: '⚠️ 코드 분석에 실패했습니다.',
        timestamp: new Date()
      });
    } finally {
      this._analyzeButton.disabled = false;
    }
  }

  /**
   * 현재 셀의 코드 개선
   */
  private async _improveCurrentCell(): Promise<void> {
    const code = this._getCurrentCellCode();
    if (!code) {
      this._addMessage({
        role: 'assistant',
        content: '⚠️ 개선할 코드가 없습니다. 노트북 셀을 선택해주세요.',
        timestamp: new Date()
      });
      return;
    }

    this._improveButton.disabled = true;

    try {
      const response = await fetch('/api/llm/improve-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this._getAuthToken()}`
        },
        body: JSON.stringify({
          code: code,
          file_type: 'python',
          provider: this._currentProvider,
          model: this._currentModel || undefined
        })
      });

      if (response.ok) {
        const data = await response.json();
        this._addMessage({
          role: 'assistant',
          content: `🔧 **코드 개선 제안:**\n\n${data.improvement}`,
          timestamp: new Date()
        });
      } else {
        throw new Error('Failed to improve code');
      }
    } catch (error) {
      console.error('Failed to improve code:', error);
      this._addMessage({
        role: 'assistant',
        content: '⚠️ 코드 개선에 실패했습니다.',
        timestamp: new Date()
      });
    } finally {
      this._improveButton.disabled = false;
    }
  }

  /**
   * 현재 활성 셀의 코드 가져오기
   */
  private _getCurrentCellCode(): string {
    try {
      // Jupyter Lab의 현재 활성 노트북에서 선택된 셀의 코드 가져오기
      const app = (window as any).jupyterapp;
      if (!app) return '';

      const shell = app.shell;
      const currentWidget = shell.currentWidget;
      
      if (currentWidget && currentWidget.content && currentWidget.content.activeCell) {
        const activeCell = currentWidget.content.activeCell;
        if (activeCell.model && activeCell.model.value) {
          return activeCell.model.value.text;
        }
      }
      
      return '';
    } catch (error) {
      console.error('Failed to get current cell code:', error);
      return '';
    }
  }

  /**
   * 인증 토큰 가져오기
   */
  private _getAuthToken(): string {
    // 실제 구현에서는 localStorage 또는 다른 방법으로 토큰을 가져와야 함
    return localStorage.getItem('token') || '';
  }

  /**
   * 위젯이 표시될 때 호출
   */
  protected onAfterShow(msg: Message): void {
    super.onAfterShow(msg);
    this._input.focus();
  }

  /**
   * 위젯 크기가 변경될 때 호출
   */
  protected onResize(msg: any): void {
    super.onResize(msg);
    this._messagesContainer.scrollTop = this._messagesContainer.scrollHeight;
  }
} 
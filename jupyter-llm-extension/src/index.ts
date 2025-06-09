import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';
import { ILauncher } from '@jupyterlab/launcher';

import { LLMChatWidget } from './chat-widget';

/**
 * LLM Chat 확장 플러그인
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter-llm-chat:plugin',
  description: 'LLM Chat Extension for Jupyter Lab',
  autoStart: true,
  requires: [ICommandPalette],
  optional: [ILauncher],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    launcher: ILauncher | null
  ) => {
    console.log('JupyterLab extension jupyter-llm-chat is activated!');

    const { commands, shell } = app;
    const command = 'llm-chat:open';
    let widget: LLMChatWidget | null = null;

    // 채팅 위젯 열기 명령어 추가
    commands.addCommand(command, {
      label: 'LLM Chat Assistant',
      caption: 'Open LLM Chat Assistant',
      icon: '🤖',
      execute: () => {
        if (!widget || widget.isDisposed) {
          widget = new LLMChatWidget();
          widget.id = 'llm-chat-widget';
          widget.title.label = 'LLM Chat';
          widget.title.icon = '🤖';
          widget.title.closable = true;
        }

        if (!widget.isAttached) {
          shell.add(widget, 'right', { rank: 1000 });
        }

        shell.activateById(widget.id);
      }
    });

    // 명령 팔레트에 추가
    palette.addItem({ command, category: 'AI Assistant' });

    // 런처에 추가 (있는 경우)
    if (launcher) {
      launcher.add({
        command,
        category: 'AI Assistant',
        rank: 1
      });
    }

    // Jupyter Lab 시작 시 자동으로 채팅 위젯 열기
    app.restored.then(() => {
      commands.execute(command);
    });
  }
};

export default plugin; 
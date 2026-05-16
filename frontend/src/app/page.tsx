'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import NavBar from '@/components/NavBar';
import Sidebar from '@/components/Sidebar';
import ChatStage from '@/components/ChatStage';
import Inspector from '@/components/Inspector';
import { streamChat, getSessions, getSession, deleteSession } from '@/lib/api';
import type { Message, ToolStep, Session, NavTab, BackendMessage } from '@/lib/types';

let _idCounter = 0;
function nanoidShort(): string {
  _idCounter++;
  return `${Date.now().toString(36)}-${_idCounter.toString(36)}-${Math.random().toString(36).slice(2, 6)}`;
}

function convertBackendMessages(backendMessages: BackendMessage[]): Message[] {
  const messages: Message[] = [];
  let i = 0;

  while (i < backendMessages.length) {
    const msg = backendMessages[i];

    if (msg.type === 'human') {
      messages.push({
        id: nanoidShort(),
        role: 'user',
        content: msg.content,
        steps: [],
      });
      i++;
      continue;
    }

    if (msg.type === 'ai') {
      const assistantMsg: Message = {
        id: nanoidShort(),
        role: 'assistant',
        content: '',
        steps: [],
      };

      const toolCallMap = new Map<string, ToolStep>();

      if (msg.tool_calls && msg.tool_calls.length > 0) {
        for (const tc of msg.tool_calls) {
          const step: ToolStep = {
            id: tc.id || nanoidShort(),
            name: tc.name,
            args: tc.args,
          };
          assistantMsg.steps.push(step);
          toolCallMap.set(tc.id, step);
        }

        i++;
        while (i < backendMessages.length && backendMessages[i].type === 'tool') {
          const toolMsg = backendMessages[i];
          const matchingStep = toolMsg.tool_call_id
            ? toolCallMap.get(toolMsg.tool_call_id)
            : assistantMsg.steps.find((s) => s.name === toolMsg.name && s.result === undefined);

          if (matchingStep) {
            matchingStep.result = toolMsg.content;
          }
          i++;
        }

        if (i < backendMessages.length && backendMessages[i].type === 'ai' && !backendMessages[i].tool_calls?.length) {
          assistantMsg.content = backendMessages[i].content;
          i++;
        }
      } else {
        assistantMsg.content = msg.content;
        i++;
      }

      messages.push(assistantMsg);
      continue;
    }

    i++;
  }

  return messages;
}

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<NavTab>('chat');
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [inspectorFile, setInspectorFile] = useState<string | null>(null);
  const inspectorKey = useRef(0);

  const refreshSessions = useCallback(async () => {
    try {
      const data = await getSessions();
      setSessions(data.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()));
    } catch {
    }
  }, []);

  useEffect(() => {
    refreshSessions();
  }, [refreshSessions]);

  const handleTabChange = useCallback((tab: NavTab) => {
    setActiveTab(tab);
    if (tab === 'memory') {
      inspectorKey.current++;
      setInspectorFile('workspace/MEMORY.md');
    } else if (tab === 'skills') {
      inspectorKey.current++;
      setInspectorFile('SKILLS_SNAPSHOT.md');
    }
  }, []);

  const handleSessionSelect = useCallback(async (sessionId: string) => {
    setActiveSessionId(sessionId);
    try {
      const backendMessages = await getSession(sessionId);
      const uiMessages = convertBackendMessages(backendMessages);
      setMessages(uiMessages);
    } catch {
      setMessages([]);
    }
  }, []);

  const handleNewSession = useCallback(() => {
    setActiveSessionId(null);
    setMessages([]);
    setInput('');
    setActiveTab('chat');
  }, []);

  const handleDeleteSession = useCallback(async (sessionId: string) => {
    try {
      await deleteSession(sessionId);
      if (activeSessionId === sessionId) {
        setActiveSessionId(null);
        setMessages([]);
      }
      await refreshSessions();
    } catch {
    }
  }, [activeSessionId, refreshSessions]);

  const handleSubmit = useCallback(async () => {
    const text = input.trim();
    if (!text || isStreaming) return;

    const userMessage: Message = {
      id: nanoidShort(),
      role: 'user',
      content: text,
      steps: [],
    };

    const assistantId = nanoidShort();
    const assistantMessage: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      steps: [],
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setInput('');
    setIsStreaming(true);

    try {
      await streamChat(text, activeSessionId, {
        onToken: (token) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: m.content + token } : m,
            ),
          );
        },
        onToolCall: (name, args) => {
          const step: ToolStep = {
            id: nanoidShort(),
            name,
            args,
          };
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, steps: [...m.steps, step] }
                : m,
            ),
          );
        },
        onToolResult: (name, resultContent) => {
          setMessages((prev) =>
            prev.map((m) => {
              if (m.id !== assistantId) return m;
              const steps = m.steps.map((s) => {
                if (s.name === name && s.result === undefined) {
                  return { ...s, result: resultContent };
                }
                return s;
              });
              return { ...m, steps };
            }),
          );
        },
        onDone: (_finalContent, sessionId) => {
          setActiveSessionId(sessionId);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, isStreaming: false } : m,
            ),
          );
          setIsStreaming(false);
          refreshSessions();
        },
        onError: (errMsg) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: `Error: ${errMsg}`, isStreaming: false }
                : m,
            ),
          );
          setIsStreaming(false);
        },
      });
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: `Error: ${err instanceof Error ? err.message : 'Unknown error'}`, isStreaming: false }
            : m,
        ),
      );
      setIsStreaming(false);
    }
  }, [input, isStreaming, activeSessionId, refreshSessions]);

  return (
    <div className="h-full flex flex-col">
      <NavBar />

      <div className="flex flex-1 overflow-hidden pt-14">
        <Sidebar
          activeTab={activeTab}
          onTabChange={handleTabChange}
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSessionSelect={handleSessionSelect}
          onNewSession={handleNewSession}
          onDeleteSession={handleDeleteSession}
        />

        <main className="flex-1 flex overflow-hidden bg-[#fafafa]/80">
          <ChatStage
            messages={messages}
            input={input}
            onInputChange={setInput}
            onSubmit={handleSubmit}
            isStreaming={isStreaming}
          />
        </main>

        <Inspector
          key={`${inspectorKey.current}-${inspectorFile}`}
          initialFile={inspectorFile}
        />
      </div>
    </div>
  );
}

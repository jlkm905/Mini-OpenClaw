'use client';

import { MessageSquare, Brain, Zap, Plus, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { NavTab, Session } from '@/lib/types';

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  sessions: Session[];
  activeSessionId: string | null;
  onSessionSelect: (sessionId: string) => void;
  onNewSession: () => void;
}

const tabs: Array<{ id: NavTab; label: string; icon: React.ReactNode }> = [
  { id: 'chat', label: 'Chat', icon: <MessageSquare className="w-4 h-4" /> },
  { id: 'memory', label: 'Memory', icon: <Brain className="w-4 h-4" /> },
  { id: 'skills', label: 'Skills', icon: <Zap className="w-4 h-4" /> },
];

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}

function getSessionLabel(session: Session): string {
  const parts = session.file_path.split('/');
  const filename = parts[parts.length - 1];
  return filename.replace('.json', '').replace('session_', 'Session ');
}

export default function Sidebar({
  activeTab,
  onTabChange,
  sessions,
  activeSessionId,
  onSessionSelect,
  onNewSession,
}: SidebarProps) {
  return (
    <aside className="w-[220px] flex-shrink-0 glass-panel border-r border-gray-200/60 flex flex-col overflow-hidden">
      <div className="flex border-b border-gray-200/60">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              'flex-1 flex flex-col items-center gap-1 py-3 text-xs font-medium transition-colors',
              activeTab === tab.id
                ? 'text-accent border-b-2 border-accent bg-blue-50/50'
                : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50/50',
            )}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      <div className="flex items-center justify-between px-3 py-2.5 border-b border-gray-200/40">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Sessions</span>
        <button
          onClick={onNewSession}
          className="flex items-center gap-1 text-xs text-accent hover:text-accent-light font-medium px-2 py-1 rounded-md hover:bg-blue-50 transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          New
        </button>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin py-1">
        {sessions.length === 0 ? (
          <div className="px-3 py-6 text-center">
            <p className="text-xs text-gray-400">No sessions yet</p>
            <p className="text-xs text-gray-400 mt-1">Start a conversation</p>
          </div>
        ) : (
          sessions.map((session) => (
            <button
              key={session.session_id}
              onClick={() => onSessionSelect(session.session_id)}
              className={cn(
                'w-full text-left px-3 py-2.5 rounded-lg mx-1 my-0.5 transition-colors',
                activeSessionId === session.session_id
                  ? 'bg-accent/10 text-accent'
                  : 'text-gray-700 hover:bg-gray-100/70',
              )}
              style={{ width: 'calc(100% - 8px)' }}
            >
              <div className="flex items-start justify-between gap-1">
                <span className="text-xs font-medium truncate leading-tight">
                  {getSessionLabel(session)}
                </span>
                <span className="text-[10px] text-gray-400 flex-shrink-0 flex items-center gap-0.5">
                  <Clock className="w-2.5 h-2.5" />
                  {formatRelativeTime(session.updated_at)}
                </span>
              </div>
              <div className="text-[10px] text-gray-400 mt-0.5">
                {session.message_count} message{session.message_count !== 1 ? 's' : ''}
              </div>
            </button>
          ))
        )}
      </div>
    </aside>
  );
}

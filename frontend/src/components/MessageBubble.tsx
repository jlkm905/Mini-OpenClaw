'use client';

import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Message } from '@/lib/types';
import ToolStepBlock from './ToolStepBlock';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end mb-3">
        <div className="max-w-[75%] bg-accent text-white rounded-2xl rounded-tr-sm px-4 py-2.5 shadow-sm">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-3">
      <div className="max-w-[85%] bg-white rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm border border-gray-100">
        {message.steps.length > 0 && (
          <div className="mb-2.5 space-y-0.5">
            {message.steps.map((step) => (
              <ToolStepBlock key={step.id} step={step} />
            ))}
          </div>
        )}

        {(message.content || message.isStreaming) && (
          <div className="flex items-start gap-2">
            <p className={cn(
              'text-sm leading-relaxed text-gray-800 whitespace-pre-wrap flex-1',
              !message.content && message.isStreaming && 'text-gray-400',
            )}>
              {message.content || (message.isStreaming ? '' : '')}
            </p>
            {message.isStreaming && !message.content && (
              <Loader2 className="w-4 h-4 text-gray-400 animate-spin mt-0.5 flex-shrink-0" />
            )}
          </div>
        )}

        {message.isStreaming && message.content && (
          <span className="inline-block w-1.5 h-4 bg-accent/70 rounded-sm animate-pulse ml-0.5 align-middle" />
        )}
      </div>
    </div>
  );
}

'use client';

import { useState } from 'react';
import { ChevronDown, ChevronRight, Wrench, CheckCircle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ToolStep } from '@/lib/types';

interface ToolStepBlockProps {
  step: ToolStep;
}

export default function ToolStepBlock({ step }: ToolStepBlockProps) {
  const [expanded, setExpanded] = useState(false);

  const hasResult = step.result !== undefined;
  const isPending = !hasResult;

  return (
    <div className="border-l-2 border-accent/70 pl-3 my-1.5 rounded-r-lg">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="flex items-center gap-2 w-full text-left group"
      >
        <span className="text-gray-400 flex-shrink-0">
          {expanded ? (
            <ChevronDown className="w-3.5 h-3.5" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5" />
          )}
        </span>
        <span className="flex items-center gap-1.5">
          {isPending ? (
            <Loader2 className="w-3.5 h-3.5 text-accent animate-spin" />
          ) : (
            <CheckCircle className="w-3.5 h-3.5 text-green-500" />
          )}
          <Wrench className="w-3 h-3 text-gray-400" />
        </span>
        <span className="text-xs font-mono font-medium text-accent">{step.name}</span>
        {isPending && (
          <span className="text-[10px] text-gray-400 italic">running…</span>
        )}
      </button>

      {expanded && (
        <div className="mt-2 space-y-1.5">
          <div>
            <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-1">
              Arguments
            </div>
            <pre className={cn(
              'text-[11px] font-mono bg-gray-50 rounded-md px-2.5 py-2 overflow-x-auto scrollbar-thin',
              'text-gray-700 border border-gray-100',
            )}>
              {JSON.stringify(step.args, null, 2)}
            </pre>
          </div>

          {hasResult && (
            <div>
              <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-1">
                Result
              </div>
              <pre className={cn(
                'text-[11px] font-mono bg-gray-50 rounded-md px-2.5 py-2 overflow-x-auto scrollbar-thin',
                'text-gray-700 border border-gray-100 whitespace-pre-wrap break-words',
              )}>
                {step.result}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

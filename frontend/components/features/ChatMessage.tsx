/**
 * Chat Message Component
 * Display single message in conversation
 */

import React from 'react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
}

export function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const isUser = role === 'user';

  return (
    <div className={cn('flex gap-3', isUser && 'flex-row-reverse')}>
      {/* Avatar */}
      <div
        className={cn(
          'h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-medium text-white',
          isUser ? 'bg-cyan-500' : 'bg-slate-400'
        )}
      >
        {isUser ? 'You' : 'AI'}
      </div>

      {/* Message bubble */}
      <div className={cn('flex max-w-xs flex-col gap-1', isUser && 'items-end')}>
        <div
          className={cn(
            'rounded-lg px-4 py-2.5 text-sm leading-relaxed break-words',
            isUser
              ? 'bg-cyan-500 text-white'
              : 'bg-slate-100 text-slate-900'
          )}
        >
          {content}
        </div>
        {timestamp && (
          <span className="text-xs text-slate-500">
            {format(timestamp, 'HH:mm')}
          </span>
        )}
      </div>
    </div>
  );
}

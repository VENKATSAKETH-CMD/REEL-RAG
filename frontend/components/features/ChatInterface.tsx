/**
 * Chat Interface Component
 * Two-way conversation with AI about video
 */

'use client';

import React, { useRef, useEffect, useState } from 'react';
import { Send, AlertCircle } from 'lucide-react';
import { useChatReel } from '@/lib/hooks/useReel';
import { ChatMessage } from '@/components/features/ChatMessage';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Spinner } from '@/components/ui/Button';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  reelId: number;
}

export function ChatInterface({ reelId }: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [error, setError] = useState('');

  const { mutate: sendMessage, isPending } = useChatReel(reelId);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim()) return;

    if (input.length > 2000) {
      setError('Message exceeds 2000 character limit');
      return;
    }

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setError('');

    // Send to backend
    sendMessage(input, {
      onSuccess: (data) => {
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.answer,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      },
      onError: (err: any) => {
        const errorMsg =
          err?.response?.data?.detail || 'Failed to get response. Please try again.';
        setError(errorMsg);
      },
    });
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-slate-200 overflow-hidden">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center text-center">
            <div>
              <p className="text-slate-500">No messages yet</p>
              <p className="text-xs text-slate-400 mt-1">Ask a question about this video</p>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <ChatMessage
              key={idx}
              role={msg.role}
              content={msg.content}
              timestamp={msg.timestamp}
            />
          ))
        )}

        {isPending && (
          <div className="flex gap-3">
            <div className="h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 bg-slate-400">
              <span className="text-xs font-medium text-white">AI</span>
            </div>
            <div className="bg-slate-100 text-slate-900 rounded-lg px-4 py-2.5 flex items-center gap-2">
              <Spinner size="sm" />
              <span className="text-sm">Thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-slate-200 p-4 flex flex-col gap-2">
        {error && (
          <div className="flex gap-2 rounded-lg bg-red-50 p-2 text-xs text-red-600 border border-red-200">
            <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            placeholder="Ask about this video..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isPending}
            maxLength={2000}
          />
          <Button
            type="submit"
            size="md"
            isLoading={isPending}
            disabled={!input.trim()}
            className="flex-shrink-0"
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
        <span className="text-xs text-slate-400">{input.length} / 2000</span>
      </div>
    </div>
  );
}

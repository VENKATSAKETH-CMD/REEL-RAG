/**
 * Reel Detail Page
 * Video player with chat interface
 */

'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { useReel, useReelStatus } from '@/lib/hooks/useReel';
import { VideoPlayer } from '@/components/features/VideoPlayer';
import { ChatInterface } from '@/components/features/ChatInterface';
import { Button, Spinner } from '@/components/ui/Button';

export default function ReelDetailPage() {
  const params = useParams();
  const router = useRouter();
  const reelId = parseInt(params.id as string);

  const { data: reel, isLoading } = useReel(reelId);
  const { data: status } = useReelStatus(reelId);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!reel) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50">
        <p className="text-slate-600">Reel not found</p>
        <Button onClick={() => router.back()}>Go Back</Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur-md">
        <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8">
          <Button variant="ghost" size="sm" onClick={() => router.back()} className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Video section */}
          <div className="lg:col-span-2">
            <div className="space-y-4">
              <div>
                <h1 className="text-2xl font-bold text-slate-900">{reel.title || 'Untitled'}</h1>
                <p className="text-sm text-slate-500">
                  Status:{' '}
                  <span className={`font-medium ${
                    status === 'ready' ? 'text-green-600' :
                    status === 'processing' ? 'text-blue-600' :
                    status === 'failed' ? 'text-red-600' : 'text-yellow-600'
                  }`}>
                    {status || reel.status}
                  </span>
                </p>
              </div>

              {status === 'ready' && reel.video_url ? (
                <VideoPlayer src={reel.video_url} title={reel.title || undefined} />
              ) : (
                <div className="flex h-96 items-center justify-center rounded-lg bg-slate-200">
                  <div className="text-center">
                    <Spinner size="lg" />
                    <p className="mt-4 text-slate-600">
                      {status === 'processing' ? 'Video is processing...' : 'Video is not ready yet'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Chat section */}
          <div className="h-full lg:col-span-1">
            {status === 'ready' ? (
              <ChatInterface reelId={reelId} />
            ) : (
              <div className="flex h-96 items-center justify-center rounded-lg border border-slate-200 bg-white">
                <div className="text-center">
                  <p className="text-sm text-slate-600">
                    Chat will be available once video processing is complete
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

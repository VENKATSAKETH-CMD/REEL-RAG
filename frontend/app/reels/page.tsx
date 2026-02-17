/**
 * Reels List Page
 * Browse and manage user's reels
 */

'use client';

import React from 'react';
import { useReels } from '@/lib/hooks/useReel';
import { useLogout } from '@/lib/hooks/useAuth';
import { UploadZone } from '@/components/features/UploadZone';
import { ReelCard } from '@/components/features/ReelCard';
import { Button } from '@/components/ui/Button';
import { SkeletonReelGrid } from '@/components/ui/Skeleton';
import { LogOut } from 'lucide-react';

export default function ReelsPage() {
  const { data: reels, isLoading, refetch } = useReels();
  const logout = useLogout();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur-md">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-slate-900">My Reels</h1>
            <Button variant="ghost" size="sm" onClick={logout} className="gap-2">
              <LogOut className="h-4 w-4" />
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Upload section */}
        <div className="mb-12">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">Upload New Video</h2>
          <UploadZone onSuccess={() => refetch()} />
        </div>

        {/* Reels grid */}
        <div>
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            Your Videos {reels && `(${reels.length})`}
          </h2>

        {isLoading ? (
          <SkeletonReelGrid count={8} />
        ) : reels && reels.length > 0 ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {reels.map((reel) => (
                <ReelCard key={reel.id} reel={reel} />
              ))}
            </div>
          ) : (
            <div className="rounded-lg border-2 border-dashed border-slate-300 p-12 text-center">
              <p className="text-slate-500">No videos yet. Upload one to get started!</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

'use client';

import { useEffect } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function ReelsError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('[Reels Error Boundary]', error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 p-4">
      <div className="max-w-md w-full bg-white rounded-lg border border-slate-200 shadow-lg p-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-100">
            <AlertCircle className="h-6 w-6 text-red-600" />
          </div>
          <h1 className="text-xl font-bold text-slate-900">Reels Error</h1>
        </div>

        <div className="mb-6">
          <p className="text-sm text-slate-600 mb-4">
            Failed to load your reels. Please try refreshing or return home.
          </p>

          {error.message && (
            <div className="bg-slate-50 rounded-lg p-3 mb-4 border border-slate-200">
              <p className="text-xs font-mono text-slate-700 break-words">
                {error.message}
              </p>
            </div>
          )}

          {error.digest && (
            <div className="text-xs text-slate-500">
              Error ID: <span className="font-mono">{error.digest}</span>
            </div>
          )}
        </div>

        <div className="flex gap-3">
          <Button
            onClick={() => reset()}
            className="flex-1 flex items-center justify-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Retry
          </Button>
          <Button
            variant="outline"
            onClick={() => (window.location.href = '/')}
            className="flex-1"
          >
            Home
          </Button>
        </div>
      </div>
    </div>
  );
}

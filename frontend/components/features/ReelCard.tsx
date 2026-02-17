/**
 * Reel Card Component
 * Display reel preview with status
 */

import React from 'react';
import Link from 'next/link';
import { format } from 'date-fns';
import { Play, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { Reel } from '@/lib/reel-store';
import { Card } from '@/components/ui/Card';
import { cn } from '@/lib/utils';

interface ReelCardProps {
  reel: Reel;
}

export function ReelCard({ reel }: ReelCardProps) {
  const statusConfig = {
    uploaded: { icon: Clock, color: 'bg-yellow-100 text-yellow-700', label: 'Uploading...' },
    processing: { icon: Clock, color: 'bg-blue-100 text-blue-700', label: 'Processing...' },
    ready: { icon: CheckCircle, color: 'bg-green-100 text-green-700', label: 'Ready' },
    failed: { icon: AlertCircle, color: 'bg-red-100 text-red-700', label: 'Failed' },
  };

  const config = statusConfig[reel.status];
  const StatusIcon = config.icon;

  return (
    <Link href={`/reels/${reel.id}`}>
      <Card hoverable className="group overflow-hidden">
        {/* Thumbnail placeholder */}
        <div className="relative aspect-video w-full bg-gradient-to-br from-slate-200 to-slate-300 overflow-hidden mb-3">
          {reel.video_url ? (
            <img
              src={reel.video_url}
              alt={reel.title || 'Reel'}
              className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="flex h-full items-center justify-center">
              <Play className="h-12 w-12 text-slate-400" />
            </div>
          )}

          {/* Status badge */}
          <div className={cn('absolute top-2 right-2 rounded-full px-2 py-1 text-xs font-medium flex items-center gap-1', config.color)}>
            <StatusIcon className="h-3 w-3" />
            {config.label}
          </div>
        </div>

        {/* Title and meta */}
        <div className="flex flex-col gap-2">
          <h3 className="font-medium text-slate-900 line-clamp-2 group-hover:text-cyan-600 transition-colors">
            {reel.title || 'Untitled Video'}
          </h3>
          <p className="text-xs text-slate-500">
            {format(new Date(reel.created_at), 'MMM d, yyyy')}
          </p>
        </div>
      </Card>
    </Link>
  );
}

/**
 * Skeleton Loader Component
 * Placeholder for loading states
 */

import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'default' | 'card' | 'text' | 'avatar' | 'image';
}

export function Skeleton({ className, variant = 'default' }: SkeletonProps) {
  const baseClass = 'animate-pulse rounded bg-slate-200';

  const variantClass = {
    default: 'h-12 w-12',
    card: 'h-48 w-full rounded-lg',
    text: 'h-4 w-full',
    avatar: 'h-10 w-10 rounded-full',
    image: 'aspect-video w-full',
  }[variant];

  return <div className={cn(baseClass, variantClass, className)} />;
}

export function SkeletonReelCard() {
  return (
    <div className="space-y-3">
      <Skeleton variant="image" />
      <Skeleton variant="text" />
      <Skeleton variant="text" className="w-3/4" />
      <div className="flex gap-2">
        <Skeleton className="h-2 flex-1" />
        <Skeleton className="h-2 w-1/4" />
      </div>
    </div>
  );
}

export function SkeletonReelGrid({ count = 12 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonReelCard key={i} />
      ))}
    </div>
  );
}

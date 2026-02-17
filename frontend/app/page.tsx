/**
 * Home Page
 * Landing page - redirects authenticated users to /reels
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth-store';

export default function HomePage() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/reels');
    } else {
      router.push('/auth/login');
    }
  }, [isAuthenticated, router]);

  return null;
}

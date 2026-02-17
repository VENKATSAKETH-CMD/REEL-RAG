/**
 * Reel Data Hooks
 * Upload, list, fetch, and chat operations
 */

'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useReelStore } from '@/lib/reel-store';
import { useAuthStore } from '@/lib/auth-store';
import { apiClient } from '@/lib/api';

export function useReels() {
  const { setReels } = useReelStore();
  const { user } = useAuthStore();

  return useQuery({
    queryKey: ['reels'],
    queryFn: async () => {
      const response = await apiClient.listReels();
      // Backend returns array directly, not { reels: [...] }
      const allReels = Array.isArray(response) ? response : (response.reels || []);
      // Filter to show only current user's reels
      const userReels = user ? allReels.filter(reel => reel.user_id === user.id) : allReels;
      setReels(userReels);
      return userReels;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useReel(reelId: number) {
  const { setCurrentReel } = useReelStore();

  return useQuery({
    queryKey: ['reel', reelId],
    queryFn: async () => {
      const response = await apiClient.getReel(reelId);
      setCurrentReel(response);
      return response;
    },
    enabled: !!reelId,
  });
}

export function useUploadReel() {
  const { addReel, setIsUploading, setUploadProgress, clearUpload } = useReelStore();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { file: File; title: string }) => {
      setIsUploading(true);
      setUploadProgress(0);

      // Simulate progress for now (backend doesn't support progress tracking)
      const interval = setInterval(() => {
        setUploadProgress((p) => Math.min(p + 10, 90));
      }, 200);

      try {
        const response = await apiClient.uploadReel(data.file, data.title);
        clearInterval(interval);
        setUploadProgress(100);
        return response;
      } catch (error) {
        clearInterval(interval);
        throw error;
      }
    },
    onSuccess: (data) => {
      addReel(data);
      clearUpload();
      // Invalidate the reels list query so it refetches with the new video
      queryClient?.invalidateQueries({ queryKey: ['reels'] });
    },
    onError: () => {
      clearUpload();
    },
  });
}

export function useChatReel(reelId: number) {
  return useMutation({
    mutationFn: async (message: string) => {
      if (message.length > 2000) {
        throw new Error('Message exceeds 2000 character limit');
      }
      const response = await apiClient.chatReel(reelId, message);
      return response;
    },
  });
}

export function useReelStatus(reelId: number) {
  return useQuery({
    queryKey: ['reel-status', reelId],
    queryFn: async () => {
      const response = await apiClient.getReel(reelId);
      return response.status;
    },
    refetchInterval: response => 
      response?.status === 'processing' ? 2000 : false, // Poll every 2s while processing
    enabled: !!reelId,
  });
}

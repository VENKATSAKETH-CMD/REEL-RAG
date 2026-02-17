/**
 * Reel Store (Zustand)
 * Manages reel state and uploads
 */

import { create } from 'zustand';

export interface Reel {
  id: number;
  user_id: number;
  video_url: string;
  title: string | null;
  status: 'uploaded' | 'processing' | 'ready' | 'failed';
  created_at: string;
}

interface ReelStore {
  reels: Reel[];
  currentReel: Reel | null;
  uploadProgress: number;
  isUploading: boolean;

  setReels: (reels: Reel[]) => void;
  addReel: (reel: Reel) => void;
  setCurrentReel: (reel: Reel | null) => void;
  updateReel: (reelId: number, updates: Partial<Reel>) => void;
  setUploadProgress: (progress: number) => void;
  setIsUploading: (uploading: boolean) => void;
  clearUpload: () => void;
}

export const useReelStore = create<ReelStore>((set) => ({
  reels: [],
  currentReel: null,
  uploadProgress: 0,
  isUploading: false,

  setReels: (reels) => set({ reels }),
  addReel: (reel) => set((state) => ({ reels: [reel, ...state.reels] })),
  setCurrentReel: (reel) => set({ currentReel: reel }),
  updateReel: (reelId, updates) =>
    set((state) => ({
      reels: state.reels.map((r) => (r.id === reelId ? { ...r, ...updates } : r)),
      currentReel: state.currentReel?.id === reelId ? { ...state.currentReel, ...updates } : state.currentReel,
    })),
  setUploadProgress: (progress) => set({ uploadProgress: progress }),
  setIsUploading: (uploading) => set({ isUploading: uploading }),
  clearUpload: () => set({ uploadProgress: 0, isUploading: false }),
}));

/**
 * Upload Zone Component
 * Drag-and-drop file upload with progress
 */

'use client';

import React, { useRef, useState } from 'react';
import { Upload } from 'lucide-react';
import { useUploadReel } from '@/lib/hooks/useReel';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { cn } from '@/lib/utils';

interface UploadZoneProps {
  onSuccess?: () => void;
}

export function UploadZone({ onSuccess }: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');

  const { mutate: upload, isPending, progress } = useUploadReel();

  const validateFile = (file: File): boolean => {
    const validTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska'];
    const maxSize = 100 * 1024 * 1024; // 100MB

    if (!validTypes.includes(file.type)) {
      setError('Please upload a valid video file (MP4, MOV, AVI, MKV)');
      return false;
    }

    if (file.size > maxSize) {
      setError('File size exceeds 100MB limit');
      return false;
    }

    setError('');
    return true;
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0 && validateFile(files[0])) {
      setSelectedFile(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0] && validateFile(e.target.files[0])) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = () => {
    if (!selectedFile || !title.trim()) {
      setError('Please select a file and enter a title');
      return;
    }

    upload(
      { file: selectedFile, title },
      {
        onSuccess: () => {
          setSelectedFile(null);
          setTitle('');
          onSuccess?.();
        },
        onError: (err: any) => {
          setError(err?.response?.data?.detail || 'Upload failed. Please try again.');
        },
      }
    );
  };

  return (
    <Card className="border-2 border-dashed">
      <div
        className={cn(
          'flex flex-col items-center justify-center gap-4 p-8 text-center transition-colors',
          isDragging && 'bg-cyan-50',
          isPending && 'opacity-75'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {!selectedFile ? (
          <>
            <Upload className="h-12 w-12 text-slate-400" />
            <div>
              <p className="font-medium text-slate-900">Drag and drop your video here</p>
              <p className="text-sm text-slate-500">or click to browse (max 100MB)</p>
            </div>
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="text-cyan-500 hover:text-cyan-600 font-medium"
              disabled={isPending}
            >
              Browse files
            </button>
            <input
              ref={inputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              className="hidden"
              disabled={isPending}
            />
          </>
        ) : (
          <>
            <div className="flex w-full flex-col gap-3">
              <div className="rounded-lg bg-slate-50 p-3">
                <p className="text-sm font-medium text-slate-900 truncate">{selectedFile.name}</p>
                <p className="text-xs text-slate-500 mt-1">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>

              <Input
                label="Video Title"
                placeholder="Enter a title for your video"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={isPending}
              />

              {isPending && (
                <div className="flex flex-col gap-2">
                  <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-cyan-500 transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-slate-600 text-center">{progress}% uploaded</p>
                </div>
              )}

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setSelectedFile(null);
                    setTitle('');
                  }}
                  disabled={isPending}
                  fullWidth
                >
                  Clear
                </Button>
                <Button onClick={handleUpload} isLoading={isPending} fullWidth>
                  Upload
                </Button>
              </div>
            </div>
          </>
        )}

        {error && (
          <div className="w-full rounded-lg bg-red-50 p-3 text-sm text-red-600 border border-red-200">
            {error}
          </div>
        )}
      </div>
    </Card>
  );
}

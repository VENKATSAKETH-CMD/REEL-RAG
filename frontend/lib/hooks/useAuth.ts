/**
 * Authentication Hooks
 * Login, register, and auth state management
 */

'use client';

import { useMutation, useQuery } from '@tanstack/react-query';
import { useAuthStore } from '@/lib/auth-store';
import { apiClient } from '@/lib/api';

export function useLogin() {
  const { setUser, setToken } = useAuthStore();

  return useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      const response = await apiClient.login(credentials.email, credentials.password);
      return response;
    },
    onSuccess: (data) => {
      apiClient.setToken(data.access_token);
      setToken(data.access_token);
      setUser({ id: data.user.id, email: data.user.email });
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      const response = await apiClient.register(credentials.email, credentials.password);
      return response;
    },
  });
}

export function useLogout() {
  const { logout } = useAuthStore();

  return () => {
    logout();
    apiClient.setToken('');
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
      window.location.href = '/auth/login';
    }
  };
}

export function useAuthStatus() {
  const { token, isAuthenticated, hydrateFromStorage } = useAuthStore();

  return useQuery({
    queryKey: ['auth-status'],
    queryFn: async () => {
      hydrateFromStorage();
      return !!token;
    },
    staleTime: Infinity,
    retry: false,
  });
}

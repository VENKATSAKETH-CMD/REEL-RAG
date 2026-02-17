/**
 * API Client Configuration
 * Type-safe axios instance for backend communication
 */

import axios, { AxiosError, AxiosInstance } from 'axios';

export interface ApiErrorResponse {
  detail: string | string[];
  status?: number;
}

export class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor for adding auth token
    this.client.interceptors.request.use((config) => {
      const token = this.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Interceptor for handling errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiErrorResponse>) => {
        if (error.response?.status === 401) {
          this.clearToken();
          window.location.href = '/auth/login';
        }
        return Promise.reject(error);
      }
    );
  }

  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  private clearToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  // Auth endpoints
  async register(email: string, password: string) {
    console.log('[API] Register request:', { email, baseURL: this.baseURL });
    try {
      const { data } = await this.client.post('/auth/register', { email, password });
      console.log('[API] Register success:', data);
      return data;
    } catch (error: any) {
      console.error('[API] Register error:', {
        status: error?.response?.status,
        statusText: error?.response?.statusText,
        data: error?.response?.data,
        message: error?.message,
        url: error?.config?.url,
      });
      throw error;
    }
  }

  async login(email: string, password: string) {
    const { data } = await this.client.post('/auth/login', new URLSearchParams({
      username: email,
      password,
    }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return data;
  }

  // Reel endpoints
  async uploadReel(file: File, title: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);

    const { data } = await this.client.post('/reels', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  }

  async listReels(page: number = 1, perPage: number = 20) {
    const { data } = await this.client.get('/reels', {
      params: { page, per_page: perPage },
    });
    return data;
  }

  async getReel(reelId: number) {
    const { data } = await this.client.get(`/reels/${reelId}`);
    return data;
  }

  // Chat endpoint
  async chatReel(reelId: number, message: string) {
    const token = this.getToken();
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
    const { data } = await this.client.post(`/reels/${reelId}/chat`, {
      message,
    }, config);
    return data;
  }

  // Health check
  async healthCheck() {
    const { data } = await this.client.get('/health');
    return data;
  }
}

export const apiClient = new ApiClient();

import apiClient from '@/lib/api-client';
import type { AIProvider, AIProviderMetrics } from '@/types';

export const aiProviderService = {
  async getProviders(): Promise<AIProvider[]> {
    const response = await apiClient.get<AIProvider[]>('/api/v1/admin/providers');
    return response.data;
  },

  async getProvider(id: string): Promise<AIProvider> {
    const response = await apiClient.get<AIProvider>(`/api/v1/admin/providers/${id}`);
    return response.data;
  },

  async getProviderMetrics(
    id: string,
    params?: {
      start_date?: string;
      end_date?: string;
      granularity?: 'hour' | 'day' | 'week' | 'month';
    }
  ): Promise<AIProviderMetrics[]> {
    const response = await apiClient.get<AIProviderMetrics[]>(
      `/api/v1/admin/providers/${id}/metrics`,
      { params }
    );
    return response.data;
  },

  async getProviderHealth(id: string): Promise<{
    status: string;
    latency_ms: number;
    error_rate: number;
    uptime: number;
  }> {
    const response = await apiClient.get(
      `/api/v1/admin/providers/${id}/health`
    );
    return response.data;
  },

  async toggleProvider(id: string, enabled: boolean): Promise<AIProvider> {
    const response = await apiClient.post<AIProvider>(
      `/api/v1/admin/providers/${id}/toggle`,
      { enabled }
    );
    return response.data;
  },

  async testProvider(id: string): Promise<{ success: boolean; latency_ms: number; error?: string }> {
    const response = await apiClient.post(
      `/api/v1/admin/providers/${id}/test`
    );
    return response.data;
  },
};

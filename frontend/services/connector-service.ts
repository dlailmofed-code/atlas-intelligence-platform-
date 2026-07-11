import apiClient from '@/lib/api-client';
import type { Connector, ConnectorLog } from '@/types';

export const connectorService = {
  async getConnectors(): Promise<Connector[]> {
    const response = await apiClient.get<Connector[]>('/api/v1/admin/connectors');
    return response.data;
  },

  async getConnector(id: string): Promise<Connector> {
    const response = await apiClient.get<Connector>(`/api/v1/admin/connectors/${id}`);
    return response.data;
  },

  async getConnectorLogs(
    id: string,
    params?: {
      page?: number;
      page_size?: number;
      level?: 'info' | 'warning' | 'error';
    }
  ): Promise<{ items: ConnectorLog[]; total: number }> {
    const response = await apiClient.get(`/api/v1/admin/connectors/${id}/logs`, { params });
    return response.data;
  },

  async syncConnector(id: string): Promise<{ message: string; job_id: string }> {
    const response = await apiClient.post<{ message: string; job_id: string }>(
      `/api/v1/admin/connectors/${id}/sync`
    );
    return response.data;
  },

  async toggleConnector(id: string, enabled: boolean): Promise<Connector> {
    const response = await apiClient.post<Connector>(
      `/api/v1/admin/connectors/${id}/toggle`,
      { enabled }
    );
    return response.data;
  },

  async updateConnectorConfig(
    id: string,
    config: Record<string, unknown>
  ): Promise<Connector> {
    const response = await apiClient.patch<Connector>(
      `/api/v1/admin/connectors/${id}`,
      { config }
    );
    return response.data;
  },

  async testConnector(id: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post<{ success: boolean; message: string }>(
      `/api/v1/admin/connectors/${id}/test`
    );
    return response.data;
  },
};

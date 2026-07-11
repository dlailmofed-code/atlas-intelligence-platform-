import apiClient from '@/lib/api-client';
import type {
  Report,
  ReportListResponse,
  ReportTemplate,
  ReportSchedule,
} from '@/types';

export interface CreateReportRequest {
  title: string;
  description: string;
  type: string;
  config?: Record<string, unknown>;
}

export interface GenerateReportRequest {
  type: string;
  filters?: Record<string, unknown>;
}

export const reportService = {
  async getReports(params?: {
    page?: number;
    page_size?: number;
    type?: string;
    status?: string;
  }): Promise<ReportListResponse> {
    const response = await apiClient.get<ReportListResponse>('/api/v1/reports/', { params });
    return response.data;
  },

  async getReport(id: string): Promise<Report> {
    const response = await apiClient.get<Report>(`/api/v1/reports/${id}`);
    return response.data;
  },

  async createReport(data: CreateReportRequest): Promise<Report> {
    const response = await apiClient.post<Report>('/api/v1/reports/', data);
    return response.data;
  },

  async updateReport(id: string, data: Partial<CreateReportRequest>): Promise<Report> {
    const response = await apiClient.patch<Report>(`/api/v1/reports/${id}`, data);
    return response.data;
  },

  async deleteReport(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`/api/v1/reports/${id}`);
    return response.data;
  },

  async generateReport(data: GenerateReportRequest): Promise<Report> {
    const response = await apiClient.post<Report>('/api/v1/reports/generate', data);
    return response.data;
  },

  async exportReport(
    id: string,
    format: 'pdf' | 'html' | 'docx' | 'xlsx' | 'json' | 'csv'
  ): Promise<Blob> {
    const response = await apiClient.get(`/api/v1/reports/${id}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },

  async getTemplates(): Promise<ReportTemplate[]> {
    const response = await apiClient.get<ReportTemplate[]>('/api/v1/reports/templates');
    return response.data;
  },

  async getSchedules(): Promise<ReportSchedule[]> {
    const response = await apiClient.get<ReportSchedule[]>('/api/v1/reports/schedules');
    return response.data;
  },

  async createSchedule(
    reportId: string,
    cronExpression: string,
    enabled: boolean = true
  ): Promise<ReportSchedule> {
    const response = await apiClient.post<ReportSchedule>('/api/v1/reports/schedules', {
      report_id: reportId,
      cron_expression: cronExpression,
      enabled,
    });
    return response.data;
  },

  async updateSchedule(
    id: string,
    data: Partial<{ cron_expression: string; enabled: boolean }>
  ): Promise<ReportSchedule> {
    const response = await apiClient.patch<ReportSchedule>(
      `/api/v1/reports/schedules/${id}`,
      data
    );
    return response.data;
  },

  async deleteSchedule(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(
      `/api/v1/reports/schedules/${id}`
    );
    return response.data;
  },
};

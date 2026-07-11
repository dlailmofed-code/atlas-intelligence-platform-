import apiClient from '@/lib/api-client';
import type {
  IntelligenceSignal,
  Pattern,
  CausalLink,
  IntelligenceIndicator,
  IntelligenceDashboard,
  SignalFilters,
} from '@/types';

export interface GetSignalsParams {
  page?: number;
  page_size?: number;
  filters?: SignalFilters;
}

export interface GetDashboardParams {
  timeRange?: string;
}

export const intelligenceService = {
  async getSignals(params: GetSignalsParams = {}): Promise<{
    items: IntelligenceSignal[];
    total: number;
    page: number;
    page_size: number;
    has_next: boolean;
  }> {
    const { page = 1, page_size = 20, filters = {} } = params;
    
    const queryParams = new URLSearchParams({
      page: page.toString(),
      page_size: page_size.toString(),
    });
    
    if (filters.type) queryParams.append('type', filters.type);
    if (filters.category) queryParams.append('category', filters.category);
    if (filters.region) queryParams.append('region', filters.region);
    if (filters.industry) queryParams.append('industry', filters.industry);
    if (filters.min_intensity !== undefined) queryParams.append('min_intensity', filters.min_intensity.toString());
    if (filters.min_confidence !== undefined) queryParams.append('min_confidence', filters.min_confidence.toString());
    
    const response = await apiClient.get<{
      items: IntelligenceSignal[];
      total: number;
      page: number;
      page_size: number;
      has_next: boolean;
    }>(`/api/v1/intelligence/signals/?${queryParams.toString()}`);
    return response.data;
  },

  async getSignal(id: string): Promise<IntelligenceSignal> {
    const response = await apiClient.get<IntelligenceSignal>(`/api/v1/intelligence/signals/${id}`);
    return response.data;
  },

  async getPatterns(params: GetSignalsParams = {}): Promise<{
    items: Pattern[];
    total: number;
    page: number;
    page_size: number;
    has_next: boolean;
  }> {
    const { page = 1, page_size = 20 } = params;
    
    const response = await apiClient.get<{
      items: Pattern[];
      total: number;
      page: number;
      page_size: number;
      has_next: boolean;
    }>(`/api/v1/intelligence/patterns/?page=${page}&page_size=${page_size}`);
    return response.data;
  },

  async getCausalLinks(params: GetSignalsParams = {}): Promise<{
    items: CausalLink[];
    total: number;
    page: number;
    page_size: number;
    has_next: boolean;
  }> {
    const { page = 1, page_size = 20 } = params;
    
    const response = await apiClient.get<{
      items: CausalLink[];
      total: number;
      page: number;
      page_size: number;
      has_next: boolean;
    }>(`/api/v1/intelligence/causal-links/?page=${page}&page_size=${page_size}`);
    return response.data;
  },

  async getIndicators(params: GetDashboardParams = {}): Promise<IntelligenceIndicator[]> {
    const { timeRange = '30d' } = params;
    const response = await apiClient.get<IntelligenceIndicator[]>(
      `/api/v1/intelligence/indicators/?time_range=${timeRange}`
    );
    return response.data;
  },

  async getDashboard(params: GetDashboardParams = {}): Promise<IntelligenceDashboard> {
    const { timeRange = '30d' } = params;
    const response = await apiClient.get<IntelligenceDashboard>(
      `/api/v1/intelligence/dashboard/?time_range=${timeRange}`
    );
    return response.data;
  },

  async processIntelligence(data: {
    content?: string;
    source_type?: string;
  }): Promise<{
    signals: IntelligenceSignal[];
    patterns: Pattern[];
    opportunities: string[];
  }> {
    const response = await apiClient.post<{
      signals: IntelligenceSignal[];
      patterns: Pattern[];
      opportunities: string[];
    }>('/api/v1/intelligence/process', data);
    return response.data;
  },
};

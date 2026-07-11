import apiClient from '@/lib/api-client';
import type {
  Opportunity,
  OpportunityListResponse,
  OpportunityFilters,
} from '@/types';

export interface GetOpportunitiesParams {
  page?: number;
  page_size?: number;
  filters?: OpportunityFilters;
}

export const opportunityService = {
  async getOpportunities(
    params: GetOpportunitiesParams = {}
  ): Promise<OpportunityListResponse> {
    const { page = 1, page_size = 20, filters = {} } = params;
    
    const queryParams = new URLSearchParams({
      page: page.toString(),
      page_size: page_size.toString(),
    });
    
    if (filters.category) queryParams.append('category', filters.category);
    if (filters.industry) queryParams.append('industry', filters.industry);
    if (filters.region) queryParams.append('region', filters.region);
    if (filters.min_score !== undefined) queryParams.append('min_score', filters.min_score.toString());
    if (filters.max_score !== undefined) queryParams.append('max_score', filters.max_score.toString());
    if (filters.is_bookmarked !== undefined) queryParams.append('is_bookmarked', String(filters.is_bookmarked));
    
    const response = await apiClient.get<OpportunityListResponse>(
      `/api/v1/opportunities/?${queryParams.toString()}`
    );
    return response.data;
  },

  async getOpportunity(id: string): Promise<Opportunity> {
    const response = await apiClient.get<Opportunity>(`/api/v1/opportunities/${id}`);
    return response.data;
  },

  async getFeaturedOpportunities(limit: number = 5): Promise<Opportunity[]> {
    const response = await apiClient.get<OpportunityListResponse>(
      `/api/v1/opportunities/?page_size=${limit}&featured=true`
    );
    return response.data.items;
  },

  async getMyBookmarks(page: number = 1, pageSize: number = 20): Promise<OpportunityListResponse> {
    const response = await apiClient.get<OpportunityListResponse>(
      `/api/v1/opportunities/?page=${page}&page_size=${pageSize}&bookmarked=true`
    );
    return response.data;
  },

  async bookmarkOpportunity(id: string): Promise<void> {
    await apiClient.post(`/api/v1/opportunities/${id}/bookmark`);
  },

  async unbookmarkOpportunity(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/opportunities/${id}/bookmark`);
  },
};

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { opportunityService, GetOpportunitiesParams } from '@/services/opportunity-service';
import type { OpportunityFilters } from '@/types';

export function useOpportunities(params: GetOpportunitiesParams = {}) {
  return useQuery({
    queryKey: ['opportunities', params],
    queryFn: () => opportunityService.getOpportunities(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useOpportunity(id: string | undefined) {
  return useQuery({
    queryKey: ['opportunity', id],
    queryFn: () => opportunityService.getOpportunity(id!),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useFeaturedOpportunities(limit: number = 5) {
  return useQuery({
    queryKey: ['opportunities', 'featured', limit],
    queryFn: () => opportunityService.getFeaturedOpportunities(limit),
    staleTime: 5 * 60 * 1000,
  });
}

export function useBookmarks(page: number = 1, pageSize: number = 20) {
  return useQuery({
    queryKey: ['opportunities', 'bookmarks', page, pageSize],
    queryFn: () => opportunityService.getMyBookmarks(page, pageSize),
    staleTime: 5 * 60 * 1000,
  });
}

export function useBookmarkOpportunity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => opportunityService.bookmarkOpportunity(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
    },
  });
}

export function useUnbookmarkOpportunity() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => opportunityService.unbookmarkOpportunity(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
    },
  });
}

export function useOpportunityFilters() {
  const [filters, setFilters] = React.useState<OpportunityFilters>({});
  const [page, setPage] = React.useState(1);

  const updateFilters = (newFilters: Partial<OpportunityFilters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
    setPage(1);
  };

  const resetFilters = () => {
    setFilters({});
    setPage(1);
  };

  return {
    filters,
    page,
    setPage,
    updateFilters,
    resetFilters,
  };
}

// Need to import React for useState
import React from 'react';

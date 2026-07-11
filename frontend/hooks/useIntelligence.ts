'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { intelligenceService, GetSignalsParams, GetDashboardParams } from '@/services/intelligence-service';

export function useSignals(params: GetSignalsParams = {}) {
  return useQuery({
    queryKey: ['signals', params],
    queryFn: () => intelligenceService.getSignals(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useSignal(id: string | undefined) {
  return useQuery({
    queryKey: ['signal', id],
    queryFn: () => intelligenceService.getSignal(id!),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function usePatterns(params: GetSignalsParams = {}) {
  return useQuery({
    queryKey: ['patterns', params],
    queryFn: () => intelligenceService.getPatterns(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCausalLinks(params: GetSignalsParams = {}) {
  return useQuery({
    queryKey: ['causal-links', params],
    queryFn: () => intelligenceService.getCausalLinks(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useIndicators(params: GetDashboardParams = {}) {
  return useQuery({
    queryKey: ['indicators', params],
    queryFn: () => intelligenceService.getIndicators(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useIntelligenceDashboard(params: GetDashboardParams = {}) {
  return useQuery({
    queryKey: ['intelligence-dashboard', params],
    queryFn: () => intelligenceService.getDashboard(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useProcessIntelligence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { content?: string; source_type?: string }) =>
      intelligenceService.processIntelligence(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['signals'] });
      queryClient.invalidateQueries({ queryKey: ['patterns'] });
      queryClient.invalidateQueries({ queryKey: ['opportunities'] });
    },
  });
}

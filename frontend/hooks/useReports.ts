'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reportService, CreateReportRequest } from '@/services/report-service';

export function useReports(params?: {
  page?: number;
  page_size?: number;
  type?: string;
  status?: string;
}) {
  return useQuery({
    queryKey: ['reports', params],
    queryFn: () => reportService.getReports(params),
  });
}

export function useReport(id: string) {
  return useQuery({
    queryKey: ['report', id],
    queryFn: () => reportService.getReport(id),
    enabled: !!id,
  });
}

export function useCreateReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateReportRequest) => reportService.createReport(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
    },
  });
}

export function useUpdateReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: Partial<CreateReportRequest>;
    }) => reportService.updateReport(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      queryClient.invalidateQueries({ queryKey: ['report', id] });
    },
  });
}

export function useDeleteReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => reportService.deleteReport(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
    },
  });
}

export function useGenerateReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { type: string; filters?: Record<string, unknown> }) =>
      reportService.generateReport(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
    },
  });
}

export function useExportReport() {
  return useMutation({
    mutationFn: ({
      id,
      format,
    }: {
      id: string;
      format: 'pdf' | 'html' | 'docx' | 'xlsx' | 'json' | 'csv';
    }) => reportService.exportReport(id, format),
  });
}

export function useReportTemplates() {
  return useQuery({
    queryKey: ['report-templates'],
    queryFn: () => reportService.getTemplates(),
  });
}

export function useReportSchedules() {
  return useQuery({
    queryKey: ['report-schedules'],
    queryFn: () => reportService.getSchedules(),
  });
}

export function useCreateReportSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      reportId,
      cronExpression,
      enabled,
    }: {
      reportId: string;
      cronExpression: string;
      enabled?: boolean;
    }) => reportService.createSchedule(reportId, cronExpression, enabled),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['report-schedules'] });
    },
  });
}

export function useUpdateReportSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { cron_expression?: string; enabled?: boolean };
    }) => reportService.updateSchedule(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['report-schedules'] });
    },
  });
}

export function useDeleteReportSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => reportService.deleteSchedule(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['report-schedules'] });
    },
  });
}

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  adminDashboardService,
  organizationService,
  adminUserService,
  roleService,
  permissionService,
  featureFlagService,
  apiKeyService,
  adminSubscriptionService,
  auditLogService,
} from '@/services/admin-service';
import { aiProviderService } from '@/services/ai-provider-service';
import { connectorService } from '@/services/connector-service';

// Dashboard
export function useAdminDashboardHealth() {
  return useQuery({
    queryKey: ['admin-dashboard-health'],
    queryFn: () => adminDashboardService.getHealth(),
  });
}

export function useAdminDashboardAnalytics(params?: { period?: 'day' | 'week' | 'month' | 'year' }) {
  return useQuery({
    queryKey: ['admin-dashboard-analytics', params],
    queryFn: () => adminDashboardService.getAnalytics(params),
  });
}

export function useAdminDashboardStats() {
  return useQuery({
    queryKey: ['admin-dashboard-stats'],
    queryFn: () => adminDashboardService.getStats(),
  });
}

// Organizations
export function useOrganizations(params?: {
  page?: number;
  page_size?: number;
  search?: string;
  is_active?: boolean;
}) {
  return useQuery({
    queryKey: ['organizations', params],
    queryFn: () => organizationService.getOrganizations(params),
  });
}

export function useOrganization(id: string) {
  return useQuery({
    queryKey: ['organization', id],
    queryFn: () => organizationService.getOrganization(id),
    enabled: !!id,
  });
}

export function useCreateOrganization() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { name: string; slug: string; plan_id?: string }) =>
      organizationService.createOrganization(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
    },
  });
}

export function useUpdateOrganization() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { name?: string; is_active?: boolean; plan_id?: string };
    }) => organizationService.updateOrganization(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
      queryClient.invalidateQueries({ queryKey: ['organization', id] });
    },
  });
}

export function useDeleteOrganization() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => organizationService.deleteOrganization(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
    },
  });
}

// Users
export function useAdminUsers(params?: {
  page?: number;
  page_size?: number;
  search?: string;
  role?: string;
  is_active?: boolean;
}) {
  return useQuery({
    queryKey: ['admin-users', params],
    queryFn: () => adminUserService.getUsers(params),
  });
}

export function useAdminUser(id: string) {
  return useQuery({
    queryKey: ['admin-user', id],
    queryFn: () => adminUserService.getUser(id),
    enabled: !!id,
  });
}

export function useCreateAdminUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      email: string;
      full_name: string;
      password: string;
      role?: string;
    }) => adminUserService.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
  });
}

export function useUpdateAdminUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { full_name?: string; role?: string; is_active?: boolean };
    }) => adminUserService.updateUser(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      queryClient.invalidateQueries({ queryKey: ['admin-user', id] });
    },
  });
}

export function useDeleteAdminUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => adminUserService.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
  });
}

// Roles
export function useRoles() {
  return useQuery({
    queryKey: ['roles'],
    queryFn: () => roleService.getRoles(),
  });
}

export function useRole(id: string) {
  return useQuery({
    queryKey: ['role', id],
    queryFn: () => roleService.getRole(id),
    enabled: !!id,
  });
}

export function useCreateRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { name: string; description: string; permissions: string[] }) =>
      roleService.createRole(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
    },
  });
}

export function useUpdateRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { name?: string; description?: string; permissions?: string[] };
    }) => roleService.updateRole(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
      queryClient.invalidateQueries({ queryKey: ['role', id] });
    },
  });
}

export function useDeleteRole() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => roleService.deleteRole(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roles'] });
    },
  });
}

// Permissions
export function usePermissions() {
  return useQuery({
    queryKey: ['permissions'],
    queryFn: () => permissionService.getPermissions(),
  });
}

// Feature Flags
export function useFeatureFlags() {
  return useQuery({
    queryKey: ['feature-flags'],
    queryFn: () => featureFlagService.getFeatureFlags(),
  });
}

export function useFeatureFlag(id: string) {
  return useQuery({
    queryKey: ['feature-flag', id],
    queryFn: () => featureFlagService.getFeatureFlag(id),
    enabled: !!id,
  });
}

export function useCreateFeatureFlag() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      key: string;
      name: string;
      description: string;
      enabled?: boolean;
      targeting?: { percentage?: number; user_ids?: string[]; roles?: string[] };
    }) => featureFlagService.createFeatureFlag(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feature-flags'] });
    },
  });
}

export function useUpdateFeatureFlag() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: {
        name?: string;
        description?: string;
        enabled?: boolean;
        targeting?: { percentage?: number; user_ids?: string[]; roles?: string[] };
      };
    }) => featureFlagService.updateFeatureFlag(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['feature-flags'] });
      queryClient.invalidateQueries({ queryKey: ['feature-flag', id] });
    },
  });
}

export function useDeleteFeatureFlag() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => featureFlagService.deleteFeatureFlag(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feature-flags'] });
    },
  });
}

export function useToggleFeatureFlag() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => featureFlagService.toggleFeatureFlag(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['feature-flags'] });
      queryClient.invalidateQueries({ queryKey: ['feature-flag', id] });
    },
  });
}

// API Keys
export function useAPIKeys() {
  return useQuery({
    queryKey: ['api-keys'],
    queryFn: () => apiKeyService.getAPIKeys(),
  });
}

export function useCreateAPIKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { name: string; permissions: string[]; expires_at?: string }) =>
      apiKeyService.createAPIKey(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
    },
  });
}

export function useRevokeAPIKey() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiKeyService.revokeAPIKey(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
    },
  });
}

// Subscriptions
export function useAdminSubscriptions(params?: {
  page?: number;
  page_size?: number;
  status?: string;
}) {
  return useQuery({
    queryKey: ['admin-subscriptions', params],
    queryFn: () => adminSubscriptionService.getSubscriptions(params),
  });
}

export function useAdminPlans() {
  return useQuery({
    queryKey: ['admin-plans'],
    queryFn: () => adminSubscriptionService.getPlans(),
  });
}

export function useCreatePlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      name: string;
      description: string;
      price_monthly: number;
      price_yearly: number;
      features: string[];
      limits: Record<string, number>;
      is_active: boolean;
    }) => adminSubscriptionService.createPlan(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-plans'] });
    },
  });
}

export function useUpdatePlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: {
        name?: string;
        description?: string;
        price_monthly?: number;
        price_yearly?: number;
        features?: string[];
        limits?: Record<string, number>;
        is_active?: boolean;
      };
    }) => adminSubscriptionService.updatePlan(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['admin-plans'] });
    },
  });
}

export function useDeletePlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => adminSubscriptionService.deletePlan(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-plans'] });
    },
  });
}

// Audit Logs
export function useAuditLogs(params?: {
  page?: number;
  page_size?: number;
  user_id?: string;
  action?: string;
  resource?: string;
  start_date?: string;
  end_date?: string;
}) {
  return useQuery({
    queryKey: ['audit-logs', params],
    queryFn: () => auditLogService.getAuditLogs(params),
  });
}

export function useExportAuditLogs() {
  return useMutation({
    mutationFn: (params: { format: 'csv' | 'json'; start_date?: string; end_date?: string }) =>
      auditLogService.exportAuditLogs(params),
  });
}

// AI Providers
export function useAIProviders() {
  return useQuery({
    queryKey: ['ai-providers'],
    queryFn: () => aiProviderService.getProviders(),
  });
}

export function useAIProvider(id: string) {
  return useQuery({
    queryKey: ['ai-provider', id],
    queryFn: () => aiProviderService.getProvider(id),
    enabled: !!id,
  });
}

export function useAIProviderMetrics(
  id: string,
  params?: { start_date?: string; end_date?: string; granularity?: 'hour' | 'day' | 'week' | 'month' }
) {
  return useQuery({
    queryKey: ['ai-provider-metrics', id, params],
    queryFn: () => aiProviderService.getProviderMetrics(id, params),
    enabled: !!id,
  });
}

export function useToggleAIProvider() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, enabled }: { id: string; enabled: boolean }) =>
      aiProviderService.toggleProvider(id, enabled),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['ai-providers'] });
      queryClient.invalidateQueries({ queryKey: ['ai-provider', id] });
    },
  });
}

// Connectors
export function useConnectors() {
  return useQuery({
    queryKey: ['connectors'],
    queryFn: () => connectorService.getConnectors(),
  });
}

export function useConnector(id: string) {
  return useQuery({
    queryKey: ['connector', id],
    queryFn: () => connectorService.getConnector(id),
    enabled: !!id,
  });
}

export function useConnectorLogs(
  id: string,
  params?: { page?: number; page_size?: number; level?: 'info' | 'warning' | 'error' }
) {
  return useQuery({
    queryKey: ['connector-logs', id, params],
    queryFn: () => connectorService.getConnectorLogs(id, params),
    enabled: !!id,
  });
}

export function useSyncConnector() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => connectorService.syncConnector(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['connectors'] });
      queryClient.invalidateQueries({ queryKey: ['connector', id] });
    },
  });
}

export function useToggleConnector() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, enabled }: { id: string; enabled: boolean }) =>
      connectorService.toggleConnector(id, enabled),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['connectors'] });
      queryClient.invalidateQueries({ queryKey: ['connector', id] });
    },
  });
}

import apiClient from '@/lib/api-client';
import type {
  Organization,
  User,
  Role,
  Permission,
  AuditLog,
  FeatureFlag,
  APIKey,
  SystemHealth,
  UsageAnalytics,
  SubscriptionPlan,
  Subscription,
} from '@/types';

// Dashboard
export const adminDashboardService = {
  async getHealth(): Promise<SystemHealth> {
    const response = await apiClient.get<SystemHealth>('/api/v1/admin/dashboard/health');
    return response.data;
  },

  async getAnalytics(params?: {
    period?: 'day' | 'week' | 'month' | 'year';
  }): Promise<UsageAnalytics> {
    const response = await apiClient.get<UsageAnalytics>('/api/v1/admin/dashboard/analytics', {
      params,
    });
    return response.data;
  },

  async getStats(): Promise<{
    total_users: number;
    total_organizations: number;
    total_signals: number;
    total_opportunities: number;
    total_reports: number;
    active_subscriptions: number;
  }> {
    const response = await apiClient.get('/api/v1/admin/dashboard/stats');
    return response.data;
  },
};

// Organizations
export const organizationService = {
  async getOrganizations(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    is_active?: boolean;
  }): Promise<{ items: Organization[]; total: number; page: number; page_size: number }> {
    const response = await apiClient.get('/api/v1/admin/organizations', { params });
    return response.data;
  },

  async getOrganization(id: string): Promise<Organization> {
    const response = await apiClient.get<Organization>(`/api/v1/admin/organizations/${id}`);
    return response.data;
  },

  async createOrganization(data: {
    name: string;
    slug: string;
    plan_id?: string;
  }): Promise<Organization> {
    const response = await apiClient.post<Organization>('/api/v1/admin/organizations', data);
    return response.data;
  },

  async updateOrganization(
    id: string,
    data: Partial<{ name: string; is_active: boolean; plan_id: string }>
  ): Promise<Organization> {
    const response = await apiClient.patch<Organization>(
      `/api/v1/admin/organizations/${id}`,
      data
    );
    return response.data;
  },

  async deleteOrganization(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(
      `/api/v1/admin/organizations/${id}`
    );
    return response.data;
  },
};

// Users
export const adminUserService = {
  async getUsers(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    role?: string;
    is_active?: boolean;
  }): Promise<{ items: User[]; total: number; page: number; page_size: number }> {
    const response = await apiClient.get('/api/v1/admin/users', { params });
    return response.data;
  },

  async getUser(id: string): Promise<User> {
    const response = await apiClient.get<User>(`/api/v1/admin/users/${id}`);
    return response.data;
  },

  async createUser(data: {
    email: string;
    full_name: string;
    password: string;
    role?: string;
  }): Promise<User> {
    const response = await apiClient.post<User>('/api/v1/admin/users', data);
    return response.data;
  },

  async updateUser(
    id: string,
    data: Partial<{ full_name: string; role: string; is_active: boolean }>
  ): Promise<User> {
    const response = await apiClient.patch<User>(`/api/v1/admin/users/${id}`, data);
    return response.data;
  },

  async deleteUser(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`/api/v1/admin/users/${id}`);
    return response.data;
  },

  async resendVerification(id: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(
      `/api/v1/admin/users/${id}/resend-verification`
    );
    return response.data;
  },
};

// Roles
export const roleService = {
  async getRoles(): Promise<Role[]> {
    const response = await apiClient.get<Role[]>('/api/v1/admin/roles');
    return response.data;
  },

  async getRole(id: string): Promise<Role> {
    const response = await apiClient.get<Role>(`/api/v1/admin/roles/${id}`);
    return response.data;
  },

  async createRole(data: { name: string; description: string; permissions: string[] }): Promise<Role> {
    const response = await apiClient.post<Role>('/api/v1/admin/roles', data);
    return response.data;
  },

  async updateRole(
    id: string,
    data: Partial<{ name: string; description: string; permissions: string[] }>
  ): Promise<Role> {
    const response = await apiClient.patch<Role>(`/api/v1/admin/roles/${id}`, data);
    return response.data;
  },

  async deleteRole(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`/api/v1/admin/roles/${id}`);
    return response.data;
  },
};

// Permissions
export const permissionService = {
  async getPermissions(): Promise<Permission[]> {
    const response = await apiClient.get<Permission[]>('/api/v1/admin/permissions');
    return response.data;
  },
};

// Feature Flags
export const featureFlagService = {
  async getFeatureFlags(): Promise<FeatureFlag[]> {
    const response = await apiClient.get<FeatureFlag[]>('/api/v1/admin/feature-flags');
    return response.data;
  },

  async getFeatureFlag(id: string): Promise<FeatureFlag> {
    const response = await apiClient.get<FeatureFlag>(
      `/api/v1/admin/feature-flags/${id}`
    );
    return response.data;
  },

  async createFeatureFlag(data: {
    key: string;
    name: string;
    description: string;
    enabled?: boolean;
    targeting?: FeatureFlag['targeting'];
  }): Promise<FeatureFlag> {
    const response = await apiClient.post<FeatureFlag>(
      '/api/v1/admin/feature-flags',
      data
    );
    return response.data;
  },

  async updateFeatureFlag(
    id: string,
    data: Partial<{
      name: string;
      description: string;
      enabled: boolean;
      targeting: FeatureFlag['targeting'];
    }>
  ): Promise<FeatureFlag> {
    const response = await apiClient.patch<FeatureFlag>(
      `/api/v1/admin/feature-flags/${id}`,
      data
    );
    return response.data;
  },

  async deleteFeatureFlag(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(
      `/api/v1/admin/feature-flags/${id}`
    );
    return response.data;
  },

  async toggleFeatureFlag(id: string): Promise<FeatureFlag> {
    const response = await apiClient.post<FeatureFlag>(
      `/api/v1/admin/feature-flags/${id}/toggle`
    );
    return response.data;
  },
};

// API Keys
export const apiKeyService = {
  async getAPIKeys(): Promise<APIKey[]> {
    const response = await apiClient.get<APIKey[]>('/api/v1/admin/api-keys');
    return response.data;
  },

  async createAPIKey(data: {
    name: string;
    permissions: string[];
    expires_at?: string;
  }): Promise<{ key: string } & APIKey> {
    const response = await apiClient.post('/api/v1/admin/api-keys', data);
    return response.data;
  },

  async revokeAPIKey(id: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(
      `/api/v1/admin/api-keys/${id}/revoke`
    );
    return response.data;
  },

  async rotateAPIKey(id: string): Promise<{ key: string }> {
    const response = await apiClient.post<{ key: string }>(
      `/api/v1/admin/api-keys/${id}/rotate`
    );
    return response.data;
  },
};

// Subscriptions
export const adminSubscriptionService = {
  async getSubscriptions(params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }): Promise<{ items: Subscription[]; total: number }> {
    const response = await apiClient.get('/api/v1/admin/subscriptions', { params });
    return response.data;
  },

  async getPlans(): Promise<SubscriptionPlan[]> {
    const response = await apiClient.get<SubscriptionPlan[]>('/api/v1/admin/plans');
    return response.data;
  },

  async createPlan(data: Omit<SubscriptionPlan, 'id'>): Promise<SubscriptionPlan> {
    const response = await apiClient.post<SubscriptionPlan>('/api/v1/admin/plans', data);
    return response.data;
  },

  async updatePlan(
    id: string,
    data: Partial<SubscriptionPlan>
  ): Promise<SubscriptionPlan> {
    const response = await apiClient.patch<SubscriptionPlan>(
      `/api/v1/admin/plans/${id}`,
      data
    );
    return response.data;
  },

  async deletePlan(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(
      `/api/v1/admin/plans/${id}`
    );
    return response.data;
  },
};

// Audit Logs
export const auditLogService = {
  async getAuditLogs(params?: {
    page?: number;
    page_size?: number;
    user_id?: string;
    action?: string;
    resource?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<{ items: AuditLog[]; total: number }> {
    const response = await apiClient.get('/api/v1/admin/audit-logs', { params });
    return response.data;
  },

  async exportAuditLogs(params?: {
    format: 'csv' | 'json';
    start_date?: string;
    end_date?: string;
  }): Promise<Blob> {
    const response = await apiClient.get('/api/v1/admin/audit-logs/export', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};

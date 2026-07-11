import apiClient from '@/lib/api-client';
import type {
  Notification,
  NotificationListResponse,
  UserNotificationPreferences,
} from '@/types';

export const notificationService = {
  async getNotifications(params?: {
    page?: number;
    page_size?: number;
    is_read?: boolean;
  }): Promise<NotificationListResponse> {
    const response = await apiClient.get<NotificationListResponse>('/api/v1/notifications/', {
      params,
    });
    return response.data;
  },

  async getNotification(id: string): Promise<Notification> {
    const response = await apiClient.get<Notification>(`/api/v1/notifications/${id}`);
    return response.data;
  },

  async markAsRead(id: string): Promise<Notification> {
    const response = await apiClient.patch<Notification>(
      `/api/v1/notifications/${id}/read`
    );
    return response.data;
  },

  async markAllAsRead(): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(
      '/api/v1/notifications/read-all'
    );
    return response.data;
  },

  async deleteNotification(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(
      `/api/v1/notifications/${id}`
    );
    return response.data;
  },

  async getPreferences(): Promise<UserNotificationPreferences> {
    const response = await apiClient.get<UserNotificationPreferences>(
      '/api/v1/notifications/preferences'
    );
    return response.data;
  },

  async updatePreferences(
    preferences: Partial<UserNotificationPreferences>
  ): Promise<UserNotificationPreferences> {
    const response = await apiClient.patch<UserNotificationPreferences>(
      '/api/v1/notifications/preferences',
      preferences
    );
    return response.data;
  },
};

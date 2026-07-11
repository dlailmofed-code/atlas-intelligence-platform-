import apiClient from '@/lib/api-client';
import type {
  Subscription,
  SubscriptionPlan,
  UsageRecord,
  Invoice,
  PaymentMethod,
} from '@/types';

export const subscriptionService = {
  async getSubscription(): Promise<Subscription> {
    const response = await apiClient.get<Subscription>('/api/v1/subscriptions/current');
    return response.data;
  },

  async getPlans(): Promise<SubscriptionPlan[]> {
    const response = await apiClient.get<SubscriptionPlan[]>('/api/v1/subscriptions/plans');
    return response.data;
  },

  async getUsage(): Promise<UsageRecord[]> {
    const response = await apiClient.get<UsageRecord[]>('/api/v1/subscriptions/usage');
    return response.data;
  },

  async getInvoices(params?: {
    page?: number;
    page_size?: number;
  }): Promise<{ items: Invoice[]; total: number; page: number; page_size: number }> {
    const response = await apiClient.get('/api/v1/subscriptions/invoices', { params });
    return response.data;
  },

  async getPaymentMethods(): Promise<PaymentMethod[]> {
    const response = await apiClient.get<PaymentMethod[]>('/api/v1/subscriptions/payment-methods');
    return response.data;
  },

  async addPaymentMethod(paymentMethodId: string): Promise<PaymentMethod> {
    const response = await apiClient.post<PaymentMethod>(
      '/api/v1/subscriptions/payment-methods',
      { payment_method_id: paymentMethodId }
    );
    return response.data;
  },

  async removePaymentMethod(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(
      `/api/v1/subscriptions/payment-methods/${id}`
    );
    return response.data;
  },

  async setDefaultPaymentMethod(id: string): Promise<PaymentMethod> {
    const response = await apiClient.post<PaymentMethod>(
      `/api/v1/subscriptions/payment-methods/${id}/default`
    );
    return response.data;
  },

  async subscribe(planId: string, billingCycle: 'monthly' | 'yearly'): Promise<Subscription> {
    const response = await apiClient.post<Subscription>('/api/v1/subscriptions/subscribe', {
      plan_id: planId,
      billing_cycle: billingCycle,
    });
    return response.data;
  },

  async upgrade(planId: string): Promise<Subscription> {
    const response = await apiClient.post<Subscription>('/api/v1/subscriptions/upgrade', {
      plan_id: planId,
    });
    return response.data;
  },

  async cancel(immediately: boolean = false): Promise<Subscription> {
    const response = await apiClient.post<Subscription>('/api/v1/subscriptions/cancel', {
      immediately,
    });
    return response.data;
  },

  async reactivate(): Promise<Subscription> {
    const response = await apiClient.post<Subscription>('/api/v1/subscriptions/reactivate');
    return response.data;
  },
};

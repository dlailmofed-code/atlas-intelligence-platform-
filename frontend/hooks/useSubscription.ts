'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { subscriptionService } from '@/services/subscription-service';

export function useSubscription() {
  return useQuery({
    queryKey: ['subscription'],
    queryFn: () => subscriptionService.getSubscription(),
  });
}

export function usePlans() {
  return useQuery({
    queryKey: ['plans'],
    queryFn: () => subscriptionService.getPlans(),
  });
}

export function useUsage() {
  return useQuery({
    queryKey: ['usage'],
    queryFn: () => subscriptionService.getUsage(),
  });
}

export function useInvoices(params?: { page?: number; page_size?: number }) {
  return useQuery({
    queryKey: ['invoices', params],
    queryFn: () => subscriptionService.getInvoices(params),
  });
}

export function usePaymentMethods() {
  return useQuery({
    queryKey: ['payment-methods'],
    queryFn: () => subscriptionService.getPaymentMethods(),
  });
}

export function useSubscribe() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      planId,
      billingCycle,
    }: {
      planId: string;
      billingCycle: 'monthly' | 'yearly';
    }) => subscriptionService.subscribe(planId, billingCycle),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] });
      queryClient.invalidateQueries({ queryKey: ['usage'] });
    },
  });
}

export function useUpgrade() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (planId: string) => subscriptionService.upgrade(planId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] });
    },
  });
}

export function useCancelSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (immediately: boolean) => subscriptionService.cancel(immediately),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] });
    },
  });
}

export function useReactivateSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => subscriptionService.reactivate(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription'] });
    },
  });
}

export function useAddPaymentMethod() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (paymentMethodId: string) =>
      subscriptionService.addPaymentMethod(paymentMethodId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment-methods'] });
    },
  });
}

export function useRemovePaymentMethod() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => subscriptionService.removePaymentMethod(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment-methods'] });
    },
  });
}

export function useSetDefaultPaymentMethod() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => subscriptionService.setDefaultPaymentMethod(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment-methods'] });
    },
  });
}

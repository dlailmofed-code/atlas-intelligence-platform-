'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore, useIsAuthenticated, useUser, useAuthLoading } from '@/store/auth-store';
import { authService } from '@/services/auth-service';
import type { LoginRequest, RegisterRequest } from '@/types';

export function useAuth() {
  const { setAuth, setUser, setToken, logout, setLoading } = useAuthStore();
  const isAuthenticated = useIsAuthenticated();
  const user = useUser();
  const isLoading = useAuthLoading();
  const router = useRouter();

  const login = async (data: LoginRequest) => {
    setLoading(true);
    try {
      const result = await authService.login(data);
      setAuth(result.tokens, result.user);
      router.push('/dashboard');
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const register = async (data: RegisterRequest) => {
    setLoading(true);
    try {
      const result = await authService.register(data);
      setAuth(result.tokens, result.user);
      router.push('/dashboard');
    } catch (error) {
      setLoading(false);
      throw error;
    }
  };

  const logoutUser = async () => {
    try {
      await authService.logout();
    } catch (error) {
      // Ignore logout errors
    } finally {
      logout();
      router.push('/auth/login');
    }
  };

  const refreshUser = async () => {
    if (isAuthenticated) {
      try {
        const userData = await authService.getMe();
        setUser(userData);
      } catch (error) {
        logout();
        router.push('/auth/login');
      }
    }
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout: logoutUser,
    refreshUser,
  };
}

export function useAuthGuard(redirectTo: string = '/auth/login') {
  const router = useRouter();
  const isAuthenticated = useIsAuthenticated();
  const isLoading = useAuthLoading();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(redirectTo);
    }
  }, [isAuthenticated, isLoading, redirectTo, router]);

  return { isAuthenticated, isLoading };
}

export function useGuestGuard(redirectTo: string = '/dashboard') {
  const router = useRouter();
  const isAuthenticated = useIsAuthenticated();
  const isLoading = useAuthLoading();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push(redirectTo);
    }
  }, [isAuthenticated, isLoading, redirectTo, router]);

  return { isAuthenticated, isLoading };
}

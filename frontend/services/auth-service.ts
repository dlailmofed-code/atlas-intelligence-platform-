import apiClient from '@/lib/api-client';
import type {
  LoginRequest,
  RegisterRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  TokenResponse,
  User,
} from '@/types';

export const authService = {
  async login(data: LoginRequest): Promise<{ tokens: TokenResponse; user: User }> {
    const response = await apiClient.post<TokenResponse & { user: User }>(
      '/api/v1/auth/login',
      data
    );
    return {
      tokens: {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        token_type: response.data.token_type,
        expires_in: response.data.expires_in,
      },
      user: response.data.user,
    };
  },

  async register(data: RegisterRequest): Promise<{ tokens: TokenResponse; user: User }> {
    const response = await apiClient.post<TokenResponse & { user: User }>(
      '/api/v1/auth/register',
      data
    );
    return {
      tokens: {
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        token_type: response.data.token_type,
        expires_in: response.data.expires_in,
      },
      user: response.data.user,
    };
  },

  async logout(): Promise<void> {
    await apiClient.post('/api/v1/auth/logout');
  },

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>(
      '/api/v1/auth/refresh',
      { refresh_token: refreshToken }
    );
    return response.data;
  },

  async getMe(): Promise<User> {
    const response = await apiClient.get<User>('/api/v1/users/me');
    return response.data;
  },

  async forgotPassword(data: ForgotPasswordRequest): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(
      '/api/v1/auth/forgot-password',
      data
    );
    return response.data;
  },

  async resetPassword(data: ResetPasswordRequest): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(
      '/api/v1/auth/reset-password',
      data
    );
    return response.data;
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await apiClient.patch<User>('/api/v1/users/me', data);
    return response.data;
  },

  async updatePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(
      '/api/v1/auth/change-password',
      { current_password: currentPassword, new_password: newPassword }
    );
    return response.data;
  },
};

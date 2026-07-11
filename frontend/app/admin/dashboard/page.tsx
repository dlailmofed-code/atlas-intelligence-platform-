'use client';

import * as React from 'react';
import {
  useAdminDashboardHealth,
  useAdminDashboardAnalytics,
  useAdminDashboardStats,
} from '@/hooks/useAdmin';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { formatRelativeTime } from '@/lib/utils';
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Database,
  Server,
  Users,
  Zap,
  TrendingUp,
  FileText,
  Target,
  RefreshCw,
} from 'lucide-react';

export default function AdminDashboardPage() {
  const { data: health, isLoading: loadingHealth, refetch: refetchHealth } = useAdminDashboardHealth();
  const { data: analytics, isLoading: loadingAnalytics } = useAdminDashboardAnalytics({ period: 'month' });
  const { data: stats, isLoading: loadingStats } = useAdminDashboardStats();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'up':
      case 'healthy':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'degraded':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'down':
      case 'unhealthy':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800';
      case 'unhealthy':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Admin Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor system health and platform analytics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge className={health?.status ? getStatusColor(health.status) : 'bg-gray-100'}>
            {health?.status || 'Unknown'}
          </Badge>
          <span className="text-sm text-muted-foreground">
            Last updated: {health?.timestamp ? formatRelativeTime(health.timestamp) : 'Never'}
          </span>
          <button
            onClick={() => refetchHealth()}
            className="rounded-full p-2 hover:bg-muted"
            disabled={loadingHealth}
          >
            <RefreshCw className={`h-4 w-4 ${loadingHealth ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* System Health */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            System Health
          </CardTitle>
          <CardDescription>Real-time status of system components</CardDescription>
        </CardHeader>
        <CardContent>
          {loadingHealth ? (
            <div className="space-y-4">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {health?.components.map((component) => (
                <div
                  key={component.name}
                  className="flex items-center justify-between rounded-lg border p-4"
                >
                  <div className="flex items-center gap-3">
                    {getStatusIcon(component.status)}
                    <span className="font-medium">{component.name}</span>
                  </div>
                  <div className="text-right text-sm">
                    {component.latency_ms !== undefined && (
                      <span className="text-muted-foreground">{component.latency_ms}ms</span>
                    )}
                    {component.error_rate !== undefined && (
                      <span className={component.error_rate > 5 ? 'text-red-500' : 'text-muted-foreground'}>
                        {component.error_rate.toFixed(1)}% errors
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Platform Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-blue-100 p-2">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats?.total_users?.toLocaleString() || 0}</p>
              <p className="text-sm text-muted-foreground">Total Users</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-purple-100 p-2">
              <Database className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats?.total_organizations?.toLocaleString() || 0}</p>
              <p className="text-sm text-muted-foreground">Organizations</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-orange-100 p-2">
              <Target className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats?.total_opportunities?.toLocaleString() || 0}</p>
              <p className="text-sm text-muted-foreground">Opportunities</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-green-100 p-2">
              <Zap className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats?.active_subscriptions?.toLocaleString() || 0}</p>
              <p className="text-sm text-muted-foreground">Active Subscriptions</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analytics */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Usage Analytics
            </CardTitle>
            <CardDescription>This month&apos;s platform usage</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingAnalytics ? (
              <div className="space-y-4">
                {[1, 2, 3, 4].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">API Requests</span>
                  <span className="font-medium">{analytics?.total_requests?.toLocaleString() || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Signals Generated</span>
                  <span className="font-medium">{analytics?.total_signals?.toLocaleString() || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Opportunities Identified</span>
                  <span className="font-medium">{analytics?.total_opportunities?.toLocaleString() || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Reports Generated</span>
                  <span className="font-medium">{analytics?.total_reports?.toLocaleString() || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Storage Used</span>
                  <span className="font-medium">
                    {analytics?.storage_used_bytes
                      ? `${(analytics.storage_used_bytes / 1024 / 1024 / 1024).toFixed(2)} GB`
                      : '0 GB'}
                  </span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Top Users
            </CardTitle>
            <CardDescription>Most active users this month</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingAnalytics ? (
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : analytics?.top_users && analytics.top_users.length > 0 ? (
              <div className="space-y-2">
                {analytics.top_users.map((user, index) => (
                  <div key={user.user_id} className="flex items-center justify-between rounded-lg border p-3">
                    <div className="flex items-center gap-3">
                      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-muted text-xs font-medium">
                        {index + 1}
                      </span>
                      <span className="font-medium">{user.email}</span>
                    </div>
                    <span className="text-muted-foreground">{user.requests.toLocaleString()} requests</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-8">No data available</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-4">
          <a href="/admin/organizations" className="block">
            <div className="flex items-center gap-3 rounded-lg border p-4 transition-colors hover:bg-accent">
              <Database className="h-5 w-5 text-muted-foreground" />
              <span>Manage Organizations</span>
            </div>
          </a>
          <a href="/admin/users" className="block">
            <div className="flex items-center gap-3 rounded-lg border p-4 transition-colors hover:bg-accent">
              <Users className="h-5 w-5 text-muted-foreground" />
              <span>Manage Users</span>
            </div>
          </a>
          <a href="/admin/feature-flags" className="block">
            <div className="flex items-center gap-3 rounded-lg border p-4 transition-colors hover:bg-accent">
              <Zap className="h-5 w-5 text-muted-foreground" />
              <span>Feature Flags</span>
            </div>
          </a>
          <a href="/admin/audit-logs" className="block">
            <div className="flex items-center gap-3 rounded-lg border p-4 transition-colors hover:bg-accent">
              <FileText className="h-5 w-5 text-muted-foreground" />
              <span>Audit Logs</span>
            </div>
          </a>
        </CardContent>
      </Card>
    </div>
  );
}

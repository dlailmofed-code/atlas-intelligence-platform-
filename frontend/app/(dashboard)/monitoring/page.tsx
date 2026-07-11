'use client';

import * as React from 'react';
import { useAdminDashboardHealth, useAdminDashboardAnalytics } from '@/hooks/useAdmin';
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
  RefreshCw,
  Zap,
  Clock,
} from 'lucide-react';

export default function MonitoringPage() {
  const { data: health, isLoading: loadingHealth, refetch } = useAdminDashboardHealth();
  const { data: analytics, isLoading: loadingAnalytics } = useAdminDashboardAnalytics({ period: 'day' });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'up':
      case 'healthy':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'degraded':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'down':
      case 'unhealthy':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-400" />;
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
          <h1 className="text-2xl font-bold">System Monitoring</h1>
          <p className="text-muted-foreground">
            Monitor system health and performance metrics
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Badge className={health?.status ? getStatusColor(health.status) : 'bg-gray-100'}>
            {health?.status || 'Unknown'}
          </Badge>
          <span className="text-sm text-muted-foreground">
            Last updated: {health?.timestamp ? formatRelativeTime(health.timestamp) : 'Never'}
          </span>
          <button
            onClick={() => refetch()}
            className="rounded-full p-2 hover:bg-muted"
            disabled={loadingHealth}
          >
            <RefreshCw className={`h-4 w-4 ${loadingHealth ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* System Components */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            System Components
          </CardTitle>
          <CardDescription>Real-time status of all system components</CardDescription>
        </CardHeader>
        <CardContent>
          {loadingHealth ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {health?.components.map((component) => (
                <div
                  key={component.name}
                  className="flex items-center justify-between rounded-lg border p-4"
                >
                  <div className="flex items-center gap-3">
                    {getStatusIcon(component.status)}
                    <div>
                      <p className="font-medium">{component.name}</p>
                      <p className="text-sm text-muted-foreground capitalize">{component.status}</p>
                    </div>
                  </div>
                  <div className="text-right text-sm">
                    {component.latency_ms !== undefined && (
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3 text-muted-foreground" />
                        <span>{component.latency_ms}ms</span>
                      </div>
                    )}
                    {component.error_rate !== undefined && (
                      <div className="flex items-center gap-1">
                        <AlertCircle className={`h-3 w-3 ${component.error_rate > 5 ? 'text-red-500' : 'text-muted-foreground'}`} />
                        <span className={component.error_rate > 5 ? 'text-red-500' : ''}>
                          {component.error_rate.toFixed(1)}% errors
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Today's Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-blue-100 p-2">
              <Activity className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{analytics?.total_requests?.toLocaleString() || 0}</p>
              <p className="text-sm text-muted-foreground">API Requests</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-purple-100 p-2">
              <Zap className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{analytics?.total_signals?.toLocaleString() || 0}</p>
              <p className="text-sm text-muted-foreground">Signals</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-green-100 p-2">
              <Database className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{analytics?.total_opportunities?.toLocaleString() || 0}</p>
              <p className="text-sm text-muted-foreground">Opportunities</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-orange-100 p-2">
              <Server className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {analytics?.storage_used_bytes
                  ? `${(analytics.storage_used_bytes / 1024 / 1024 / 1024).toFixed(2)} GB`
                  : '0 GB'}
              </p>
              <p className="text-sm text-muted-foreground">Storage</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Queue Status Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            Background Jobs
          </CardTitle>
          <CardDescription>Status of background job queues</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between rounded-lg border p-4">
              <div>
                <p className="font-medium">Intelligence Processing</p>
                <p className="text-sm text-muted-foreground">Queue: default</p>
              </div>
              <div className="flex items-center gap-4">
                <Badge variant="default">3 Active</Badge>
                <span className="text-sm text-muted-foreground">0 Pending</span>
              </div>
            </div>
            <div className="flex items-center justify-between rounded-lg border p-4">
              <div>
                <p className="font-medium">Report Generation</p>
                <p className="text-sm text-muted-foreground">Queue: reports</p>
              </div>
              <div className="flex items-center gap-4">
                <Badge variant="default">1 Active</Badge>
                <span className="text-sm text-muted-foreground">2 Pending</span>
              </div>
            </div>
            <div className="flex items-center justify-between rounded-lg border p-4">
              <div>
                <p className="font-medium">Data Sync</p>
                <p className="text-sm text-muted-foreground">Queue: sync</p>
              </div>
              <div className="flex items-center gap-4">
                <Badge variant="secondary">Idle</Badge>
                <span className="text-sm text-muted-foreground">0 Pending</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

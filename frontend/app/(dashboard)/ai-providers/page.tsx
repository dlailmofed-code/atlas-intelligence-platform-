'use client';

import * as React from 'react';
import { useAIProviders, useToggleAIProvider } from '@/hooks/useAdmin';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Switch } from '@/components/ui/switch';
import { formatCurrency } from '@/lib/utils';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Cpu,
  DollarSign,
  RefreshCw,
  Timer,
  XCircle,
  Zap,
} from 'lucide-react';

export default function AIProvidersPage() {
  const { data: providers, isLoading, refetch } = useAIProviders();
  const toggleMutation = useToggleAIProvider();

  const handleToggle = (id: string, currentEnabled: boolean) => {
    toggleMutation.mutate({ id, enabled: !currentEnabled });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'inactive':
        return <XCircle className="h-5 w-5 text-gray-400" />;
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-400" />;
    }
  };

  const getHealthColor = (health: number) => {
    if (health >= 90) return 'text-green-500';
    if (health >= 70) return 'text-yellow-500';
    return 'text-red-500';
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-6 lg:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent className="space-y-4">
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">AI Providers</h1>
          <p className="text-muted-foreground">
            Manage your AI provider connections and monitor usage
          </p>
        </div>
        <Button variant="outline" onClick={() => refetch()} disabled={isLoading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Overview Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-green-100 p-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {providers?.filter((p) => p.status === 'active').length || 0}
              </p>
              <p className="text-sm text-muted-foreground">Active</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-blue-100 p-2">
              <Zap className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {providers?.reduce((acc, p) => acc + p.requests_today, 0).toLocaleString() || 0}
              </p>
              <p className="text-sm text-muted-foreground">Requests Today</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-purple-100 p-2">
              <Cpu className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {providers?.reduce((acc, p) => acc + p.tokens_used_today, 0).toLocaleString() || 0}
              </p>
              <p className="text-sm text-muted-foreground">Tokens Today</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-orange-100 p-2">
              <DollarSign className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {formatCurrency(providers?.reduce((acc, p) => acc + p.cost_today, 0) || 0)}
              </p>
              <p className="text-sm text-muted-foreground">Cost Today</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Provider Cards */}
      <div className="grid gap-6 lg:grid-cols-2">
        {providers?.map((provider) => (
          <Card key={provider.id}>
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getStatusIcon(provider.status)}
                  <div>
                    <CardTitle>{provider.name}</CardTitle>
                    <CardDescription className="capitalize">{provider.type}</CardDescription>
                  </div>
                </div>
                <Switch
                  checked={provider.status === 'active'}
                  onCheckedChange={() => handleToggle(provider.id, provider.status === 'active')}
                  disabled={toggleMutation.isPending}
                />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Health Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Activity className="h-4 w-4" />
                    Health
                  </div>
                  <p className={`text-2xl font-bold ${getHealthColor(provider.health)}`}>
                    {provider.health}%
                  </p>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Timer className="h-4 w-4" />
                    Latency
                  </div>
                  <p className="text-2xl font-bold">{provider.latency_ms}ms</p>
                </div>
              </div>

              {/* Usage Stats */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Error Rate</span>
                  <span className={provider.error_rate > 5 ? 'text-red-500' : ''}>
                    {provider.error_rate.toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Requests Today</span>
                  <span>{provider.requests_today.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Tokens Today</span>
                  <span>{provider.tokens_used_today.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Cost Today</span>
                  <span>{formatCurrency(provider.cost_today)}</span>
                </div>
              </div>

              {/* Monthly Stats */}
              <div className="border-t pt-4">
                <p className="text-sm font-medium">This Month</p>
                <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Requests: </span>
                    <span>{provider.requests_monthly.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Tokens: </span>
                    <span>{provider.tokens_used_monthly.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Cost: </span>
                    <span>{formatCurrency(provider.cost_monthly)}</span>
                  </div>
                </div>
              </div>

              {/* Failover Status */}
              <div className="flex items-center gap-2">
                <Badge variant={provider.failover_enabled ? 'default' : 'secondary'}>
                  {provider.failover_enabled ? 'Failover Enabled' : 'No Failover'}
                </Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {providers?.length === 0 && (
        <Card className="flex flex-col items-center justify-center py-12">
          <Cpu className="h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-4 font-semibold">No AI Providers</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Configure your AI providers in the admin settings
          </p>
        </Card>
      )}
    </div>
  );
}

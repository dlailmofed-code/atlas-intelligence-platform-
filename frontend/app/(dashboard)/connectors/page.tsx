'use client';

import * as React from 'react';
import { useConnectors, useSyncConnector, useToggleConnector } from '@/hooks/useAdmin';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Switch } from '@/components/ui/switch';
import { formatRelativeTime } from '@/lib/utils';
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Globe,
  Link2,
  RefreshCw,
  Settings,
  Trash2,
  XCircle,
} from 'lucide-react';

export default function ConnectorsPage() {
  const { data: connectors, isLoading, refetch } = useConnectors();
  const syncMutation = useSyncConnector();
  const toggleMutation = useToggleConnector();

  const handleSync = (id: string) => {
    syncMutation.mutate(id);
  };

  const handleToggle = (id: string, currentEnabled: boolean) => {
    toggleMutation.mutate({ id, enabled: !currentEnabled });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'syncing':
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'inactive':
        return <XCircle className="h-5 w-5 text-gray-400" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'syncing':
        return 'bg-blue-100 text-blue-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'financial':
        return <Globe className="h-5 w-5" />;
      case 'news':
        return <Activity className="h-5 w-5" />;
      case 'government':
        return <Link2 className="h-5 w-5" />;
      default:
        return <Globe className="h-5 w-5" />;
    }
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
          <h1 className="text-2xl font-bold">Data Connectors</h1>
          <p className="text-muted-foreground">
            Manage your data source connections and sync status
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
                {connectors?.filter((c) => c.status === 'active').length || 0}
              </p>
              <p className="text-sm text-muted-foreground">Active</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-blue-100 p-2">
              <RefreshCw className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {connectors?.filter((c) => c.status === 'syncing').length || 0}
              </p>
              <p className="text-sm text-muted-foreground">Syncing</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-red-100 p-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {connectors?.filter((c) => c.status === 'error').length || 0}
              </p>
              <p className="text-sm text-muted-foreground">Errors</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 p-4">
            <div className="rounded-full bg-purple-100 p-2">
              <Activity className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">
                {connectors?.reduce((acc, c) => acc + c.items_synced, 0).toLocaleString() || 0}
              </p>
              <p className="text-sm text-muted-foreground">Total Synced</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Connector Cards */}
      <div className="grid gap-6 lg:grid-cols-2">
        {connectors?.map((connector) => (
          <Card key={connector.id}>
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="rounded-full bg-muted p-2">
                    {getTypeIcon(connector.type)}
                  </div>
                  <div>
                    <CardTitle>{connector.name}</CardTitle>
                    <CardDescription>{connector.provider}</CardDescription>
                  </div>
                </div>
                <Switch
                  checked={connector.status === 'active'}
                  onCheckedChange={() => handleToggle(connector.id, connector.status === 'active')}
                  disabled={toggleMutation.isPending}
                />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Status */}
              <div className="flex items-center justify-between">
                <Badge className={getStatusColor(connector.status)}>
                  {connector.status}
                </Badge>
                {connector.last_sync && (
                  <span className="text-sm text-muted-foreground">
                    Last sync: {formatRelativeTime(connector.last_sync)}
                  </span>
                )}
              </div>

              {/* Health */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Health:</span>
                <div className="flex items-center gap-1">
                  <div className="h-2 w-24 rounded-full bg-muted">
                    <div
                      className={`h-2 rounded-full ${
                        connector.health >= 90
                          ? 'bg-green-500'
                          : connector.health >= 70
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${connector.health}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">{connector.health}%</span>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Items Synced</span>
                  <p className="font-medium">{connector.items_synced.toLocaleString()}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Errors Today</span>
                  <p className={`font-medium ${connector.errors_today > 0 ? 'text-red-500' : ''}`}>
                    {connector.errors_today}
                  </p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 border-t pt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSync(connector.id)}
                  disabled={syncMutation.isPending || connector.status === 'syncing'}
                  className="flex-1"
                >
                  <RefreshCw className={`mr-2 h-4 w-4 ${connector.status === 'syncing' ? 'animate-spin' : ''}`} />
                  Sync Now
                </Button>
                <Button variant="outline" size="icon">
                  <Settings className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="icon">
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {connectors?.length === 0 && (
        <Card className="flex flex-col items-center justify-center py-12">
          <Link2 className="h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-4 font-semibold">No Connectors</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Add your first data connector to start syncing data
          </p>
        </Card>
      )}
    </div>
  );
}

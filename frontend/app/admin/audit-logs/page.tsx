'use client';

import * as React from 'react';
import { useAuditLogs, useExportAuditLogs } from '@/hooks/useAdmin';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { Pagination } from '@/components/ui/pagination';
import { formatRelativeTime } from '@/lib/utils';
import {
  Download,
  FileText,
  Search,
  User,
  Filter,
  AlertCircle,
  CheckCircle2,
  Info,
} from 'lucide-react';

export default function AdminAuditLogsPage() {
  const [page, setPage] = React.useState(1);
  const [search, setSearch] = React.useState('');
  const [actionFilter, setActionFilter] = React.useState('');

  const { data: auditLogs, isLoading } = useAuditLogs({
    page,
    page_size: 20,
    user_id: search.includes('@') ? search : undefined,
    action: actionFilter || undefined,
  });

  const exportMutation = useExportAuditLogs();

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      const blob = await exportMutation.mutateAsync({
        format,
        start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch {
      console.error('Export failed');
    }
  };

  const getActionIcon = (action: string) => {
    if (action.startsWith('create')) {
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    }
    if (action.startsWith('delete')) {
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
    return <Info className="h-4 w-4 text-blue-500" />;
  };

  const actionTypes = [
    { value: '', label: 'All Actions' },
    { value: 'create', label: 'Create' },
    { value: 'update', label: 'Update' },
    { value: 'delete', label: 'Delete' },
    { value: 'login', label: 'Login' },
    { value: 'logout', label: 'Logout' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Audit Logs</h1>
          <p className="text-muted-foreground">
            Track all user actions and system changes
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => handleExport('csv')}
            disabled={exportMutation.isPending}
          >
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </Button>
          <Button
            variant="outline"
            onClick={() => handleExport('json')}
            disabled={exportMutation.isPending}
          >
            <Download className="mr-2 h-4 w-4" />
            Export JSON
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by user email..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={actionFilter}
            onChange={(e) => {
              setActionFilter(e.target.value);
              setPage(1);
            }}
            className="rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            {actionTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Audit Logs Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left text-sm font-medium">Timestamp</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">User</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Action</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Resource</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">IP Address</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Details</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  [...Array(10)].map((_, i) => (
                    <tr key={i} className="border-b">
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-32" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-40" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-6 w-20" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-32" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-24" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-48" />
                      </td>
                    </tr>
                  ))
                ) : auditLogs?.items && auditLogs.items.length > 0 ? (
                  auditLogs.items.map((log) => (
                    <tr key={log.id} className="border-b">
                      <td className="px-4 py-3 text-muted-foreground">
                        {formatRelativeTime(log.created_at)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{log.user_email}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          {getActionIcon(log.action)}
                          <Badge variant="secondary" className="font-normal">
                            {log.action}
                          </Badge>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="text-sm">{log.resource}</span>
                        {log.resource_id && (
                          <span className="ml-2 text-xs text-muted-foreground">
                            ({log.resource_id.slice(0, 8)}...)
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground text-sm">
                        {log.ip_address}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground text-sm">
                        {log.details ? (
                          <code className="rounded bg-muted px-1 py-0.5 text-xs">
                            {JSON.stringify(log.details).slice(0, 50)}...
                          </code>
                        ) : (
                          '-'
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="px-4 py-12 text-center text-muted-foreground">
                      No audit logs found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Pagination */}
      {auditLogs && auditLogs.total > 20 && (
        <Pagination
          page={page}
          pageSize={20}
          total={auditLogs.total}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}

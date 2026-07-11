'use client';

import * as React from 'react';
import {
  useOrganizations,
  useDeleteOrganization,
} from '@/hooks/useAdmin';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { Pagination } from '@/components/ui/pagination';
import { formatRelativeTime } from '@/lib/utils';
import {
  Building2,
  Plus,
  Search,
  MoreHorizontal,
  Trash2,
  Edit,
  Eye,
} from 'lucide-react';

export default function AdminOrganizationsPage() {
  const [page, setPage] = React.useState(1);
  const [search, setSearch] = React.useState('');

  const { data, isLoading, refetch } = useOrganizations({
    page,
    page_size: 20,
    search: search || undefined,
  });

  const deleteMutation = useDeleteOrganization();

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this organization?')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Organizations</h1>
          <p className="text-muted-foreground">
            Manage platform organizations
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Organization
        </Button>
      </div>

      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search organizations..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="pl-10"
          />
        </div>
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left text-sm font-medium">Organization</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Plan</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Members</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Seats</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Created</th>
                  <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  [...Array(5)].map((_, i) => (
                    <tr key={i} className="border-b">
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-48" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-24" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-12" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-12" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-16" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-24" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-8 w-20" />
                      </td>
                    </tr>
                  ))
                ) : data?.items && data.items.length > 0 ? (
                  data.items.map((org) => (
                    <tr key={org.id} className="border-b">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <div className="rounded-full bg-muted p-2">
                            <Building2 className="h-4 w-4" />
                          </div>
                          <div>
                            <p className="font-medium">{org.name}</p>
                            <p className="text-sm text-muted-foreground">{org.slug}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant="secondary">{org.plan_name}</Badge>
                      </td>
                      <td className="px-4 py-3">{org.member_count}</td>
                      <td className="px-4 py-3">{org.seat_count}</td>
                      <td className="px-4 py-3">
                        <Badge variant={org.is_active ? 'default' : 'secondary'}>
                          {org.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {formatRelativeTime(org.created_at)}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(org.id)}
                            disabled={deleteMutation.isPending}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="px-4 py-12 text-center text-muted-foreground">
                      No organizations found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Pagination */}
      {data && data.total > 20 && (
        <Pagination
          page={page}
          pageSize={20}
          total={data.total}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}

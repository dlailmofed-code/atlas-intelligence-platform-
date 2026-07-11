'use client';

import * as React from 'react';
import { useAdminSubscriptions } from '@/hooks/useAdmin';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Pagination } from '@/components/ui/pagination';
import { formatRelativeTime } from '@/lib/utils';
import { CreditCard } from 'lucide-react';

export default function AdminSubscriptionsPage() {
  const [page, setPage] = React.useState(1);

  const { data: subscriptions, isLoading } = useAdminSubscriptions({
    page,
    page_size: 20,
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      case 'past_due':
        return 'bg-red-100 text-red-800';
      case 'trialing':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Subscriptions</h1>
        <p className="text-muted-foreground">
          Manage platform subscriptions
        </p>
      </div>

      {/* Subscriptions Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left text-sm font-medium">User</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Plan</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Billing</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Period End</th>
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
                        <Skeleton className="h-6 w-24" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-6 w-20" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-16" />
                      </td>
                      <td className="px-4 py-3">
                        <Skeleton className="h-4 w-32" />
                      </td>
                    </tr>
                  ))
                ) : subscriptions?.items && subscriptions.items.length > 0 ? (
                  subscriptions.items.map((sub) => (
                    <tr key={sub.id} className="border-b">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <div className="rounded-full bg-muted p-2">
                            <CreditCard className="h-4 w-4" />
                          </div>
                          <span className="font-medium">{sub.user_id}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant="secondary">{sub.plan_name}</Badge>
                      </td>
                      <td className="px-4 py-3">
                        <Badge className={getStatusColor(sub.status)}>{sub.status}</Badge>
                      </td>
                      <td className="px-4 py-3 capitalize">{sub.billing_cycle}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {formatRelativeTime(sub.current_period_end)}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="px-4 py-12 text-center text-muted-foreground">
                      No subscriptions found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Pagination */}
      {subscriptions && subscriptions.total > 20 && (
        <Pagination
          page={page}
          pageSize={20}
          total={subscriptions.total}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}

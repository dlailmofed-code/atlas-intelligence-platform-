'use client';

import * as React from 'react';
import {
  useSubscription,
  usePlans,
  useUsage,
  useInvoices,
  useCancelSubscription,
  useReactivateSubscription,
} from '@/hooks/useSubscription';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Pagination } from '@/components/ui/pagination';
import { formatCurrency, formatRelativeTime } from '@/lib/utils';
import {
  CreditCard,
  Download,
  TrendingUp,
  AlertTriangle,
  Check,
  X,
  Zap,
} from 'lucide-react';

export default function BillingPage() {
  const [page, setPage] = React.useState(1);

  const { data: subscription, isLoading: loadingSubscription } = useSubscription();
  const { data: plans, isLoading: loadingPlans } = usePlans();
  const { data: usage, isLoading: loadingUsage } = useUsage();
  const { data: invoices, isLoading: loadingInvoices } = useInvoices({ page, page_size: 10 });
  const cancelMutation = useCancelSubscription();
  const reactivateMutation = useReactivateSubscription();

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

  if (loadingSubscription) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-12 w-24" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Billing</h1>
        <p className="text-muted-foreground">
          Manage your subscription and billing information
        </p>
      </div>

      {/* Current Plan */}
      {subscription && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Current Plan</CardTitle>
              <CardDescription>Your active subscription</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-2xl font-bold">{subscription.plan_name}</p>
                  <Badge className={getStatusColor(subscription.status)}>
                    {subscription.status}
                  </Badge>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold">
                    {subscription.billing_cycle === 'monthly' ? '$29' : '$290'}
                    <span className="text-sm font-normal text-muted-foreground">
                      /{subscription.billing_cycle === 'monthly' ? 'mo' : 'yr'}
                    </span>
                  </p>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Billing cycle</span>
                  <span className="capitalize">{subscription.billing_cycle}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Current period</span>
                  <span>
                    {new Date(subscription.current_period_start).toLocaleDateString()} -{' '}
                    {new Date(subscription.current_period_end).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" className="flex-1">
                  Change Plan
                </Button>
                {subscription.status === 'active' ? (
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={() => cancelMutation.mutate(false)}
                    disabled={cancelMutation.isPending}
                  >
                    Cancel
                  </Button>
                ) : (
                  <Button
                    variant="default"
                    className="flex-1"
                    onClick={() => reactivateMutation.mutate()}
                    disabled={reactivateMutation.isPending}
                  >
                    Reactivate
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Usage This Month</CardTitle>
              <CardDescription>Track your resource usage</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {loadingUsage ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-16 w-full" />
                  ))}
                </div>
              ) : (
                usage?.map((record) => (
                  <div key={record.id} className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="capitalize">{record.feature.replace('_', ' ')}</span>
                      <span className="text-muted-foreground">
                        {record.count.toLocaleString()} / {record.limit.toLocaleString()}
                      </span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-muted">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          record.count / record.limit > 0.9
                            ? 'bg-red-500'
                            : record.count / record.limit > 0.7
                            ? 'bg-yellow-500'
                            : 'bg-primary'
                        }`}
                        style={{ width: `${Math.min((record.count / record.limit) * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs */}
      <Tabs defaultValue="invoices" className="space-y-4">
        <TabsList>
          <TabsTrigger value="invoices">Invoices</TabsTrigger>
          <TabsTrigger value="plans">Available Plans</TabsTrigger>
          <TabsTrigger value="payment">Payment Method</TabsTrigger>
        </TabsList>

        <TabsContent value="invoices" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Invoice History</CardTitle>
              <CardDescription>Download your past invoices</CardDescription>
            </CardHeader>
            <CardContent>
              {loadingInvoices ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : invoices && invoices.items.length > 0 ? (
                <div className="space-y-2">
                  {invoices.items.map((invoice) => (
                    <div
                      key={invoice.id}
                      className="flex items-center justify-between rounded-lg border p-4"
                    >
                      <div className="flex items-center gap-4">
                        <div className="rounded-full bg-muted p-2">
                          <CreditCard className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="font-medium">
                            {formatCurrency(invoice.amount, invoice.currency)}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {new Date(invoice.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <Badge className={getStatusColor(invoice.status)}>
                          {invoice.status}
                        </Badge>
                        <Button variant="ghost" size="icon">
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">No invoices yet</p>
              )}
              {invoices && invoices.total > 10 && (
                <Pagination
                  page={page}
                  pageSize={10}
                  total={invoices.total}
                  onPageChange={setPage}
                />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="plans" className="space-y-4">
          {loadingPlans ? (
            <div className="grid gap-6 md:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <Card key={i}>
                  <CardHeader>
                    <Skeleton className="h-6 w-24" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-8 w-16" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-3">
              {plans?.map((plan) => (
                <Card key={plan.id} className={plan.name === subscription?.plan_name ? 'border-primary' : ''}>
                  <CardHeader>
                    <CardTitle>{plan.name}</CardTitle>
                    <CardDescription>{plan.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <span className="text-3xl font-bold">
                        {formatCurrency(plan.price_monthly)}
                      </span>
                      <span className="text-muted-foreground">/month</span>
                    </div>
                    <ul className="space-y-2 text-sm">
                      {plan.features.map((feature, i) => (
                        <li key={i} className="flex items-center gap-2">
                          <Check className="h-4 w-4 text-green-500" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <Button
                      variant={plan.name === subscription?.plan_name ? 'outline' : 'default'}
                      className="w-full"
                      disabled={plan.name === subscription?.plan_name}
                    >
                      {plan.name === subscription?.plan_name ? 'Current Plan' : 'Upgrade'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="payment" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Payment Method</CardTitle>
              <CardDescription>Manage your payment methods</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between rounded-lg border p-4">
                <div className="flex items-center gap-4">
                  <div className="rounded-full bg-muted p-2">
                    <CreditCard className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="font-medium">Visa ending in 4242</p>
                    <p className="text-sm text-muted-foreground">Expires 12/2025</p>
                  </div>
                </div>
                <Button variant="outline">Update</Button>
              </div>
              <Button variant="ghost" className="mt-4">
                <Zap className="mr-2 h-4 w-4" />
                Add Payment Method
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

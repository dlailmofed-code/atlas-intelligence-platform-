'use client';

import * as React from 'react';
import { useAdminPlans } from '@/hooks/useAdmin';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { formatCurrency } from '@/lib/utils';
import { Plus, Zap, Check } from 'lucide-react';

export default function AdminPlansPage() {
  const { data: plans, isLoading } = useAdminPlans();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Plans</h1>
          <p className="text-muted-foreground">
            Manage subscription plans
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create Plan
        </Button>
      </div>

      {/* Plans Grid */}
      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-24" />
              </CardHeader>
              <CardContent className="space-y-4">
                <Skeleton className="h-8 w-16" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-3">
          {plans?.map((plan) => (
            <Card key={plan.id} className={plan.is_active ? '' : 'opacity-60'}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>{plan.name}</CardTitle>
                  <Badge variant={plan.is_active ? 'default' : 'secondary'}>
                    {plan.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
                <CardDescription>{plan.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <span className="text-3xl font-bold">
                    {formatCurrency(plan.price_monthly)}
                  </span>
                  <span className="text-muted-foreground">/month</span>
                </div>
                <p className="text-sm text-muted-foreground">
                  Yearly: {formatCurrency(plan.price_yearly)}/year
                </p>
                
                <div className="space-y-2">
                  <p className="text-sm font-medium">Features:</p>
                  <ul className="space-y-1">
                    {plan.features.slice(0, 5).map((feature, i) => (
                      <li key={i} className="flex items-center gap-2 text-sm">
                        <Check className="h-4 w-4 text-green-500" />
                        {feature}
                      </li>
                    ))}
                    {plan.features.length > 5 && (
                      <li className="text-sm text-muted-foreground">
                        +{plan.features.length - 5} more features
                      </li>
                    )}
                  </ul>
                </div>

                <div className="border-t pt-4">
                  <p className="text-sm font-medium">Limits:</p>
                  <div className="mt-2 space-y-1 text-sm text-muted-foreground">
                    {Object.entries(plan.limits).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="capitalize">{key.replace('_', ' ')}:</span>
                        <span>{value.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2 border-t pt-4">
                  <Button variant="outline" className="flex-1">
                    Edit
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {plans?.length === 0 && (
        <Card className="flex flex-col items-center justify-center py-12">
          <Zap className="h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-4 font-semibold">No Plans</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Create your first subscription plan
          </p>
        </Card>
      )}
    </div>
  );
}

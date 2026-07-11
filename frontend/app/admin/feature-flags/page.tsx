'use client';

import * as React from 'react';
import {
  useFeatureFlags,
  useToggleFeatureFlag,
  useDeleteFeatureFlag,
} from '@/hooks/useAdmin';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Skeleton } from '@/components/ui/skeleton';
import { formatRelativeTime } from '@/lib/utils';
import {
  Plus,
  Search,
  Zap,
  Trash2,
  Edit,
  Target,
  Users,
} from 'lucide-react';

export default function AdminFeatureFlagsPage() {
  const [search, setSearch] = React.useState('');

  const { data: featureFlags, isLoading } = useFeatureFlags();
  const toggleMutation = useToggleFeatureFlag();
  const deleteMutation = useDeleteFeatureFlag();

  const handleToggle = (id: string) => {
    toggleMutation.mutate(id);
  };

  const handleDelete = (id: string) => {
    if (confirm('Are you sure you want to delete this feature flag?')) {
      deleteMutation.mutate(id);
    }
  };

  const filteredFlags = featureFlags?.filter(
    (flag) =>
      flag.name.toLowerCase().includes(search.toLowerCase()) ||
      flag.key.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Feature Flags</h1>
          <p className="text-muted-foreground">
            Control feature rollouts and experiments
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create Feature Flag
        </Button>
      </div>

      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search feature flags..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Feature Flags Grid */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent className="space-y-4">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredFlags && filteredFlags.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {filteredFlags.map((flag) => (
            <Card key={flag.id}>
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="rounded-full bg-muted p-2">
                      <Zap className="h-4 w-4" />
                    </div>
                    <div>
                      <CardTitle className="text-base">{flag.name}</CardTitle>
                      <CardDescription className="font-mono text-xs">
                        {flag.key}
                      </CardDescription>
                    </div>
                  </div>
                  <Switch
                    checked={flag.enabled}
                    onCheckedChange={() => handleToggle(flag.id)}
                    disabled={toggleMutation.isPending}
                  />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">{flag.description}</p>

                {/* Targeting Rules */}
                <div className="space-y-2">
                  <p className="text-sm font-medium">Targeting</p>
                  <div className="flex flex-wrap gap-2">
                    {flag.targeting.percentage !== undefined && (
                      <Badge variant="secondary">
                        <Target className="mr-1 h-3 w-3" />
                        {flag.targeting.percentage}% rollout
                      </Badge>
                    )}
                    {flag.targeting.user_ids && flag.targeting.user_ids.length > 0 && (
                      <Badge variant="secondary">
                        <Users className="mr-1 h-3 w-3" />
                        {flag.targeting.user_ids.length} users
                      </Badge>
                    )}
                    {flag.targeting.roles && flag.targeting.roles.length > 0 && (
                      <Badge variant="secondary">
                        {flag.targeting.roles.join(', ')}
                      </Badge>
                    )}
                    {!flag.targeting.percentage &&
                      !flag.targeting.user_ids?.length &&
                      !flag.targeting.roles?.length && (
                        <Badge variant="outline">No targeting rules</Badge>
                      )}
                  </div>
                </div>

                {/* Meta */}
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Created {formatRelativeTime(flag.created_at)}</span>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => handleDelete(flag.id)}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="flex flex-col items-center justify-center py-12">
          <Zap className="h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-4 font-semibold">No Feature Flags</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Create your first feature flag to get started
          </p>
        </Card>
      )}
    </div>
  );
}

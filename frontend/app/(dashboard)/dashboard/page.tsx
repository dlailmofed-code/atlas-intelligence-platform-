'use client';

import * as React from 'react';
import Link from 'next/link';
import { useUser } from '@/store/auth-store';
import { useFeaturedOpportunities, useOpportunities } from '@/hooks/useOpportunities';
import { useIntelligenceDashboard } from '@/hooks/useIntelligence';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton, StatCardSkeleton } from '@/components/ui/skeleton';
import { formatRelativeTime, formatNumber } from '@/lib/utils';
import {
  Target,
  TrendingUp,
  AlertCircle,
  Brain,
  ArrowRight,
  Bookmark,
  Activity,
} from 'lucide-react';

export default function DashboardPage() {
  const user = useUser();
  const { data: opportunities, isLoading: loadingOpportunities } = useFeaturedOpportunities(5);
  const { data: dashboard, isLoading: loadingDashboard } = useIntelligenceDashboard();
  const { data: bookmarks } = useOpportunities({ filters: { is_bookmarked: true }, page_size: 3 });

  const stats = [
    {
      title: 'Total Opportunities',
      value: dashboard?.total_signals || 0,
      change: '+12%',
      trend: 'up',
      icon: Target,
      color: 'text-blue-600',
    },
    {
      title: 'Active Signals',
      value: dashboard?.active_signals || 0,
      change: '+8%',
      trend: 'up',
      icon: Activity,
      color: 'text-green-600',
    },
    {
      title: 'High Confidence',
      value: dashboard?.high_confidence_signals || 0,
      change: '+5%',
      trend: 'up',
      icon: TrendingUp,
      color: 'text-purple-600',
    },
    {
      title: 'Patterns Detected',
      value: dashboard?.patterns_detected || 0,
      change: '+15%',
      trend: 'up',
      icon: Brain,
      color: 'text-orange-600',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-2xl font-bold">
          Welcome back, {user?.full_name?.split(' ')[0] || 'User'}
        </h1>
        <p className="text-muted-foreground">
          Here&apos;s what&apos;s happening with your intelligence today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {loadingDashboard ? (
          <>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </>
        ) : (
          stats.map((stat) => (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatNumber(stat.value)}</div>
                <p className="text-xs text-muted-foreground">
                  <span className={stat.trend === 'up' ? 'text-green-600' : 'text-red-600'}>
                    {stat.change}
                  </span>{' '}
                  from last month
                </p>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Featured Opportunities */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Featured Opportunities</CardTitle>
              <CardDescription>Top business opportunities identified</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/opportunities">
                View all <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            {loadingOpportunities ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center gap-4">
                    <Skeleton className="h-12 w-12 rounded" />
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-48" />
                      <Skeleton className="h-3 w-32" />
                    </div>
                  </div>
                ))}
              </div>
            ) : opportunities && opportunities.length > 0 ? (
              <div className="space-y-4">
                {opportunities.map((opp) => (
                  <Link
                    key={opp.id}
                    href={`/opportunities/${opp.id}`}
                    className="flex items-start gap-4 rounded-lg border p-3 transition-colors hover:bg-accent"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Target className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1 space-y-1">
                      <p className="font-medium leading-none">{opp.title}</p>
                      <p className="text-sm text-muted-foreground line-clamp-1">
                        {opp.description}
                      </p>
                      <div className="flex items-center gap-2 pt-1">
                        <Badge variant="secondary" className="text-xs">
                          {opp.category}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {opp.industry}
                        </Badge>
                        {opp.score && (
                          <span className="text-xs text-muted-foreground">
                            Score: {opp.score.overall}
                          </span>
                        )}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Target className="h-12 w-12 text-muted-foreground/50" />
                <p className="mt-2 text-sm text-muted-foreground">
                  No opportunities yet
                </p>
                <Button variant="outline" size="sm" className="mt-4" asChild>
                  <Link href="/opportunities">Explore Opportunities</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Signals */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Signals</CardTitle>
              <CardDescription>Latest intelligence signals detected</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/intelligence">
                View all <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            {loadingDashboard ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="flex items-center gap-4">
                    <Skeleton className="h-12 w-12 rounded" />
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-48" />
                      <Skeleton className="h-3 w-32" />
                    </div>
                  </div>
                ))}
              </div>
            ) : dashboard?.recent_signals && dashboard.recent_signals.length > 0 ? (
              <div className="space-y-4">
                {dashboard.recent_signals.map((signal) => (
                  <Link
                    key={signal.id}
                    href={`/intelligence/signals/${signal.id}`}
                    className="flex items-start gap-4 rounded-lg border p-3 transition-colors hover:bg-accent"
                  >
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-orange-100">
                      <AlertCircle className="h-5 w-5 text-orange-600" />
                    </div>
                    <div className="flex-1 space-y-1">
                      <p className="font-medium leading-none">{signal.name}</p>
                      <p className="text-sm text-muted-foreground line-clamp-1">
                        {signal.description}
                      </p>
                      <div className="flex items-center gap-2 pt-1">
                        <Badge
                          variant={signal.trend === 'up' ? 'success' : signal.trend === 'down' ? 'destructive' : 'secondary'}
                          className="text-xs"
                        >
                          {signal.trend}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {formatRelativeTime(signal.detected_at)}
                        </span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Brain className="h-12 w-12 text-muted-foreground/50" />
                <p className="mt-2 text-sm text-muted-foreground">
                  No signals detected yet
                </p>
                <Button variant="outline" size="sm" className="mt-4" asChild>
                  <Link href="/intelligence">View Intelligence</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="cursor-pointer transition-colors hover:border-primary">
          <Link href="/opportunities" className="block p-6">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
                <Target className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold">Explore Opportunities</h3>
                <p className="text-sm text-muted-foreground">
                  Discover new business opportunities
                </p>
              </div>
            </div>
          </Link>
        </Card>

        <Card className="cursor-pointer transition-colors hover:border-primary">
          <Link href="/intelligence" className="block p-6">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-100">
                <Brain className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold">Intelligence Dashboard</h3>
                <p className="text-sm text-muted-foreground">
                  View real-time intelligence
                </p>
              </div>
            </div>
          </Link>
        </Card>

        <Card className="cursor-pointer transition-colors hover:border-primary">
          <Link href="/reports" className="block p-6">
            <div className="flex items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
                <Bookmark className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold">Saved Reports</h3>
                <p className="text-sm text-muted-foreground">
                  Access your saved reports
                </p>
              </div>
            </div>
          </Link>
        </Card>
      </div>
    </div>
  );
}

'use client';

import * as React from 'react';
import Link from 'next/link';
import { useIntelligenceDashboard, useSignals, usePatterns, useCausalLinks } from '@/hooks/useIntelligence';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Pagination } from '@/components/ui/pagination';
import { Skeleton } from '@/components/ui/skeleton';
import { formatRelativeTime, formatNumber } from '@/lib/utils';
import {
  Brain,
  Activity,
  AlertCircle,
  GitBranch,
  TrendingUp,
  TrendingDown,
  Minus,
  ArrowRight,
  Zap,
  Target,
} from 'lucide-react';

export default function IntelligencePage() {
  const [activeTab, setActiveTab] = React.useState('signals');
  const [page, setPage] = React.useState(1);
  const [timeRange, setTimeRange] = React.useState('30d');

  const { data: dashboard, isLoading: loadingDashboard } = useIntelligenceDashboard({ timeRange });
  const { data: signals, isLoading: loadingSignals } = useSignals({ page, page_size: 10 });
  const { data: patterns, isLoading: loadingPatterns } = usePatterns({ page, page_size: 10 });
  const { data: causalLinks, isLoading: loadingCausalLinks } = useCausalLinks({ page, page_size: 10 });

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getPatternTypeColor = (type: string) => {
    switch (type) {
      case 'convergence':
        return 'bg-blue-100 text-blue-800';
      case 'divergence':
        return 'bg-purple-100 text-purple-800';
      case 'trend':
        return 'bg-green-100 text-green-800';
      case 'anomaly':
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
          <h1 className="text-2xl font-bold">Intelligence Dashboard</h1>
          <p className="text-muted-foreground">
            Real-time monitoring and analysis of intelligence signals
          </p>
        </div>
        <div className="flex gap-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Signals</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loadingDashboard ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">{formatNumber(dashboard?.total_signals || 0)}</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Signals</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loadingDashboard ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">{formatNumber(dashboard?.active_signals || 0)}</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Patterns</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loadingDashboard ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">{formatNumber(dashboard?.patterns_detected || 0)}</div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Causal Links</CardTitle>
            <GitBranch className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loadingDashboard ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="text-2xl font-bold">{formatNumber(dashboard?.causal_links || 0)}</div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="signals">Signals</TabsTrigger>
          <TabsTrigger value="patterns">Patterns</TabsTrigger>
          <TabsTrigger value="causal">Causal Links</TabsTrigger>
          <TabsTrigger value="indicators">Indicators</TabsTrigger>
        </TabsList>

        {/* Signals Tab */}
        <TabsContent value="signals" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Intelligence Signals</h2>
            <Button variant="outline" size="sm" asChild>
              <Link href="/intelligence/signals">View all</Link>
            </Button>
          </div>
          
          {loadingSignals ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Card key={i}>
                  <CardContent className="p-4">
                    <Skeleton className="h-20 w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : signals && signals.items.length > 0 ? (
            <div className="space-y-4">
              {signals.items.map((signal) => (
                <Card key={signal.id} className="group">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-orange-100">
                          <AlertCircle className="h-5 w-5 text-orange-600" />
                        </div>
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold">{signal.name}</h3>
                            {getTrendIcon(signal.trend)}
                          </div>
                          <p className="text-sm text-muted-foreground">{signal.description}</p>
                          <div className="flex flex-wrap items-center gap-2 pt-2">
                            <Badge variant="secondary">{signal.category}</Badge>
                            <Badge variant="outline">
                              Intensity: {signal.intensity}%
                            </Badge>
                            <Badge variant="outline">
                              Confidence: {signal.confidence}%
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {formatRelativeTime(signal.detected_at)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm" asChild className="opacity-0 group-hover:opacity-100">
                        <Link href={`/intelligence/signals/${signal.id}`}>
                          Details <ArrowRight className="ml-1 h-4 w-4" />
                        </Link>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="flex flex-col items-center justify-center py-12">
              <AlertCircle className="h-12 w-12 text-muted-foreground/50" />
              <h3 className="mt-4 font-semibold">No signals detected</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Signals will appear here when detected
              </p>
            </Card>
          )}

          {signals && signals.total > 10 && (
            <Pagination
              page={page}
              pageSize={10}
              total={signals.total}
              onPageChange={setPage}
            />
          )}
        </TabsContent>

        {/* Patterns Tab */}
        <TabsContent value="patterns" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Detected Patterns</h2>
            <Button variant="outline" size="sm" asChild>
              <Link href="/intelligence/patterns">View all</Link>
            </Button>
          </div>

          {loadingPatterns ? (
            <div className="grid gap-4 md:grid-cols-2">
              {[1, 2, 3, 4].map((i) => (
                <Card key={i}>
                  <CardContent className="p-4">
                    <Skeleton className="h-24 w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : patterns && patterns.items.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {patterns.items.map((pattern) => (
                <Card key={pattern.id} className="group">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <Brain className="h-5 w-5 text-primary" />
                          <h3 className="font-semibold">{pattern.name}</h3>
                        </div>
                        <p className="text-sm text-muted-foreground">{pattern.description}</p>
                        <div className="flex flex-wrap items-center gap-2 pt-2">
                          <Badge className={getPatternTypeColor(pattern.type)}>
                            {pattern.type}
                          </Badge>
                          <Badge variant="outline">
                            Confidence: {(pattern.confidence * 100).toFixed(0)}%
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {formatRelativeTime(pattern.detected_at)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="flex flex-col items-center justify-center py-12">
              <Brain className="h-12 w-12 text-muted-foreground/50" />
              <h3 className="mt-4 font-semibold">No patterns detected</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Patterns will appear here when detected
              </p>
            </Card>
          )}
        </TabsContent>

        {/* Causal Links Tab */}
        <TabsContent value="causal" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Causal Relationships</h2>
            <Button variant="outline" size="sm" asChild>
              <Link href="/intelligence/causal-links">View all</Link>
            </Button>
          </div>

          {loadingCausalLinks ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Card key={i}>
                  <CardContent className="p-4">
                    <Skeleton className="h-16 w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : causalLinks && causalLinks.items.length > 0 ? (
            <div className="space-y-4">
              {causalLinks.items.map((link) => (
                <Card key={link.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">{link.cause_entity}</Badge>
                          <GitBranch className="h-4 w-4 text-muted-foreground" />
                          <Badge variant="secondary">{link.effect_entity}</Badge>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <Badge variant="outline">
                          {link.relationship_type}
                        </Badge>
                        <Badge variant="outline">
                          Confidence: {(link.confidence * 100).toFixed(0)}%
                        </Badge>
                      </div>
                    </div>
                    <p className="mt-3 text-sm text-muted-foreground">
                      {link.evidence_summary}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="flex flex-col items-center justify-center py-12">
              <GitBranch className="h-12 w-12 text-muted-foreground/50" />
              <h3 className="mt-4 font-semibold">No causal links found</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Causal relationships will appear here
              </p>
            </Card>
          )}
        </TabsContent>

        {/* Indicators Tab */}
        <TabsContent value="indicators" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Intelligence Indicators</h2>
            <Button variant="outline" size="sm" asChild>
              <Link href="/intelligence/indicators">View all</Link>
            </Button>
          </div>

          {loadingDashboard ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <Card key={i}>
                  <CardContent className="p-4">
                    <Skeleton className="h-24 w-full" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : dashboard?.top_indicators && dashboard.top_indicators.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {dashboard.top_indicators.map((indicator) => (
                <Card key={indicator.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-sm font-medium">{indicator.name}</p>
                        <p className="text-xs text-muted-foreground">{indicator.type}</p>
                      </div>
                      {getTrendIcon(indicator.trend)}
                    </div>
                    <div className="mt-3">
                      <div className="text-2xl font-bold">{indicator.value.toFixed(1)}</div>
                      {indicator.industry && (
                        <p className="text-xs text-muted-foreground">{indicator.industry}</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="flex flex-col items-center justify-center py-12">
              <Target className="h-12 w-12 text-muted-foreground/50" />
              <h3 className="mt-4 font-semibold">No indicators available</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Indicators will appear here when available
              </p>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

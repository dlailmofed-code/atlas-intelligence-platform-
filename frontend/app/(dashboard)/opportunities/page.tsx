'use client';

import * as React from 'react';
import Link from 'next/link';
import { useOpportunities, useBookmarkOpportunity, useUnbookmarkOpportunity } from '@/hooks/useOpportunities';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Pagination } from '@/components/ui/pagination';
import { Skeleton, CardSkeleton } from '@/components/ui/skeleton';
import { formatRelativeTime } from '@/lib/utils';
import {
  Search,
  Target,
  Filter,
  Bookmark,
  BookmarkCheck,
  TrendingUp,
  Globe,
  Building,
  X,
} from 'lucide-react';

const categories = [
  { value: '', label: 'All Categories' },
  { value: 'market', label: 'Market' },
  { value: 'technology', label: 'Technology' },
  { value: 'investment', label: 'Investment' },
  { value: 'partnership', label: 'Partnership' },
  { value: 'regulatory', label: 'Regulatory' },
];

const industries = [
  { value: '', label: 'All Industries' },
  { value: 'technology', label: 'Technology' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'finance', label: 'Finance' },
  { value: 'retail', label: 'Retail' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'energy', label: 'Energy' },
];

const regions = [
  { value: '', label: 'All Regions' },
  { value: 'north_america', label: 'North America' },
  { value: 'europe', label: 'Europe' },
  { value: 'asia_pacific', label: 'Asia Pacific' },
  { value: 'latin_america', label: 'Latin America' },
  { value: 'middle_east', label: 'Middle East' },
  { value: 'africa', label: 'Africa' },
];

export default function OpportunitiesPage() {
  const [page, setPage] = React.useState(1);
  const [search, setSearch] = React.useState('');
  const [filters, setFilters] = React.useState({
    category: '',
    industry: '',
    region: '',
  });
  const [showFilters, setShowFilters] = React.useState(false);

  const { data, isLoading, isFetching } = useOpportunities({
    page,
    page_size: 12,
    filters,
  });

  const bookmarkMutation = useBookmarkOpportunity();
  const unbookmarkMutation = useUnbookmarkOpportunity();

  const handleBookmark = (id: string, isBookmarked: boolean) => {
    if (isBookmarked) {
      unbookmarkMutation.mutate(id);
    } else {
      bookmarkMutation.mutate(id);
    }
  };

  const activeFiltersCount = Object.values(filters).filter(Boolean).length;

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const clearFilters = () => {
    setFilters({ category: '', industry: '', region: '' });
    setPage(1);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Opportunities</h1>
          <p className="text-muted-foreground">
            Discover and track business opportunities
          </p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col gap-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search opportunities..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button
          variant="outline"
          onClick={() => setShowFilters(!showFilters)}
          className="gap-2"
        >
          <Filter className="h-4 w-4" />
          Filters
          {activeFiltersCount > 0 && (
            <Badge variant="default" className="ml-1 h-5 w-5 rounded-full p-0 text-xs">
              {activeFiltersCount}
            </Badge>
          )}
        </Button>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Filters</CardTitle>
              {activeFiltersCount > 0 && (
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  <X className="mr-1 h-4 w-4" />
                  Clear all
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-3">
              <Select
                label="Category"
                options={categories}
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
              />
              <Select
                label="Industry"
                options={industries}
                value={filters.industry}
                onChange={(e) => handleFilterChange('industry', e.target.value)}
              />
              <Select
                label="Region"
                options={regions}
                value={filters.region}
                onChange={(e) => handleFilterChange('region', e.target.value)}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {data && !isLoading && (
            <>
              Showing {(page - 1) * 12 + 1} to {Math.min(page * 12, data.total)} of {data.total} results
            </>
          )}
        </p>
      </div>

      {/* Opportunities Grid */}
      {isLoading ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.map((opp) => (
            <Card key={opp.id} className="group overflow-hidden">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Target className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="line-clamp-1 text-base">{opp.title}</CardTitle>
                      <CardDescription className="line-clamp-1">
                        {formatRelativeTime(opp.created_at)}
                      </CardDescription>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleBookmark(opp.id, opp.is_bookmarked)}
                    className="opacity-0 transition-opacity group-hover:opacity-100"
                  >
                    {opp.is_bookmarked ? (
                      <BookmarkCheck className="h-4 w-4 text-primary" />
                    ) : (
                      <Bookmark className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="line-clamp-2 text-sm text-muted-foreground">
                  {opp.description}
                </p>
                
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">{opp.category}</Badge>
                  <Badge variant="outline">{opp.industry}</Badge>
                </div>

                {opp.score && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Overall Score</span>
                      <span className="font-medium">{opp.score.overall}%</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-muted">
                      <div
                        className="h-2 rounded-full bg-primary transition-all"
                        style={{ width: `${opp.score.overall}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Demand: {opp.score.demand}</span>
                      <span>Growth: {opp.score.growth}</span>
                      <span>Risk: {opp.score.risk}</span>
                    </div>
                  </div>
                )}

                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  {opp.region && (
                    <div className="flex items-center gap-1">
                      <Globe className="h-3 w-3" />
                      {opp.region}
                    </div>
                  )}
                  {opp.estimated_market_size && (
                    <div className="flex items-center gap-1">
                      <Building className="h-3 w-3" />
                      {opp.estimated_market_size}
                    </div>
                  )}
                </div>

                <Button variant="outline" className="w-full" asChild>
                  <Link href={`/opportunities/${opp.id}`}>View Details</Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="flex flex-col items-center justify-center py-12">
          <Target className="h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-4 font-semibold">No opportunities found</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Try adjusting your filters or search terms
          </p>
          {activeFiltersCount > 0 && (
            <Button variant="outline" onClick={clearFilters} className="mt-4">
              Clear filters
            </Button>
          )}
        </Card>
      )}

      {/* Pagination */}
      {data && data.total > 12 && (
        <Pagination
          page={page}
          pageSize={12}
          total={data.total}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}

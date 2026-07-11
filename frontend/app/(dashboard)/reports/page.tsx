'use client';

import * as React from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { formatRelativeTime } from '@/lib/utils';
import {
  FileText,
  Plus,
  Download,
  Clock,
  CheckCircle,
  FileBarChart,
  BookOpen,
  Share2,
} from 'lucide-react';

// Mock data for reports
const mockReports = [
  {
    id: '1',
    title: 'Q4 2025 Market Analysis Report',
    description: 'Comprehensive analysis of market trends and opportunities for Q4 2025',
    type: 'market_research',
    status: 'completed',
    created_at: '2025-12-15T10:30:00Z',
    pages: 45,
  },
  {
    id: '2',
    title: 'Technology Sector Deep Dive',
    description: 'In-depth analysis of the technology sector with emerging opportunities',
    type: 'sector_analysis',
    status: 'completed',
    created_at: '2025-12-10T14:20:00Z',
    pages: 32,
  },
  {
    id: '3',
    title: 'Monthly Intelligence Summary - November',
    description: 'Monthly intelligence digest covering key signals and patterns',
    type: 'intelligence_digest',
    status: 'completed',
    created_at: '2025-11-30T09:00:00Z',
    pages: 18,
  },
  {
    id: '4',
    title: 'Investment Opportunity Analysis',
    description: 'Analysis of potential investment opportunities identified this quarter',
    type: 'investment',
    status: 'generating',
    created_at: '2025-12-18T08:00:00Z',
    pages: 0,
  },
];

const reportTypes = [
  { value: 'market_research', label: 'Market Research', icon: FileBarChart },
  { value: 'sector_analysis', label: 'Sector Analysis', icon: BookOpen },
  { value: 'intelligence_digest', label: 'Intelligence Digest', icon: FileText },
  { value: 'investment', label: 'Investment Analysis', icon: FileBarChart },
];

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'completed':
      return <Badge variant="success">Completed</Badge>;
    case 'generating':
      return <Badge variant="warning">Generating</Badge>;
    case 'pending':
      return <Badge variant="secondary">Pending</Badge>;
    case 'failed':
      return <Badge variant="destructive">Failed</Badge>;
    default:
      return <Badge variant="outline">{status}</Badge>;
  }
};

export default function ReportsPage() {
  const [filter, setFilter] = React.useState('all');
  const isLoading = false; // Would be replaced with actual data fetching

  const filteredReports = filter === 'all' 
    ? mockReports 
    : mockReports.filter(r => r.type === filter);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Reports</h1>
          <p className="text-muted-foreground">
            Access and manage your intelligence reports
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Generate Report
        </Button>
      </div>

      {/* Report Types */}
      <div className="grid gap-4 md:grid-cols-4">
        {reportTypes.map((type) => (
          <Card key={type.value} className="cursor-pointer transition-colors hover:border-primary">
            <CardContent className="flex items-center gap-4 p-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <type.icon className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="font-medium">{type.label}</h3>
                <p className="text-sm text-muted-foreground">
                  {mockReports.filter(r => r.type === type.value).length} reports
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <Button
          variant={filter === 'all' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setFilter('all')}
        >
          All Reports
        </Button>
        {reportTypes.map((type) => (
          <Button
            key={type.value}
            variant={filter === type.value ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilter(type.value)}
          >
            {type.label}
          </Button>
        ))}
      </div>

      {/* Reports List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <Skeleton className="h-24 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredReports.length > 0 ? (
        <div className="space-y-4">
          {filteredReports.map((report) => (
            <Card key={report.id} className="group">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <FileText className="h-6 w-6 text-primary" />
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">{report.title}</h3>
                        {getStatusBadge(report.status)}
                      </div>
                      <p className="text-sm text-muted-foreground">{report.description}</p>
                      <div className="flex flex-wrap items-center gap-4 pt-2">
                        <Badge variant="outline">
                          {reportTypes.find(t => t.value === report.type)?.label}
                        </Badge>
                        {report.pages > 0 && (
                          <span className="text-xs text-muted-foreground">
                            {report.pages} pages
                          </span>
                        )}
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {formatRelativeTime(report.created_at)}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2 opacity-0 transition-opacity group-hover:opacity-100">
                    {report.status === 'completed' && (
                      <>
                        <Button variant="outline" size="sm">
                          <Download className="mr-1 h-4 w-4" />
                          Download
                        </Button>
                        <Button variant="outline" size="icon">
                          <Share2 className="h-4 w-4" />
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="flex flex-col items-center justify-center py-12">
          <FileText className="h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-4 font-semibold">No reports found</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Generate your first report to get started
          </p>
          <Button className="mt-4">
            <Plus className="mr-2 h-4 w-4" />
            Generate Report
          </Button>
        </Card>
      )}
    </div>
  );
}

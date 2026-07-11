'use client';

import * as React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { formatRelativeTime } from '@/lib/utils';
import {
  FolderKanban,
  Plus,
  Users,
  Target,
  Globe,
  Lock,
  MoreHorizontal,
} from 'lucide-react';

// Mock data for projects
const mockProjects = [
  {
    id: '1',
    name: 'Market Research 2025',
    description: 'Comprehensive market research for 2025 strategic planning',
    is_public: false,
    created_at: '2025-12-01T10:00:00Z',
    opportunity_count: 24,
    member_count: 5,
  },
  {
    id: '2',
    name: 'Technology Trends',
    description: 'Tracking emerging technology trends and opportunities',
    is_public: true,
    created_at: '2025-11-15T14:30:00Z',
    opportunity_count: 18,
    member_count: 3,
  },
  {
    id: '3',
    name: 'Healthcare Innovation',
    description: 'Investment opportunities in healthcare sector',
    is_public: false,
    created_at: '2025-10-20T09:00:00Z',
    opportunity_count: 12,
    member_count: 4,
  },
  {
    id: '4',
    name: 'ESG Opportunities',
    description: 'Environmental and sustainability investment opportunities',
    is_public: true,
    created_at: '2025-09-10T11:00:00Z',
    opportunity_count: 8,
    member_count: 2,
  },
];

export default function ProjectsPage() {
  const isLoading = false; // Would be replaced with actual data fetching

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Projects</h1>
          <p className="text-muted-foreground">
            Organize your research into focused projects
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Project
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
            <FolderKanban className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockProjects.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockProjects.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Public Projects</CardTitle>
            <Globe className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockProjects.filter(p => p.is_public).length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {mockProjects.reduce((acc, p) => acc + p.member_count, 0)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Projects Grid */}
      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <Skeleton className="h-32 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : mockProjects.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2">
          {mockProjects.map((project) => (
            <Card key={project.id} className="group cursor-pointer transition-colors hover:border-primary">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <FolderKanban className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-base">{project.name}</CardTitle>
                      <div className="flex items-center gap-2 pt-1">
                        {project.is_public ? (
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Globe className="h-3 w-3" />
                            Public
                          </div>
                        ) : (
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Lock className="h-3 w-3" />
                            Private
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <CardDescription className="line-clamp-2">
                  {project.description}
                </CardDescription>
                
                <div className="flex items-center gap-6 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Target className="h-4 w-4" />
                    {project.opportunity_count} opportunities
                  </div>
                  <div className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    {project.member_count} members
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t">
                  <span className="text-xs text-muted-foreground">
                    Created {formatRelativeTime(project.created_at)}
                  </span>
                  <Button variant="outline" size="sm">
                    View Project
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="flex flex-col items-center justify-center py-12">
          <FolderKanban className="h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-4 font-semibold">No projects yet</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Create your first project to start organizing your research
          </p>
          <Button className="mt-4">
            <Plus className="mr-2 h-4 w-4" />
            Create Project
          </Button>
        </Card>
      )}
    </div>
  );
}

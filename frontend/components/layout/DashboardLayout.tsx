'use client';

import * as React from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useAuthGuard } from '@/hooks/useAuth';
import { cn } from '@/lib/utils';

interface DashboardLayoutProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
}

export function DashboardLayout({ children, title, description }: DashboardLayoutProps) {
  const { isAuthenticated, isLoading } = useAuthGuard();
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header title={title} description={description} />
        <main
          className={cn(
            'flex-1 overflow-y-auto bg-background p-6',
            sidebarCollapsed ? 'ml-0' : 'ml-0'
          )}
        >
          {children}
        </main>
      </div>
    </div>
  );
}

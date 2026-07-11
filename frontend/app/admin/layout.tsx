'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthGuard } from '@/hooks/useAuth';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Building2,
  Users,
  Shield,
  Key,
  Zap,
  FileText,
  Cpu,
  Link2,
  FileCode,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

const adminNav = [
  { title: 'Dashboard', href: '/admin/dashboard', icon: LayoutDashboard },
  { title: 'Organizations', href: '/admin/organizations', icon: Building2 },
  { title: 'Users', href: '/admin/users', icon: Users },
  { title: 'Subscriptions', href: '/admin/subscriptions', icon: FileText },
  { title: 'Plans', href: '/admin/plans', icon: Zap },
  { title: 'Feature Flags', href: '/admin/feature-flags', icon: Shield },
  { title: 'API Keys', href: '/admin/api-keys', icon: Key },
  { title: 'AI Providers', href: '/admin/providers', icon: Cpu },
  { title: 'Connectors', href: '/admin/connectors', icon: Link2 },
  { title: 'Audit Logs', href: '/admin/audit-logs', icon: FileCode },
];

interface AdminLayoutProps {
  children: React.ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
  const { isAuthenticated, isLoading } = useAuthGuard();
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);
  const pathname = usePathname() ?? '';

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
      {/* Admin Sidebar */}
      <aside
        className={cn(
          'flex flex-col border-r bg-card transition-all duration-300',
          sidebarCollapsed ? 'w-[70px]' : 'w-[260px]'
        )}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b px-4">
          {!sidebarCollapsed && (
            <Link href="/admin/dashboard" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-destructive">
                <Shield className="h-5 w-5 text-destructive-foreground" />
              </div>
              <span className="font-semibold text-foreground">Admin</span>
            </Link>
          )}
          {sidebarCollapsed && (
            <Link href="/admin/dashboard" className="mx-auto">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-destructive">
                <Shield className="h-5 w-5 text-destructive-foreground" />
              </div>
            </Link>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="hidden rounded-md p-1.5 hover:bg-accent md:block"
            aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {sidebarCollapsed ? (
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronLeft className="h-4 w-4 text-muted-foreground" />
            )}
          </button>
        </div>

        {/* Admin Navigation */}
        <nav className="flex-1 space-y-1 overflow-y-auto p-2">
          {adminNav.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            const Icon = item.icon;
            
            return (
              <Link
                key={item.title}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )}
                title={sidebarCollapsed ? item.title : undefined}
              >
                <Icon className="h-5 w-5 shrink-0" />
                {!sidebarCollapsed && <span>{item.title}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Back to App */}
        <div className="border-t p-2">
          <Link
            href="/dashboard"
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
            title={sidebarCollapsed ? 'Back to App' : undefined}
          >
            <LayoutDashboard className="h-5 w-5 shrink-0" />
            {!sidebarCollapsed && <span>Back to App</span>}
          </Link>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <main className="flex-1 overflow-y-auto bg-background p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

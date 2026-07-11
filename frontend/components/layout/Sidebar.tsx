'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Target,
  Brain,
  FileText,
  FolderKanban,
  Settings,
  ChevronLeft,
  ChevronRight,
  Bell,
  CreditCard,
  Cpu,
  Link2,
  Activity,
  Shield,
  Building2,
  Users,
  Key,
  FileCode,
  LogOut,
  Zap,
} from 'lucide-react';

interface NavItem {
  title: string;
  href: string;
  icon: React.ElementType;
}

const navigation: NavItem[] = [
  { title: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { title: 'Opportunities', href: '/opportunities', icon: Target },
  { title: 'Intelligence', href: '/intelligence', icon: Brain },
  { title: 'Reports', href: '/reports', icon: FileText },
  { title: 'Projects', href: '/projects', icon: FolderKanban },
];

const accountNavigation: NavItem[] = [
  { title: 'Notifications', href: '/notifications', icon: Bell },
  { title: 'Billing', href: '/billing', icon: CreditCard },
  { title: 'AI Providers', href: '/ai-providers', icon: Cpu },
  { title: 'Connectors', href: '/connectors', icon: Link2 },
  { title: 'Monitoring', href: '/monitoring', icon: Activity },
];

const adminNavigation: NavItem[] = [
  { title: 'Admin', href: '/admin/dashboard', icon: Shield },
];

const secondaryNavigation: NavItem[] = [
  { title: 'Settings', href: '/settings', icon: Settings },
];

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
  isAdmin?: boolean;
}

export function Sidebar({ collapsed = false, onToggle, isAdmin = false }: SidebarProps) {
  const pathname = usePathname() ?? '';
  const mainNav = isAdmin ? [] : navigation;
  const middleNav = isAdmin ? adminNavigation : accountNavigation;

  return (
    <aside
      className={cn(
        'flex flex-col border-r bg-card transition-all duration-300',
        collapsed ? 'w-[70px]' : 'w-[260px]'
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between border-b px-4">
        {!collapsed && (
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <span className="text-lg font-bold text-primary-foreground">A</span>
            </div>
            <span className="font-semibold text-foreground">ATLAS</span>
          </Link>
        )}
        {collapsed && (
          <Link href="/dashboard" className="mx-auto">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <span className="text-lg font-bold text-primary-foreground">A</span>
            </div>
          </Link>
        )}
        <button
          onClick={onToggle}
          className="hidden rounded-md p-1.5 hover:bg-accent md:block"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronLeft className="h-4 w-4 text-muted-foreground" />
          )}
        </button>
      </div>

      {/* Main Navigation */}
      {mainNav.length > 0 && (
        <nav className="flex-1 space-y-1 p-2">
          {mainNav.map((item) => {
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
                title={collapsed ? item.title : undefined}
              >
                <Icon className="h-5 w-5 shrink-0" />
                {!collapsed && <span>{item.title}</span>}
              </Link>
            );
          })}
        </nav>
      )}

      {/* Middle Navigation (Account) */}
      {middleNav.length > 0 && (
        <div className="border-t p-2">
          {!collapsed && (
            <p className="px-3 py-2 text-xs font-semibold uppercase text-muted-foreground">
              {isAdmin ? 'Admin' : 'Account'}
            </p>
          )}
          {middleNav.map((item) => {
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
                title={collapsed ? item.title : undefined}
              >
                <Icon className="h-5 w-5 shrink-0" />
                {!collapsed && <span>{item.title}</span>}
              </Link>
            );
          })}
        </div>
      )}

      {/* Secondary Navigation */}
      <div className="border-t p-2">
        {secondaryNavigation.map((item) => {
          const isActive = pathname === item.href;
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
              title={collapsed ? item.title : undefined}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!collapsed && <span>{item.title}</span>}
            </Link>
          );
        })}
      </div>
    </aside>
  );
}

'use client';

import * as React from 'react';
import Link from 'next/link';
import { useAuthStore, useUser } from '@/store/auth-store';
import { Avatar } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Bell, Search, Moon, Sun } from 'lucide-react';

interface HeaderProps {
  title?: string;
  description?: string;
}

export function Header({ title, description }: HeaderProps) {
  const user = useUser();
  const { logout } = useAuthStore();
  const [isDark, setIsDark] = React.useState(false);

  React.useEffect(() => {
    const isDarkMode = document.documentElement.classList.contains('dark');
    setIsDark(isDarkMode);
  }, []);

  const toggleTheme = () => {
    document.documentElement.classList.toggle('dark');
    setIsDark(!isDark);
  };

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b bg-background/95 px-6 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex flex-col">
        {title && <h1 className="text-lg font-semibold">{title}</h1>}
        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}
      </div>

      <div className="flex items-center gap-2">
        {/* Search */}
        <Button variant="ghost" size="icon" asChild>
          <Link href="/search">
            <Search className="h-5 w-5" />
            <span className="sr-only">Search</span>
          </Link>
        </Button>

        {/* Notifications */}
        <Button variant="ghost" size="icon" asChild>
          <Link href="/notifications">
            <Bell className="h-5 w-5" />
            <span className="sr-only">Notifications</span>
          </Link>
        </Button>

        {/* Theme Toggle */}
        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {isDark ? (
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-all" />
          ) : (
            <Moon className="h-5 w-5 rotate-0 scale-100 transition-all" />
          )}
          <span className="sr-only">Toggle theme</span>
        </Button>

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-8 w-8 rounded-full">
              <Avatar name={user?.full_name} src={user?.avatar_url} size="sm" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end" forceMount>
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">{user?.full_name}</p>
                <p className="text-xs leading-none text-muted-foreground">
                  {user?.email}
                </p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <Link href="/profile">
              <DropdownMenuItem>Profile</DropdownMenuItem>
            </Link>
            <Link href="/settings">
              <DropdownMenuItem>Settings</DropdownMenuItem>
            </Link>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout} className="text-destructive">
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}

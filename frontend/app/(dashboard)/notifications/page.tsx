'use client';

import * as React from 'react';
import Link from 'next/link';
import {
  useNotifications,
  useMarkNotificationAsRead,
  useMarkAllNotificationsAsRead,
  useDeleteNotification,
} from '@/hooks/useNotifications';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Pagination } from '@/components/ui/pagination';
import { formatRelativeTime } from '@/lib/utils';
import {
  Bell,
  BellOff,
  Check,
  CheckCheck,
  Trash2,
  ExternalLink,
  AlertCircle,
  Info,
  AlertTriangle,
  Megaphone,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

const priorityIcons: Record<string, LucideIcon> = {
  low: Info,
  normal: Bell,
  high: AlertCircle,
};

const typeIcons: Record<string, LucideIcon> = {
  opportunity: Megaphone,
  market: AlertTriangle,
  alert: AlertCircle,
  system: Info,
};

export default function NotificationsPage() {
  const [page, setPage] = React.useState(1);
  const [filter, setFilter] = React.useState<'all' | 'unread'>('all');

  const { data, isLoading, isFetching } = useNotifications({
    page,
    page_size: 20,
    is_read: filter === 'unread' ? false : undefined,
  });

  const markAsReadMutation = useMarkNotificationAsRead();
  const markAllAsReadMutation = useMarkAllNotificationsAsRead();
  const deleteMutation = useDeleteNotification();

  const handleMarkAsRead = (id: string) => {
    markAsReadMutation.mutate(id);
  };

  const handleMarkAllAsRead = () => {
    markAllAsReadMutation.mutate();
  };

  const handleDelete = (id: string) => {
    deleteMutation.mutate(id);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'destructive';
      case 'low':
        return 'secondary';
      default:
        return 'default';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Notifications</h1>
          <p className="text-muted-foreground">
            {data?.unread_count ? `${data.unread_count} unread` : 'All caught up'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleMarkAllAsRead}
            disabled={!data?.unread_count || markAllAsReadMutation.isPending}
          >
            <CheckCheck className="mr-2 h-4 w-4" />
            Mark all as read
          </Button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b">
        <button
          onClick={() => {
            setFilter('all');
            setPage(1);
          }}
          className={`pb-3 px-1 text-sm font-medium transition-colors ${
            filter === 'all'
              ? 'border-b-2 border-primary text-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          All
        </button>
        <button
          onClick={() => {
            setFilter('unread');
            setPage(1);
          }}
          className={`pb-3 px-1 text-sm font-medium transition-colors ${
            filter === 'unread'
              ? 'border-b-2 border-primary text-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Unread
          {data?.unread_count ? ` (${data.unread_count})` : ''}
        </button>
      </div>

      {/* Notifications List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-3 w-1/2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <div className="space-y-2">
          {data.items.map((notification) => {
            const PriorityIcon = priorityIcons[notification.priority] || Bell;
            const TypeIcon = typeIcons[notification.type] || Bell;

            return (
              <Card
                key={notification.id}
                className={`transition-colors ${
                  !notification.is_read ? 'bg-accent/50' : ''
                }`}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <div
                      className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${
                        !notification.is_read
                          ? 'bg-primary/10 text-primary'
                          : 'bg-muted text-muted-foreground'
                      }`}
                    >
                      <TypeIcon className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <p className={`font-medium ${!notification.is_read ? '' : 'text-muted-foreground'}`}>
                              {notification.title}
                            </p>
                            <Badge variant={getPriorityColor(notification.priority)} className="text-xs">
                              {notification.priority}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {notification.message}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {formatRelativeTime(notification.created_at)}
                          </p>
                        </div>
                        <div className="flex items-center gap-1 shrink-0">
                          {!notification.is_read && (
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleMarkAsRead(notification.id)}
                              disabled={markAsReadMutation.isPending}
                              title="Mark as read"
                            >
                              <Check className="h-4 w-4" />
                            </Button>
                          )}
                          {notification.action_url && (
                            <Button variant="ghost" size="icon" asChild title="View">
                              <Link href={notification.action_url}>
                                <ExternalLink className="h-4 w-4" />
                              </Link>
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(notification.id)}
                            disabled={deleteMutation.isPending}
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card className="flex flex-col items-center justify-center py-12">
          <BellOff className="h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-4 font-semibold">No notifications</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            {filter === 'unread'
              ? "You're all caught up!"
              : "You don't have any notifications yet"}
          </p>
        </Card>
      )}

      {/* Pagination */}
      {data && data.total > 20 && (
        <Pagination
          page={page}
          pageSize={20}
          total={data.total}
          onPageChange={setPage}
        />
      )}
    </div>
  );
}

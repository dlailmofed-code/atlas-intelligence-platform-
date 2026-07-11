'use client';

import * as React from 'react';
import {
  useNotificationPreferences,
  useUpdateNotificationPreferences,
} from '@/hooks/useNotifications';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';
import { Bell, Mail, Smartphone, AlertCircle, Check } from 'lucide-react';

export default function NotificationPreferencesPage() {
  const { toast } = useToast();
  const { data: preferences, isLoading } = useNotificationPreferences();
  const updateMutation = useUpdateNotificationPreferences();

  const [localPreferences, setLocalPreferences] = React.useState({
    email: true,
    push: true,
    in_app: true,
    opportunity_alerts: true,
    market_updates: true,
    weekly_digest: true,
    security_alerts: true,
  });

  React.useEffect(() => {
    if (preferences) {
      setLocalPreferences({
        email: preferences.email,
        push: preferences.push,
        in_app: preferences.in_app,
        opportunity_alerts: preferences.opportunity_alerts,
        market_updates: preferences.market_updates,
        weekly_digest: preferences.weekly_digest,
        security_alerts: preferences.security_alerts,
      });
    }
  }, [preferences]);

  const handleToggle = (key: keyof typeof localPreferences) => {
    setLocalPreferences((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = async () => {
    try {
      await updateMutation.mutateAsync(localPreferences);
      toast({
        title: 'Preferences updated',
        description: 'Your notification preferences have been saved.',
        variant: 'default',
      });
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to update preferences. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const notificationGroups = [
    {
      title: 'Delivery Methods',
      description: 'Choose how you want to receive notifications',
      items: [
        {
          key: 'email' as const,
          label: 'Email notifications',
          description: 'Receive notifications via email',
          icon: Mail,
        },
        {
          key: 'push' as const,
          label: 'Push notifications',
          description: 'Receive push notifications on your device',
          icon: Smartphone,
        },
        {
          key: 'in_app' as const,
          label: 'In-app notifications',
          description: 'See notifications while using the app',
          icon: Bell,
        },
      ],
    },
    {
      title: 'Alert Types',
      description: 'Choose what types of alerts you want to receive',
      items: [
        {
          key: 'opportunity_alerts' as const,
          label: 'Opportunity alerts',
          description: 'Get notified about new business opportunities',
          icon: AlertCircle,
        },
        {
          key: 'market_updates' as const,
          label: 'Market updates',
          description: 'Receive updates about market trends and changes',
          icon: Bell,
        },
        {
          key: 'weekly_digest' as const,
          label: 'Weekly digest',
          description: 'Get a weekly summary of your intelligence',
          icon: Bell,
        },
        {
          key: 'security_alerts' as const,
          label: 'Security alerts',
          description: 'Important security notifications about your account',
          icon: AlertCircle,
        },
      ],
    },
  ];

  const hasChanges = preferences && JSON.stringify(localPreferences) !== JSON.stringify({
    email: preferences.email,
    push: preferences.push,
    in_app: preferences.in_app,
    opportunity_alerts: preferences.opportunity_alerts,
    market_updates: preferences.market_updates,
    weekly_digest: preferences.weekly_digest,
    security_alerts: preferences.security_alerts,
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-48" />
          <Skeleton className="mt-2 h-4 w-64" />
        </div>
        <div className="space-y-4">
          {[1, 2].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
                <Skeleton className="mt-2 h-4 w-48" />
              </CardHeader>
              <CardContent className="space-y-4">
                {[1, 2, 3].map((j) => (
                  <div key={j} className="flex items-center justify-between">
                    <div className="space-y-1">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-3 w-48" />
                    </div>
                    <Skeleton className="h-6 w-11 rounded-full" />
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Notification Preferences</h1>
        <p className="text-muted-foreground">
          Choose how and when you want to be notified
        </p>
      </div>

      {/* Preference Groups */}
      <div className="space-y-6">
        {notificationGroups.map((group) => (
          <Card key={group.title}>
            <CardHeader>
              <CardTitle>{group.title}</CardTitle>
              <CardDescription>{group.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {group.items.map((item) => (
                <div
                  key={item.key}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 rounded-full bg-muted p-2">
                      <item.icon className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <div className="space-y-0.5">
                      <Label htmlFor={item.key} className="text-base font-medium">
                        {item.label}
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        {item.description}
                      </p>
                    </div>
                  </div>
                  <Switch
                    id={item.key}
                    checked={localPreferences[item.key]}
                    onCheckedChange={() => handleToggle(item.key)}
                    disabled={updateMutation.isPending}
                  />
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Save Button */}
      {hasChanges && (
        <div className="sticky bottom-4 flex items-center justify-between rounded-lg border bg-background p-4 shadow-lg">
          <p className="text-sm text-muted-foreground">
            You have unsaved changes
          </p>
          <Button onClick={handleSave} disabled={updateMutation.isPending}>
            {updateMutation.isPending ? (
              <>
                <Check className="mr-2 h-4 w-4" />
                Saving...
              </>
            ) : (
              <>
                <Check className="mr-2 h-4 w-4" />
                Save changes
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  );
}

'use client';

import * as React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Bell,
  Moon,
  Globe,
  Shield,
  Key,
  Palette,
  CheckCircle2,
  Loader2,
} from 'lucide-react';

export default function SettingsPage() {
  const [isSaving, setIsSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(false);

  const [notifications, setNotifications] = React.useState({
    email: true,
    push: true,
    weeklyDigest: true,
    opportunities: true,
    marketUpdates: false,
  });

  const [preferences, setPreferences] = React.useState({
    theme: 'system',
    language: 'en',
    timezone: 'UTC',
  });

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account settings and preferences
        </p>
      </div>

      {saved && (
        <Alert variant="success">
          <CheckCircle2 className="h-4 w-4" />
          <AlertDescription>Settings saved successfully!</AlertDescription>
        </Alert>
      )}

      {/* Settings Tabs */}
      <Tabs defaultValue="notifications">
        <TabsList>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="appearance">Appearance</TabsTrigger>
          <TabsTrigger value="language">Language & Region</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notification Preferences
              </CardTitle>
              <CardDescription>
                Choose how and when you want to receive notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Email Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive notifications via email
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.email}
                    onChange={(e) =>
                      setNotifications((prev) => ({ ...prev, email: e.target.checked }))
                    }
                    className="h-5 w-5 rounded border-input"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Push Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive push notifications in your browser
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.push}
                    onChange={(e) =>
                      setNotifications((prev) => ({ ...prev, push: e.target.checked }))
                    }
                    className="h-5 w-5 rounded border-input"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Weekly Digest</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive a weekly summary of your intelligence
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.weeklyDigest}
                    onChange={(e) =>
                      setNotifications((prev) => ({ ...prev, weeklyDigest: e.target.checked }))
                    }
                    className="h-5 w-5 rounded border-input"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Opportunity Alerts</Label>
                    <p className="text-sm text-muted-foreground">
                      Get notified about new opportunities
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.opportunities}
                    onChange={(e) =>
                      setNotifications((prev) => ({ ...prev, opportunities: e.target.checked }))
                    }
                    className="h-5 w-5 rounded border-input"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Market Updates</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive updates about market trends
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={notifications.marketUpdates}
                    onChange={(e) =>
                      setNotifications((prev) => ({ ...prev, marketUpdates: e.target.checked }))
                    }
                    className="h-5 w-5 rounded border-input"
                  />
                </div>
              </div>

              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Preferences'
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Appearance Tab */}
        <TabsContent value="appearance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Appearance
              </CardTitle>
              <CardDescription>
                Customize the look and feel of your dashboard
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Theme</Label>
                <div className="grid grid-cols-3 gap-4">
                  <button
                    onClick={() => setPreferences((prev) => ({ ...prev, theme: 'light' }))}
                    className={`flex flex-col items-center gap-2 rounded-lg border-2 p-4 transition-colors ${
                      preferences.theme === 'light'
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <div className="h-12 w-full rounded bg-white shadow-inner" />
                    <span className="text-sm font-medium">Light</span>
                  </button>
                  <button
                    onClick={() => setPreferences((prev) => ({ ...prev, theme: 'dark' }))}
                    className={`flex flex-col items-center gap-2 rounded-lg border-2 p-4 transition-colors ${
                      preferences.theme === 'dark'
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <div className="h-12 w-full rounded bg-gray-900 shadow-inner" />
                    <span className="text-sm font-medium">Dark</span>
                  </button>
                  <button
                    onClick={() => setPreferences((prev) => ({ ...prev, theme: 'system' }))}
                    className={`flex flex-col items-center gap-2 rounded-lg border-2 p-4 transition-colors ${
                      preferences.theme === 'system'
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <div className="flex h-12 w-full rounded">
                      <div className="w-1/2 rounded-l bg-white shadow-inner" />
                      <div className="w-1/2 rounded-r bg-gray-900 shadow-inner" />
                    </div>
                    <span className="text-sm font-medium">System</span>
                  </button>
                </div>
              </div>

              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Preferences'
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Language & Region Tab */}
        <TabsContent value="language" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Language & Region
              </CardTitle>
              <CardDescription>
                Set your preferred language and regional settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-6 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label>Language</Label>
                  <Select
                    options={[
                      { value: 'en', label: 'English' },
                      { value: 'es', label: 'Español' },
                      { value: 'fr', label: 'Français' },
                      { value: 'de', label: 'Deutsch' },
                      { value: 'ar', label: 'العربية' },
                    ]}
                    value={preferences.language}
                    onChange={(e) =>
                      setPreferences((prev) => ({ ...prev, language: e.target.value }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label>Timezone</Label>
                  <Select
                    options={[
                      { value: 'UTC', label: 'UTC' },
                      { value: 'America/New_York', label: 'Eastern Time (ET)' },
                      { value: 'America/Chicago', label: 'Central Time (CT)' },
                      { value: 'America/Denver', label: 'Mountain Time (MT)' },
                      { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
                      { value: 'Europe/London', label: 'London (GMT)' },
                      { value: 'Europe/Paris', label: 'Paris (CET)' },
                      { value: 'Asia/Tokyo', label: 'Tokyo (JST)' },
                    ]}
                    value={preferences.timezone}
                    onChange={(e) =>
                      setPreferences((prev) => ({ ...prev, timezone: e.target.value }))
                    }
                  />
                </div>
              </div>

              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Preferences'
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Security
              </CardTitle>
              <CardDescription>
                Manage your account security settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Two-Factor Authentication</Label>
                    <p className="text-sm text-muted-foreground">
                      Add an extra layer of security to your account
                    </p>
                  </div>
                  <Button variant="outline" size="sm">
                    Enable
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Change Password</Label>
                    <p className="text-sm text-muted-foreground">
                      Update your password regularly for security
                    </p>
                  </div>
                  <Button variant="outline" size="sm">
                    Change
                  </Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="flex items-center gap-2">
                      <Key className="h-4 w-4" />
                      API Keys
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Manage your API keys for integrations
                    </p>
                  </div>
                  <Button variant="outline" size="sm">
                    Manage Keys
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Danger Zone */}
          <Card className="border-destructive/50">
            <CardHeader>
              <CardTitle className="text-destructive">Danger Zone</CardTitle>
              <CardDescription>
                Irreversible and destructive actions
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Delete Account</Label>
                  <p className="text-sm text-muted-foreground">
                    Permanently delete your account and all data
                  </p>
                </div>
                <Button variant="destructive" size="sm">
                  Delete Account
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

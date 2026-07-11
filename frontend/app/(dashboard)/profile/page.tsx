'use client';

import * as React from 'react';
import { useUser } from '@/store/auth-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  User,
  Mail,
  Building,
  Globe,
  Calendar,
  Edit,
  Shield,
  Bookmark,
  Activity,
} from 'lucide-react';
import { formatDate } from '@/lib/utils';

export default function ProfilePage() {
  const user = useUser();
  const [isEditing, setIsEditing] = React.useState(false);

  if (!user) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-20 w-20 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-center gap-4">
          <Avatar name={user.full_name} src={user.avatar_url} size="xl" />
          <div>
            <h1 className="text-2xl font-bold">{user.full_name}</h1>
            <div className="flex flex-wrap items-center gap-2 text-muted-foreground">
              <div className="flex items-center gap-1">
                <Mail className="h-4 w-4" />
                {user.email}
              </div>
              {user.company && (
                <div className="flex items-center gap-1">
                  <Building className="h-4 w-4" />
                  {user.company}
                </div>
              )}
            </div>
            <div className="flex items-center gap-2 pt-2">
              {user.is_verified ? (
                <Badge variant="success">Verified</Badge>
              ) : (
                <Badge variant="secondary">Not Verified</Badge>
              )}
              <Badge variant="outline">{user.language.toUpperCase()}</Badge>
            </div>
          </div>
        </div>
        <Button onClick={() => setIsEditing(!isEditing)}>
          <Edit className="mr-2 h-4 w-4" />
          Edit Profile
        </Button>
      </div>

      {/* Content Tabs */}
      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
          <TabsTrigger value="bookmarks">Bookmarks</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Profile Details */}
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Your personal information and preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label className="text-muted-foreground">Full Name</Label>
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    {isEditing ? (
                      <Input defaultValue={user.full_name} className="max-w-[300px]" />
                    ) : (
                      <span>{user.full_name}</span>
                    )}
                  </div>
                </div>
                <div className="space-y-2">
                  <Label className="text-muted-foreground">Email</Label>
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span>{user.email}</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label className="text-muted-foreground">Company</Label>
                  <div className="flex items-center gap-2">
                    <Building className="h-4 w-4 text-muted-foreground" />
                    {isEditing ? (
                      <Input defaultValue={user.company || ''} placeholder="Your company" className="max-w-[300px]" />
                    ) : (
                      <span>{user.company || 'Not specified'}</span>
                    )}
                  </div>
                </div>
                <div className="space-y-2">
                  <Label className="text-muted-foreground">Timezone</Label>
                  <div className="flex items-center gap-2">
                    <Globe className="h-4 w-4 text-muted-foreground" />
                    {isEditing ? (
                      <select
                        defaultValue={user.timezone}
                        className="max-w-[300px] rounded-md border border-input bg-background px-3 py-2"
                      >
                        <option value="UTC">UTC</option>
                        <option value="America/New_York">Eastern Time</option>
                        <option value="America/Los_Angeles">Pacific Time</option>
                        <option value="Europe/London">London</option>
                        <option value="Asia/Tokyo">Tokyo</option>
                      </select>
                    ) : (
                      <span>{user.timezone}</span>
                    )}
                  </div>
                </div>
              </div>

              {user.bio && (
                <div className="space-y-2">
                  <Label className="text-muted-foreground">Bio</Label>
                  <p className="text-sm">{user.bio}</p>
                </div>
              )}

              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="h-4 w-4" />
                Member since {formatDate(user.created_at)}
              </div>
            </CardContent>
          </Card>

          {/* Account Security */}
          <Card>
            <CardHeader>
              <CardTitle>Security</CardTitle>
              <CardDescription>Manage your account security settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100">
                    <Shield className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <p className="font-medium">Password</p>
                    <p className="text-sm text-muted-foreground">Last changed 30 days ago</p>
                  </div>
                </div>
                <Button variant="outline" size="sm">
                  Change Password
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Your recent actions on the platform</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Activity className="h-12 w-12 text-muted-foreground/50" />
                <h3 className="mt-4 font-semibold">No recent activity</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  Your activity will appear here
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="bookmarks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Saved Bookmarks</CardTitle>
              <CardDescription>Opportunities and reports you&apos;ve saved</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Bookmark className="h-12 w-12 text-muted-foreground/50" />
                <h3 className="mt-4 font-semibold">No bookmarks yet</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  Save opportunities and reports to access them quickly
                </p>
                <Button variant="outline" className="mt-4">
                  Browse Opportunities
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

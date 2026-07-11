'use client';

import * as React from 'react';
import { useAPIKeys, useRevokeAPIKey } from '@/hooks/useAdmin';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { formatRelativeTime } from '@/lib/utils';
import { Key, Plus, Copy, Trash2, RefreshCw, Eye, EyeOff } from 'lucide-react';

export default function AdminAPIKeysPage() {
  const [showKey, setShowKey] = React.useState<string | null>(null);
  const [copied, setCopied] = React.useState(false);

  const { data: apiKeys, isLoading } = useAPIKeys();
  const revokeMutation = useRevokeAPIKey();

  const handleCopy = (key: string) => {
    navigator.clipboard.writeText(key);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRevoke = (id: string) => {
    if (confirm('Are you sure you want to revoke this API key?')) {
      revokeMutation.mutate(id);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">API Keys</h1>
          <p className="text-muted-foreground">
            Manage API keys for programmatic access
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create API Key
        </Button>
      </div>

      {/* API Keys List */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="p-4">
                <Skeleton className="h-20 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : apiKeys && apiKeys.length > 0 ? (
        <div className="space-y-4">
          {apiKeys.map((apiKey) => (
            <Card key={apiKey.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="rounded-full bg-muted p-2">
                      <Key className="h-5 w-5" />
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{apiKey.name}</p>
                        <Badge variant={apiKey.is_active ? 'default' : 'secondary'}>
                          {apiKey.is_active ? 'Active' : 'Revoked'}
                        </Badge>
                      </div>
                      <p className="font-mono text-sm text-muted-foreground">
                        {apiKey.key_prefix}****{apiKey.is_active && ' (click to reveal)'}
                      </p>
                      <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
                        {apiKey.permissions.map((perm) => (
                          <Badge key={perm} variant="outline" className="text-xs">
                            {perm}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex gap-4 text-sm text-muted-foreground">
                        {apiKey.last_used && (
                          <span>Last used: {formatRelativeTime(apiKey.last_used)}</span>
                        )}
                        {apiKey.expires_at && (
                          <span>Expires: {new Date(apiKey.expires_at).toLocaleDateString()}</span>
                        )}
                        <span>Created: {formatRelativeTime(apiKey.created_at)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {apiKey.is_active && (
                      <>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleCopy(apiKey.key_prefix + '****')}
                          title="Copy key prefix"
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Rotate key"
                        >
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleRevoke(apiKey.id)}
                          disabled={revokeMutation.isPending}
                          title="Revoke key"
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
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
          <Key className="h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-4 font-semibold">No API Keys</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Create your first API key to get started
          </p>
        </Card>
      )}

      {/* Copied Toast */}
      {copied && (
        <div className="fixed bottom-4 right-4 rounded-lg bg-green-500 px-4 py-2 text-white shadow-lg">
          Copied to clipboard!
        </div>
      )}
    </div>
  );
}

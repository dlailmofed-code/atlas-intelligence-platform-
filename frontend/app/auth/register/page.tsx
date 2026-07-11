'use client';

import * as React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Eye, EyeOff, Loader2, CheckCircle2, XCircle } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading } = useAuth();
  const [showPassword, setShowPassword] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  
  const [formData, setFormData] = React.useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    company: '',
  });
  
  const [errors, setErrors] = React.useState<Record<string, string>>({});

  const passwordRequirements = [
    { id: 'length', label: 'At least 8 characters', test: (p: string) => p.length >= 8 },
    { id: 'upper', label: 'One uppercase letter', test: (p: string) => /[A-Z]/.test(p) },
    { id: 'lower', label: 'One lowercase letter', test: (p: string) => /[a-z]/.test(p) },
    { id: 'number', label: 'One number', test: (p: string) => /\d/.test(p) },
  ];

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.full_name) {
      newErrors.full_name = 'Full name is required';
    }
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else {
      const failedRequirement = passwordRequirements.find((req) => !req.test(formData.password));
      if (failedRequirement) {
        newErrors.password = failedRequirement.label;
      }
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (!validateForm()) return;
    
    try {
      await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        company: formData.company || undefined,
      });
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        setError(axiosError.response?.data?.detail || 'Registration failed. Please try again.');
      } else {
        setError('An error occurred. Please try again.');
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  return (
    <Card className="border-0 shadow-none lg:border lg:shadow-sm">
      <CardHeader className="space-y-1 px-0 lg:px-6">
        <CardTitle className="text-2xl">Create an account</CardTitle>
        <CardDescription>
          Enter your information to get started
        </CardDescription>
      </CardHeader>
      <CardContent className="px-0 lg:px-6">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="full_name">Full Name</Label>
            <Input
              id="full_name"
              name="full_name"
              type="text"
              placeholder="John Doe"
              value={formData.full_name}
              onChange={handleChange}
              error={errors.full_name}
              disabled={isLoading}
              autoComplete="name"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="company">Company (Optional)</Label>
            <Input
              id="company"
              name="company"
              type="text"
              placeholder="Your Company"
              value={formData.company}
              onChange={handleChange}
              disabled={isLoading}
              autoComplete="organization"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="you@example.com"
              value={formData.email}
              onChange={handleChange}
              error={errors.email}
              disabled={isLoading}
              autoComplete="email"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <div className="relative">
              <Input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                error={errors.password}
                disabled={isLoading}
                autoComplete="new-password"
                className="pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
            
            {/* Password Requirements */}
            <div className="mt-2 space-y-1">
              {passwordRequirements.map((req) => (
                <div
                  key={req.id}
                  className={`flex items-center gap-2 text-xs ${
                    formData.password && req.test(formData.password)
                      ? 'text-green-600'
                      : 'text-muted-foreground'
                  }`}
                >
                  {formData.password && req.test(formData.password) ? (
                    <CheckCircle2 className="h-3 w-3 text-green-600" />
                  ) : (
                    <XCircle className="h-3 w-3" />
                  )}
                  {req.label}
                </div>
              ))}
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Confirm Password</Label>
            <Input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              placeholder="••••••••"
              value={formData.confirmPassword}
              onChange={handleChange}
              error={errors.confirmPassword}
              disabled={isLoading}
              autoComplete="new-password"
            />
          </div>
          
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Creating account...
              </>
            ) : (
              'Create account'
            )}
          </Button>
        </form>
        
        <p className="mt-4 text-center text-xs text-muted-foreground">
          By creating an account, you agree to our{' '}
          <Link href="/terms" className="text-primary hover:underline">
            Terms of Service
          </Link>{' '}
          and{' '}
          <Link href="/privacy" className="text-primary hover:underline">
            Privacy Policy
          </Link>
        </p>
      </CardContent>
      <CardFooter className="px-0 lg:px-6">
        <p className="text-center text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link href="/auth/login" className="text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </CardFooter>
    </Card>
  );
}

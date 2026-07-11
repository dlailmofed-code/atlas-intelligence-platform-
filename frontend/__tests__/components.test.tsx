import { render, screen } from '@testing-library/react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Skeleton } from '@/components/ui/skeleton';

describe('UI Components', () => {
  describe('Button', () => {
    it('renders button with text', () => {
      render(<Button>Click me</Button>);
      expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
    });

    it('renders button with variant', () => {
      render(<Button variant="outline">Outline Button</Button>);
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('renders button as disabled', () => {
      render(<Button disabled>Disabled Button</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('renders button with loading state', () => {
      render(<Button isLoading>Loading</Button>);
      expect(screen.getByRole('button')).toBeDisabled();
    });
  });

  describe('Card', () => {
    it('renders card with content', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Title</CardTitle>
            <CardDescription>Test Description</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Card content</p>
          </CardContent>
        </Card>
      );
      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
      expect(screen.getByText('Card content')).toBeInTheDocument();
    });
  });

  describe('Badge', () => {
    it('renders badge with text', () => {
      render(<Badge>Test Badge</Badge>);
      expect(screen.getByText('Test Badge')).toBeInTheDocument();
    });

    it('renders badge with variant', () => {
      render(<Badge variant="default">Default</Badge>);
      expect(screen.getByText('Default')).toBeInTheDocument();
    });

    it('renders badge with destructive variant', () => {
      render(<Badge variant="destructive">Destructive</Badge>);
      expect(screen.getByText('Destructive')).toBeInTheDocument();
    });
  });

  describe('Input', () => {
    it('renders input with placeholder', () => {
      render(<Input placeholder="Enter text..." />);
      expect(screen.getByPlaceholderText('Enter text...')).toBeInTheDocument();
    });

    it('renders input with label', () => {
      render(
        <>
          <Label htmlFor="test">Test Label</Label>
          <Input id="test" placeholder="Test Input" />
        </>
      );
      expect(screen.getByText('Test Label')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Test Input')).toBeInTheDocument();
    });

    it('renders input with error', () => {
      render(<Input error="This field is required" />);
      expect(screen.getByText('This field is required')).toBeInTheDocument();
    });
  });

  describe('Avatar', () => {
    it('renders avatar with initials', () => {
      render(<Avatar name="John Doe" />);
      expect(screen.getByText('JD')).toBeInTheDocument();
    });

    it('renders avatar fallback', () => {
      render(<AvatarFallback>JD</AvatarFallback>);
      expect(screen.getByText('JD')).toBeInTheDocument();
    });
  });

  describe('Skeleton', () => {
    it('renders skeleton', () => {
      render(<Skeleton className="h-4 w-32" />);
      expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
    });
  });
});

describe('Utils', () => {
  const { formatRelativeTime, formatCurrency, formatNumber, truncate, getInitials } = require('@/lib/utils');

  describe('formatRelativeTime', () => {
    it('returns "just now" for recent dates', () => {
      const now = new Date().toISOString();
      expect(formatRelativeTime(now)).toBe('just now');
    });

    it('returns minutes ago for dates within an hour', () => {
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000).toISOString();
      expect(formatRelativeTime(fiveMinutesAgo)).toBe('5m ago');
    });

    it('returns hours ago for dates within a day', () => {
      const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString();
      expect(formatRelativeTime(twoHoursAgo)).toBe('2h ago');
    });

    it('returns days ago for dates within a week', () => {
      const threeDaysAgo = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString();
      expect(formatRelativeTime(threeDaysAgo)).toBe('3d ago');
    });
  });

  describe('formatCurrency', () => {
    it('formats currency with default USD', () => {
      expect(formatCurrency(29.99)).toBe('$29.99');
    });

    it('formats currency with custom currency', () => {
      expect(formatCurrency(29.99, 'EUR')).toContain('29.99');
    });

    it('formats large amounts', () => {
      expect(formatCurrency(1234.56)).toBe('$1,234.56');
    });
  });

  describe('formatNumber', () => {
    it('formats numbers with K suffix', () => {
      expect(formatNumber(1500)).toContain('K');
    });

    it('formats numbers with M suffix', () => {
      expect(formatNumber(1500000)).toContain('M');
    });

    it('returns string for small numbers', () => {
      expect(formatNumber(100)).toBe('100');
    });
  });

  describe('truncate', () => {
    it('truncates long strings', () => {
      const result = truncate('This is a very long string', 10);
      expect(result.length).toBeLessThan('This is a very long string'.length);
      expect(result).toContain('...');
    });

    it('returns original string for short strings', () => {
      expect(truncate('Short', 10)).toBe('Short');
    });
  });

  describe('getInitials', () => {
    it('returns initials from full name', () => {
      expect(getInitials('John Doe')).toBe('JD');
    });

    it('returns uppercase initials', () => {
      expect(getInitials('john doe')).toBe('JD');
    });

    it('limits to two characters', () => {
      expect(getInitials('John Michael Doe')).toBe('JM');
    });
  });
});

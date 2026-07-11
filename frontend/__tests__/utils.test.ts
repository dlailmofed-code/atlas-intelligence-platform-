import { describe, it, expect } from '@jest/globals';
import { cn, formatNumber, formatRelativeTime, formatDate, getInitials, generateColor } from '@/lib/utils';

describe('Utils', () => {
  describe('cn (class merging)', () => {
    it('merges class names correctly', () => {
      const result = cn('foo', 'bar');
      expect(result).toBe('foo bar');
    });

    it('handles conditional classes', () => {
      const isActive = true;
      const result = cn('base', isActive && 'active');
      expect(result).toBe('base active');
    });

    it('handles false conditions', () => {
      const isActive = false;
      const result = cn('base', isActive && 'active');
      expect(result).toBe('base');
    });

    it('merges multiple classes', () => {
      const result = cn('foo', 'bar', 'baz');
      expect(result).toBe('foo bar baz');
    });
  });

  describe('formatNumber', () => {
    it('formats numbers below 1000', () => {
      expect(formatNumber(100)).toBe('100');
      expect(formatNumber(999)).toBe('999');
    });

    it('formats thousands with K', () => {
      expect(formatNumber(1000)).toBe('1K');
      expect(formatNumber(1500)).toBe('1.5K');
      expect(formatNumber(10000)).toBe('10K');
    });

    it('formats millions with M', () => {
      expect(formatNumber(1000000)).toBe('1M');
      expect(formatNumber(1500000)).toBe('1.5M');
    });
  });

  describe('getInitials', () => {
    it('returns initials from full name', () => {
      expect(getInitials('John Doe')).toBe('JD');
      expect(getInitials('Alice Smith')).toBe('AS');
    });

    it('handles single name', () => {
      expect(getInitials('John')).toBe('J');
    });

    it('handles empty string', () => {
      expect(getInitials('')).toBe('');
    });
  });

  describe('generateColor', () => {
    it('returns a valid color class', () => {
      const color = generateColor('test');
      expect(color).toMatch(/^bg-[a-z]+-[0-9]+$/);
    });

    it('returns consistent color for same input', () => {
      const color1 = generateColor('test');
      const color2 = generateColor('test');
      expect(color1).toBe(color2);
    });

    it('returns different colors for different inputs', () => {
      const color1 = generateColor('test1');
      const color2 = generateColor('test2');
      expect(color1).not.toBe(color2);
    });
  });

  describe('formatDate', () => {
    it('formats ISO date string', () => {
      const date = '2025-01-15T10:30:00Z';
      const result = formatDate(date);
      expect(result).toContain('Jan');
      expect(result).toContain('15');
      expect(result).toContain('2025');
    });
  });
});

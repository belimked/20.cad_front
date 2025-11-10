import { describe, it, expect } from 'vitest';
import { formatFileSize } from './formatFileSize';

describe('formatFileSize', () => {
  it('should format bytes correctly', () => {
    expect(formatFileSize(0)).toBe('0 B');
    expect(formatFileSize(500)).toBe('500 B');
    expect(formatFileSize(1023)).toBe('1023 B');
  });

  it('should format kilobytes correctly', () => {
    expect(formatFileSize(1024)).toBe('1.0 KB');
    expect(formatFileSize(1536)).toBe('1.5 KB');
    expect(formatFileSize(10240)).toBe('10.0 KB');
  });

  it('should format megabytes correctly', () => {
    expect(formatFileSize(1048576)).toBe('1.0 MB');
    expect(formatFileSize(1572864)).toBe('1.5 MB');
    expect(formatFileSize(10485760)).toBe('10.0 MB');
  });

  it('should format gigabytes correctly', () => {
    expect(formatFileSize(1073741824)).toBe('1.0 GB');
    expect(formatFileSize(1610612736)).toBe('1.5 GB');
  });

  it('should handle negative numbers', () => {
    expect(formatFileSize(-1024)).toBe('-1.0 KB');
  });

  it('should handle very large numbers', () => {
    expect(formatFileSize(1099511627776)).toBe('1.0 TB');
  });
});

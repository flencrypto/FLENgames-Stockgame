import { describe, expect, it, vi, beforeEach } from 'vitest';
import {
  createSymbolSearchCache,
  normalizeSymbolSearchKeyword,
  parseSymbolSearchResponse,
  type SymbolSearchMatch,
} from './alphaVantage';

describe('normalizeSymbolSearchKeyword', () => {
  it('trims whitespace and lowercases the keyword', () => {
    expect(normalizeSymbolSearchKeyword('  AApL ')).toBe('aapl');
  });

  it('returns an empty string for whitespace-only input', () => {
    expect(normalizeSymbolSearchKeyword('   ')).toBe('');
  });
});

describe('createSymbolSearchCache', () => {
  beforeEach(() => {
    vi.useRealTimers();
  });

  it('stores and retrieves cached results within ttl', () => {
    const cache = createSymbolSearchCache({ ttlMs: 1000 });
    const matches: SymbolSearchMatch[] = [{ symbol: 'AAPL', name: 'Apple Inc.' }];

    cache.set('AAPL', matches);

    const cached = cache.get('AAPL');
    expect(cached).toEqual(matches);
    expect(cache.size()).toBe(1);
  });

  it('expires entries after ttl', () => {
    vi.useFakeTimers();
    const cache = createSymbolSearchCache({ ttlMs: 1000 });
    const matches: SymbolSearchMatch[] = [{ symbol: 'MSFT', name: 'Microsoft Corp.' }];

    cache.set('MSFT', matches);

    vi.advanceTimersByTime(1001);

    expect(cache.get('MSFT')).toBeNull();
    expect(cache.size()).toBe(0);
  });

  it('evicts the least recently used entry when max size exceeded', () => {
    vi.useFakeTimers();
    const cache = createSymbolSearchCache({ ttlMs: 5000, maxEntries: 2 });
    const aapl: SymbolSearchMatch[] = [{ symbol: 'AAPL', name: 'Apple Inc.' }];
    const msft: SymbolSearchMatch[] = [{ symbol: 'MSFT', name: 'Microsoft Corp.' }];
    const goog: SymbolSearchMatch[] = [{ symbol: 'GOOG', name: 'Alphabet Inc.' }];

    cache.set('AAPL', aapl);
    cache.set('MSFT', msft);

    // Access AAPL so MSFT becomes the least recently used entry
    expect(cache.get('AAPL')).toEqual(aapl);

    cache.set('GOOG', goog);

    expect(cache.get('MSFT')).toBeNull();
    expect(cache.get('AAPL')).toEqual(aapl);
    expect(cache.get('GOOG')).toEqual(goog);
  });
});

describe('parseSymbolSearchResponse', () => {
  it('parses valid bestMatches array', () => {
    const response = {
      bestMatches: [
        {
          '1. symbol': 'AAPL',
          '2. name': 'Apple Inc.',
          '3. type': 'Equity',
          '4. region': 'United States',
          '8. currency': 'USD',
          '9. matchScore': '0.8889',
        },
      ],
    };

    const result = parseSymbolSearchResponse(response);

    expect(result.matches).toEqual([
      {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        type: 'Equity',
        region: 'United States',
        currency: 'USD',
        matchScore: 0.8889,
      },
    ]);
    expect(result.isRateLimited).toBe(false);
    expect(result.isCacheable).toBe(true);
    expect(result.message).toBeUndefined();
  });

  it('handles rate limit note responses', () => {
    const result = parseSymbolSearchResponse({ Note: 'Please try again later.' });

    expect(result.matches).toEqual([]);
    expect(result.isRateLimited).toBe(true);
    expect(result.isCacheable).toBe(false);
    expect(result.message).toBe('Please try again later.');
  });

  it('handles error message responses', () => {
    const result = parseSymbolSearchResponse({ 'Error Message': 'Invalid API call.' });

    expect(result.matches).toEqual([]);
    expect(result.isRateLimited).toBe(false);
    expect(result.isCacheable).toBe(false);
    expect(result.message).toBe('Invalid API call.');
  });

  it('filters out invalid matches while remaining cacheable', () => {
    const response = {
      bestMatches: [
        { '1. symbol': 'TSLA', '2. name': 'Tesla Inc.' },
        { '1. symbol': '', '2. name': 'Invalid' },
        { 'not a match': true },
      ],
    };

    const result = parseSymbolSearchResponse(response);

    expect(result.matches).toEqual([
      {
        symbol: 'TSLA',
        name: 'Tesla Inc.',
      },
    ]);
    expect(result.isCacheable).toBe(true);
    expect(result.message).toBeUndefined();
  });

  it('returns an error message for unexpected structures', () => {
    const result = parseSymbolSearchResponse({ foo: 'bar' });

    expect(result.matches).toEqual([]);
    expect(result.isCacheable).toBe(false);
    expect(result.message).toBe('Unexpected response from Alpha Vantage.');
  });
});

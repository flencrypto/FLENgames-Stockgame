import { describe, expect, it } from 'vitest';

import {
  calculateSystem1Points,
  calculateSystem2Points,
  formatToYYYYMMDD,
  getNextFriday,
  getNextMarketDay,
  mergeLeagueUsers,
  normalizeUsers,
  sanitizeUserEntry,
  shouldReplaceUserEntry,
  type LeagueEntry,
  type LeagueUsers,
  type Prediction,
} from './prediction';

describe('prediction utilities', () => {
  const basePrediction: Prediction = {
    id: 1,
    symbol: 'AAPL',
    prediction: 'up',
    period: 'day',
    madeAt: '2024-01-01T00:00:00.000Z',
    targetDate: '2024-01-02',
    openPrice: 100,
    closePrice: 110,
    status: 'resolved',
    user: 'Test',
  };

  it('calculates system 1 and system 2 points', () => {
    const resolvedPredictions: Prediction[] = [
      basePrediction,
      { ...basePrediction, id: 2, closePrice: 90, prediction: 'down' },
    ];

    expect(calculateSystem1Points(resolvedPredictions)).toBe(2);
    expect(Math.round(calculateSystem2Points(resolvedPredictions))).toBe(20);
  });

  it('returns next trading day skipping weekends', () => {
    const friday = new Date('2024-03-01T12:00:00Z');
    const nextMarketDay = getNextMarketDay(friday);

    expect(nextMarketDay.getDay()).toBe(1);
    expect(formatToYYYYMMDD(nextMarketDay)).toBe('2024-03-04');
  });

  it('returns next friday from midweek date', () => {
    const monday = new Date('2024-03-04T12:00:00Z');
    const nextFriday = getNextFriday(monday);

    expect(nextFriday.getDay()).toBe(5);
    expect(formatToYYYYMMDD(nextFriday)).toBe('2024-03-08');
  });

  it('sanitizes user entries and reassesses points when predictions exist', () => {
    const entry: Partial<LeagueEntry> = {
      predictions: [
        { ...basePrediction, user: 'SomeOne', openPrice: 100, closePrice: 120 },
        { ...basePrediction, id: 3, prediction: 'down', openPrice: 50, closePrice: 40 },
      ],
      pointsS1: 99,
      updatedAt: '2024-01-01T00:00:00.000Z',
    };

    const sanitized = sanitizeUserEntry('PlayerOne', entry);
    expect(sanitized.predictions).toHaveLength(2);
    expect(sanitized.predictions.every((prediction) => prediction.user === 'PlayerOne')).toBe(true);
    expect(sanitized.pointsS1).toBe(2);
  });

  it('preserves numeric price data provided as strings when sanitizing entries', () => {
    const entry: Partial<LeagueEntry> = {
      predictions: [
        {
          ...basePrediction,
          id: 6,
          openPrice: '150.25',
          closePrice: '175.75',
          status: 'resolved',
        } as unknown as Prediction,
      ],
    };

    const sanitized = sanitizeUserEntry('StringPlayer', entry);
    expect(sanitized.predictions[0].openPrice).toBe(150.25);
    expect(sanitized.predictions[0].closePrice).toBe(175.75);
    expect(calculateSystem2Points(sanitized.predictions)).toBeGreaterThan(0);
  });

  it('decides whether to replace user entries based on freshness and score', () => {
    const existing: LeagueEntry = {
      predictions: [basePrediction],
      pointsS1: 1,
      pointsS2: 10,
      updatedAt: '2024-03-01T00:00:00.000Z',
    };

    const incoming: LeagueEntry = {
      predictions: [basePrediction, { ...basePrediction, id: 4 }],
      pointsS1: 2,
      pointsS2: 25,
      updatedAt: '2024-03-02T00:00:00.000Z',
    };

    expect(shouldReplaceUserEntry(existing, incoming)).toBe(true);
  });

  it('merges league users while tracking additions and updates', () => {
    const existing: LeagueUsers = {
      Alpha: {
        predictions: [basePrediction],
        pointsS1: 1,
        pointsS2: 10,
        updatedAt: '2024-03-01T00:00:00.000Z',
      },
    };

    const incoming = {
      Alpha: {
        predictions: [basePrediction, { ...basePrediction, id: 5 }],
        pointsS1: 3,
        pointsS2: 40,
        updatedAt: '2024-03-03T00:00:00.000Z',
      },
      Beta: {
        predictions: [basePrediction],
        pointsS1: 1,
        pointsS2: 12,
        updatedAt: '2024-03-02T00:00:00.000Z',
      },
    };

    const summary = mergeLeagueUsers(existing, incoming, { exclude: ['Ignored'] });

    expect(summary.added).toEqual(['Beta']);
    expect(summary.updated).toEqual(['Alpha']);
    expect(Object.keys(summary.mergedUsers)).toEqual(['Alpha', 'Beta']);
  });

  it('normalizes stored users and flags when mutations are required', () => {
    const stored = {
      Gamma: {
        predictions: [{ ...basePrediction, user: 'WrongUser' }],
        pointsS1: 3,
        pointsS2: 30,
        updatedAt: '2024-03-04T00:00:00.000Z',
      },
    };

    const { normalizedUsers, hasChanges } = normalizeUsers(stored);

    expect(Object.keys(normalizedUsers)).toEqual(['Gamma']);
    expect(normalizedUsers.Gamma.predictions[0].user).toBe('Gamma');
    expect(hasChanges).toBe(true);
  });
});

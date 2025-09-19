const DEFAULT_CACHE_TTL_MS = 5 * 60 * 1000;
const DEFAULT_CACHE_MAX_ENTRIES = 50;
const isRecord = (value) => typeof value === 'object' && value !== null;
const toCleanString = (value) => {
    if (typeof value === 'string') {
        const trimmed = value.trim();
        return trimmed.length > 0 ? trimmed : undefined;
    }
    return undefined;
};
const toNumber = (value) => {
    if (typeof value === 'number' && Number.isFinite(value)) {
        return value;
    }
    if (typeof value === 'string') {
        const parsed = Number.parseFloat(value);
        return Number.isFinite(parsed) ? parsed : undefined;
    }
    return undefined;
};
const cloneMatches = (matches) => {
    return matches.map((match) => ({ ...match }));
};
export const normalizeSymbolSearchKeyword = (keyword) => keyword.trim().toLowerCase();
export const createSymbolSearchCache = (options = {}) => {
    const ttlMs = typeof options.ttlMs === 'number' && options.ttlMs > 0 ? options.ttlMs : DEFAULT_CACHE_TTL_MS;
    const maxEntries = typeof options.maxEntries === 'number' && options.maxEntries > 0
        ? Math.floor(options.maxEntries)
        : DEFAULT_CACHE_MAX_ENTRIES;
    let accessSequence = 0;
    const cache = new Map();
    const set = (keyword, matches) => {
        if (maxEntries === 0) {
            return;
        }
        const normalizedKey = normalizeSymbolSearchKeyword(keyword);
        if (!normalizedKey) {
            return;
        }
        const now = Date.now();
        accessSequence += 1;
        cache.set(normalizedKey, {
            matches: cloneMatches(matches),
            expiresAt: now + ttlMs,
            lastAccessed: accessSequence,
        });
        if (cache.size > maxEntries) {
            let oldestKey = null;
            let oldestAccess = Number.POSITIVE_INFINITY;
            cache.forEach((entry, entryKey) => {
                if (entry.lastAccessed < oldestAccess) {
                    oldestAccess = entry.lastAccessed;
                    oldestKey = entryKey;
                }
            });
            if (oldestKey) {
                cache.delete(oldestKey);
            }
        }
    };
    const get = (keyword) => {
        const normalizedKey = normalizeSymbolSearchKeyword(keyword);
        if (!normalizedKey) {
            return null;
        }
        const entry = cache.get(normalizedKey);
        if (!entry) {
            return null;
        }
        const now = Date.now();
        if (entry.expiresAt <= now) {
            cache.delete(normalizedKey);
            return null;
        }
        accessSequence += 1;
        entry.lastAccessed = accessSequence;
        return cloneMatches(entry.matches);
    };
    const clear = () => {
        cache.clear();
    };
    const pruneExpired = (now = Date.now()) => {
        Array.from(cache.entries()).forEach(([entryKey, entry]) => {
            if (entry.expiresAt <= now) {
                cache.delete(entryKey);
            }
        });
    };
    const size = () => cache.size;
    return {
        get,
        set,
        size,
        clear,
        pruneExpired,
    };
};
const parseSymbolSearchMatch = (value) => {
    if (!isRecord(value)) {
        return null;
    }
    const symbol = toCleanString(value['1. symbol']);
    const name = toCleanString(value['2. name']);
    if (!symbol || !name) {
        return null;
    }
    const match = {
        symbol,
        name,
    };
    const type = toCleanString(value['3. type']);
    const region = toCleanString(value['4. region']);
    const currency = toCleanString(value['8. currency']);
    const score = toNumber(value['9. matchScore']);
    if (type) {
        match.type = type;
    }
    if (region) {
        match.region = region;
    }
    if (currency) {
        match.currency = currency;
    }
    if (typeof score === 'number') {
        match.matchScore = score;
    }
    return match;
};
export const parseSymbolSearchResponse = (value) => {
    if (!isRecord(value)) {
        return {
            matches: [],
            message: 'Unexpected response from Alpha Vantage.',
            isRateLimited: false,
            isCacheable: false,
        };
    }
    const note = toCleanString(value.Note);
    if (note) {
        return {
            matches: [],
            message: note,
            isRateLimited: true,
            isCacheable: false,
        };
    }
    const information = toCleanString(value.Information);
    if (information) {
        return {
            matches: [],
            message: information,
            isRateLimited: true,
            isCacheable: false,
        };
    }
    const errorMessage = toCleanString(value['Error Message']);
    if (errorMessage) {
        return {
            matches: [],
            message: errorMessage,
            isRateLimited: false,
            isCacheable: false,
        };
    }
    const rawBestMatches = value.bestMatches;
    if (!Array.isArray(rawBestMatches)) {
        return {
            matches: [],
            message: 'Unexpected response from Alpha Vantage.',
            isRateLimited: false,
            isCacheable: false,
        };
    }
    const matches = rawBestMatches
        .map(parseSymbolSearchMatch)
        .filter((match) => Boolean(match));
    return {
        matches,
        message: undefined,
        isRateLimited: false,
        isCacheable: true,
    };
};

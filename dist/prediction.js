export const calculateSystem1Points = (entries) => entries
    .filter((prediction) => prediction.status === 'resolved' &&
    typeof prediction.openPrice === 'number' &&
    typeof prediction.closePrice === 'number')
    .reduce((total, prediction) => {
    const actualDirection = (prediction.closePrice ?? 0) > (prediction.openPrice ?? 0) ? 'up' : 'down';
    return total + (prediction.prediction === actualDirection ? 1 : -1);
}, 0);
export const calculateSystem2Points = (entries) => entries
    .filter((prediction) => prediction.status === 'resolved' &&
    typeof prediction.openPrice === 'number' &&
    typeof prediction.closePrice === 'number' &&
    prediction.openPrice !== 0)
    .reduce((total, prediction) => {
    const change = ((prediction.closePrice ?? 0) - (prediction.openPrice ?? 0)) / (prediction.openPrice ?? 1);
    const changePercent = change * 100;
    return prediction.prediction === 'up' ? total + changePercent : total - changePercent;
}, 0);
export const formatDate = (date) => new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
}).format(date);
export const formatToYYYYMMDD = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
};
export const getNextMarketDay = (referenceDate = new Date()) => {
    const result = new Date(referenceDate);
    result.setHours(0, 0, 0, 0);
    result.setDate(result.getDate() + 1);
    while (result.getDay() === 0 || result.getDay() === 6) {
        result.setDate(result.getDate() + 1);
    }
    return result;
};
export const getNextFriday = (referenceDate = new Date()) => {
    const result = new Date(referenceDate);
    result.setHours(0, 0, 0, 0);
    const daysUntilFriday = (5 - result.getDay() + 7) % 7;
    if (daysUntilFriday === 0) {
        result.setDate(result.getDate() + 7);
    }
    else {
        result.setDate(result.getDate() + daysUntilFriday);
    }
    return result;
};
export const formatNumber = (value) => {
    if (value === null || value === undefined || value === 'None') {
        return 'N/A';
    }
    const numericValue = Number(value);
    if (Number.isNaN(numericValue)) {
        return 'N/A';
    }
    if (numericValue >= 1e9) {
        return `$${(numericValue / 1e9).toFixed(2)}B`;
    }
    if (numericValue >= 1e6) {
        return `$${(numericValue / 1e6).toFixed(2)}M`;
    }
    return `$${numericValue.toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
};
export const getValidTimestamp = (value) => {
    if (typeof value !== 'string') {
        return 0;
    }
    const parsed = Date.parse(value);
    return Number.isNaN(parsed) ? 0 : parsed;
};
const isPrediction = (entry) => {
    if (!entry || typeof entry !== 'object') {
        return false;
    }
    const candidate = entry;
    return (typeof candidate.symbol === 'string' &&
        (candidate.prediction === 'up' || candidate.prediction === 'down') &&
        (candidate.period === 'day' || candidate.period === 'week') &&
        typeof candidate.madeAt === 'string' &&
        typeof candidate.targetDate === 'string' &&
        (candidate.status === 'pending' ||
            candidate.status === 'resolved' ||
            candidate.status === undefined));
};
export const sanitizeUserEntry = (username, entry = {}) => {
    const rawPredictions = Array.isArray(entry.predictions)
        ? entry.predictions
        : [];
    const sanitizedPredictions = rawPredictions.filter(isPrediction).map((prediction) => {
        const openPrice = typeof prediction.openPrice === 'number' ? prediction.openPrice : null;
        const closePrice = typeof prediction.closePrice === 'number' ? prediction.closePrice : null;
        const status = prediction.status === 'resolved' ? 'resolved' : 'pending';
        return {
            ...prediction,
            openPrice,
            closePrice,
            status,
            user: username,
        };
    });
    const hasPredictionData = sanitizedPredictions.length > 0;
    const computedS1 = hasPredictionData
        ? Math.round(calculateSystem1Points(sanitizedPredictions))
        : Math.round(Number(entry.pointsS1 ?? 0));
    const computedS2 = hasPredictionData
        ? Math.round(calculateSystem2Points(sanitizedPredictions))
        : Math.round(Number(entry.pointsS2 ?? 0));
    const updatedAtCandidate = typeof entry.updatedAt === 'string' && entry.updatedAt
        ? entry.updatedAt
        : new Date().toISOString();
    return {
        predictions: sanitizedPredictions,
        pointsS1: computedS1,
        pointsS2: computedS2,
        updatedAt: updatedAtCandidate,
    };
};
export const shouldReplaceUserEntry = (existingEntry, incomingEntry) => {
    const existingTimestamp = getValidTimestamp(existingEntry?.updatedAt);
    const incomingTimestamp = getValidTimestamp(incomingEntry?.updatedAt);
    if (incomingTimestamp && existingTimestamp) {
        if (incomingTimestamp > existingTimestamp) {
            return true;
        }
        if (incomingTimestamp < existingTimestamp) {
            return false;
        }
    }
    else if (incomingTimestamp && !existingTimestamp) {
        return true;
    }
    else if (!incomingTimestamp && existingTimestamp) {
        return false;
    }
    const existingCount = existingEntry?.predictions?.length ?? 0;
    const incomingCount = incomingEntry?.predictions?.length ?? 0;
    if (incomingCount !== existingCount) {
        return incomingCount > existingCount;
    }
    if (incomingEntry.pointsS1 !== existingEntry.pointsS1) {
        return incomingEntry.pointsS1 > existingEntry.pointsS1;
    }
    if (incomingEntry.pointsS2 !== existingEntry.pointsS2) {
        return incomingEntry.pointsS2 > existingEntry.pointsS2;
    }
    return false;
};
export const mergeLeagueUsers = (existingUsers, incomingUsers, options = {}) => {
    const excludedUsers = new Set(options.exclude ?? []);
    const mergedUsers = { ...existingUsers };
    const summary = { added: [], updated: [], mergedUsers };
    if (!incomingUsers || typeof incomingUsers !== 'object') {
        return summary;
    }
    Object.entries(incomingUsers).forEach(([username, entry]) => {
        if (!username || excludedUsers.has(username) || !entry || typeof entry !== 'object') {
            return;
        }
        const sanitizedEntry = sanitizeUserEntry(username, entry);
        const existingEntry = mergedUsers[username];
        if (!existingEntry) {
            mergedUsers[username] = sanitizedEntry;
            summary.added.push(username);
            return;
        }
        if (shouldReplaceUserEntry(existingEntry, sanitizedEntry)) {
            mergedUsers[username] = sanitizedEntry;
            summary.updated.push(username);
        }
    });
    summary.mergedUsers = mergedUsers;
    return summary;
};
export const normalizeUsers = (storedUsers) => {
    if (!storedUsers || typeof storedUsers !== 'object') {
        return { normalizedUsers: {}, hasChanges: false };
    }
    const normalizedUsers = {};
    let hasChanges = false;
    Object.entries(storedUsers).forEach(([username, entry]) => {
        if (!username || !entry || typeof entry !== 'object') {
            return;
        }
        const sanitizedEntry = sanitizeUserEntry(username, entry);
        normalizedUsers[username] = sanitizedEntry;
        const originalEntry = entry;
        const originalPredictions = Array.isArray(originalEntry?.predictions)
            ? originalEntry.predictions
            : [];
        if (!originalEntry.updatedAt ||
            sanitizedEntry.updatedAt !== originalEntry.updatedAt ||
            sanitizedEntry.predictions.length !== originalPredictions.length) {
            hasChanges = true;
            return;
        }
        sanitizedEntry.predictions.forEach((prediction, index) => {
            const originalPrediction = originalPredictions[index];
            if (!originalPrediction || originalPrediction.user !== username) {
                hasChanges = true;
            }
        });
    });
    return { normalizedUsers, hasChanges };
};

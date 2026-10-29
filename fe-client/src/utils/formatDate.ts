const DATE_ONLY = /^(\d{4})-(\d{2})-(\d{2})$/;

// `new Date("YYYY-MM-DD")` is UTC midnight, which renders as the previous
// day west of UTC. Date-only values are calendar days, so read them as local.
const parseDate = (value: Date | string): Date => {
    if (typeof value === 'string') {
        const match = DATE_ONLY.exec(value);
        if (match) {
            const [, y, m, d] = match;
            return new Date(Number(y), Number(m) - 1, Number(d));
        }
    }
    return new Date(value);
};

// Local calendar day as YYYY-MM-DD (toISOString would give the UTC day).
const toLocalDateString = (date: Date = new Date()): string => {
    const pad = (n: number) => String(n).padStart(2, "0");
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
};

const formatDate = (date: Date | string) => {
    return parseDate(date).toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
    });
};

const formatTime = (date: Date | string) => {
    return parseDate(date).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
    });
};

export {formatDate, formatTime, parseDate, toLocalDateString};

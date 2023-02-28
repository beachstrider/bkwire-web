import isValidDate from 'date-fns/isValid';

const minDate = '1970-01-01';
const locales: Record<string, [string, string]> = {
  seconds: ['1m', '1m'],
  minute: ['1m', '%dm'],
  hour: ['1h', '%dh'],
  day: ['1d', '%dd'],
  month: ['1mo', '%dmo'],
  year: ['1y', '%dy'],
};

export const formatDateRelative = (date: Date, prefix = '', suffix = '') => {
  const separator = ' ';
  const seconds = Math.floor((+new Date() - +new Date(date)) / 1000);
  const intervals = {
    year: seconds / (60 * 60 * 24 * 365.25),
    month: seconds / (60 * 60 * 24 * (365.25 / 12)),
    day: seconds / (60 * 60 * 24),
    hour: seconds / (60 * 60),
    minute: seconds / 60,
  };

  let words = prefix + separator;
  let interval = 0;
  let distance = locales.seconds[0];

  Object.entries(intervals).some(([key, value]) => {
    interval = Math.floor(value);

    if (interval === 1) {
      distance = locales[key][0];
      return true;
    } else if (interval > 1) {
      distance = locales[key][1];
      return true;
    }
    return false;
  });

  distance = distance.replace(/%d/i, interval.toString());
  words += distance + separator + suffix;

  return words.trim();
};

export const toDateSafe = (value?: string | Date) => {
  const date = new Date(value || minDate);
  return isValidDate(date) ? date : new Date(minDate);
};

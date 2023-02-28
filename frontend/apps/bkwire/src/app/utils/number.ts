export const formatKMB = (num: number) => {
  const item = [
    { value: 1e18, symbol: 'Q5' },
    { value: 1e15, symbol: 'Q4' },
    { value: 1e12, symbol: 'T' },
    { value: 1e9, symbol: 'B' },
    { value: 1e6, symbol: 'M' },
    { value: 1e3, symbol: 'K' },
    { value: 1, symbol: '' },
  ]
    .slice()
    .find((item) => Math.abs(num) >= item.value);

  return item
    ? `${(Math.abs(num) / item.value)
      .toFixed(0)
      .replace(/\.0+$|(\.[0-9]*[1-9])0+$/, '$1')}${item.symbol}${num < 0 ? '+' : ''
    }`
    : '0';
};

export const formatRange = ({ min, max }: { min: number; max: number }) => {
  if (max !== null && max > 0 && min > max) {
    throw new Error('Invalid range');
  }

  return max < 0 ? `> ${min}` : `${min} - ${max}`;
};

export const formatRangeKMB = ({ min, max }: { min: number; max: number }) => {
  if (max !== null && max > 0 && min > max) {
    throw new Error('Invalid range');
  }

  if (min === max) {
    max = -1;
  }

  min = Math.floor(min / 10) * 10;

  const minFormatted = formatKMB(min);

  if (max < 0) {
    return `${minFormatted}+`;
  }

  const maxFormatted = formatKMB(max);

  return `${minFormatted} - ${maxFormatted}`;
};

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
});

export const formatAmount = (amount: number) => {
  return currencyFormatter.format(amount);
};

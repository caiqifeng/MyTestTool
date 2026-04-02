import { formatPrice } from './price';

describe('formatPrice', () => {
  test('formats integer price with yuan symbol', () => {
    expect(formatPrice(15)).toBe('¥15.00');
  });

  test('formats decimal price with two decimal places', () => {
    expect(formatPrice(19.99)).toBe('¥19.99');
  });

  test('rounds to two decimal places', () => {
    expect(formatPrice(12.345)).toBe('¥12.35');
  });

  test('handles zero', () => {
    expect(formatPrice(0)).toBe('¥0.00');
  });

  test('handles negative prices (for discounts)', () => {
    expect(formatPrice(-5.5)).toBe('-¥5.50');
  });
});
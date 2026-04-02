export function formatPrice(amount: number): string {
  const sign = amount < 0 ? '-' : '';
  const absolute = Math.abs(amount);
  return `${sign}¥${absolute.toFixed(2)}`;
}
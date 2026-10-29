import snapshot from '../../public/data/usage.json';

export const usage = snapshot;
export const compact = (value: number) => new Intl.NumberFormat('en', {
  notation: 'compact', maximumFractionDigits: 1,
}).format(value);
export const integer = (value: number) => new Intl.NumberFormat('en').format(value);
export const cost = (value: string | number) => new Intl.NumberFormat('en', {
  style: 'currency', currency: 'USD', maximumFractionDigits: 2,
}).format(Number(value));
export const updatedAt = snapshot.generatedAt.slice(0, 16).replace('T', ' ');

export function heatmapDays() {
  const today = new Date(`${snapshot.generatedAt.slice(0, 10)}T00:00:00Z`);
  const end = new Date(today);
  end.setUTCDate(end.getUTCDate() + (7 - end.getUTCDay()) % 7);
  const start = new Date(end);
  start.setUTCDate(start.getUTCDate() - 370);
  const byDate = new Map(snapshot.daily.map(day => [day.date, day]));
  const days = Array.from({ length: 371 }, (_, index) => {
    const date = new Date(start);
    date.setUTCDate(date.getUTCDate() + index);
    const key = date.toISOString().slice(0, 10);
    return { date: key, value: byDate.get(key)?.totalTokens ?? 0,
      requests: byDate.get(key)?.requests ?? 0, future: date > today };
  });
  const active = days.map(day => day.value).filter(Boolean).sort((a, b) => a - b);
  const thresholds = [.25, .5, .75].map(q => active[Math.floor((active.length - 1) * q)] ?? 0);
  return days.map(day => ({ ...day, level: day.value === 0 ? 0 : 1 + thresholds.filter(t => day.value > t).length }));
}

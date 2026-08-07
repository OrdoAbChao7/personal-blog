import { getCollection, type CollectionEntry } from 'astro:content';

/** 按日期倒序 */
export function sortByDate<T extends { data: { date: string } }>(items: T[]): T[] {
  return [...items].sort((a, b) => b.data.date.localeCompare(a.data.date));
}

/** 获取项目（默认排除草稿） */
export async function getProjects(opts: { featured?: boolean; status?: string } = {}) {
  const all = await getCollection('projects', ({ data }) => !data.draft);
  let items = sortByDate(all);
  if (opts.featured) items = items.filter((p) => p.data.featured);
  if (opts.status) items = items.filter((p) => p.data.status === opts.status);
  return items;
}

/** 获取研究文章 */
export async function getResearch(opts: { featured?: boolean; category?: string } = {}) {
  const all = await getCollection('research', ({ data }) => !data.draft);
  let items = sortByDate(all);
  if (opts.featured) items = items.filter((p) => p.data.featured);
  if (opts.category) items = items.filter((p) => p.data.category === opts.category);
  return items;
}

/** 获取工程日志 */
export async function getEngineering() {
  const all = await getCollection('engineering', ({ data }) => !data.draft);
  return sortByDate(all);
}

/** 格式化日期：2026-08-05 → 2026.08.05 */
export function formatDate(dateStr: string): string {
  return dateStr.replaceAll('-', '.');
}

export type Project = CollectionEntry<'projects'>;
export type Research = CollectionEntry<'research'>;
export type Engineering = CollectionEntry<'engineering'>;

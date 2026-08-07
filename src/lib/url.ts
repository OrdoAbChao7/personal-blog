// 统一处理 base 前缀，兼容 GitHub Pages 部署
export function url(path = '/'): string {
  const base = import.meta.env.BASE_URL || '/';

  const cleanBase = base.endsWith('/')
    ? base.slice(0, -1)
    : base;

  const cleanPath = path.startsWith('/')
    ? path
    : `/${path}`;

  return `${cleanBase}${cleanPath}`;
}
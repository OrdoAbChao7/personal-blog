// 统一处理 base 前缀，兼容 GitHub Pages 部署
// import.meta.env.BASE_URL 由 astro.config.mjs 的 base 决定（如 '/personal-blog/'）
export function url(path = '/'): string {
  const base = import.meta.env.BASE_URL;
  if (path === '/' || path === '') return base;
  const clean = path.startsWith('/') ? path.slice(1) : path;
  return `${base}${clean}`;
}

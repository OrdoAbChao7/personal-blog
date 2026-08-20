export interface ReadingStats {
  wordCount: number;
  minutes: number;
}

/**
 * Estimate readable content from Markdown/MDX source.
 * Code, imports, frontmatter, URLs, and markup syntax do not contribute to reading time.
 */
export function getReadingStats(source = ''): ReadingStats {
  const readableText = source
    .replace(/^---[\s\S]*?---\s*/m, '')
    .replace(/^\s*(import|export)\s.+$/gm, '')
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`[^`]*`/g, '')
    .replace(/!?(\[[^\]]*\])\([^)]*\)/g, '$1')
    .replace(/<[^>]*>/g, ' ')
    .replace(/[>#*_~|]/g, ' ')
    .replace(/[-–—]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const chineseCharacters = (readableText.match(/[\u3400-\u9fff]/g) || []).length;
  const latinWords = (
    readableText
      .replace(/[\u3400-\u9fff]/g, ' ')
      .match(/\b[\p{L}\p{N}][\p{L}\p{N}'-]*\b/gu) || []
  ).length;

  const wordCount = chineseCharacters + latinWords;
  const minutes = Math.max(1, Math.ceil(chineseCharacters / 400 + latinWords / 200));

  return { wordCount, minutes };
}

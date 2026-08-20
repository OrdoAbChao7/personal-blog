import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

// 项目作品集
const projects = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './content/projects' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    category: z.enum(['hardware', 'hardware-ai', 'software', 'research']),
    techStack: z.array(z.string()).default([]),
    status: z.enum(['idea', 'building', 'shipped', 'archived']).default('building'),
    github: z.string().url().optional(),
    demo: z.string().url().optional(),
    cover: z.string().optional(),
    featured: z.boolean().default(false),
    startDate: z.string().optional(),
    endDate: z.string().nullable().optional(),
    date: z.string(),
    draft: z.boolean().default(false),
  }),
});

// 工程实践日志
const engineering = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './content/engineering' }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    hardware: z.string().optional(),
    software: z.string().optional(),
    difficulty: z.number().min(1).max(5).default(3),
    date: z.string(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

// 技术与社会思考
const thinking = defineCollection({
  loader: glob({ pattern: '**/*.mdx', base: './content/thinking' }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    category: z.enum(['ai-trend', 'society', 'startup', 'tech-analysis']),
    date: z.string(),
    tags: z.array(z.string()).default([]),
    cover: z.string().optional(),
    featured: z.boolean().default(false),
    draft: z.boolean().default(false),
  }),
});

export const collections = { projects, engineering, thinking };

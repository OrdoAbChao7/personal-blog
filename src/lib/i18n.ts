export type Lang = 'zh' | 'en';

/** UI 外壳文案字典（MDX 内容不翻译，保持中文） */
export const translations: Record<Lang, Record<string, string>> = {
  zh: {
    'nav.home': '首页',
    'nav.projects': '项目',
    'nav.engineering': '工程',
    'nav.thinking': '思考',
    'nav.about': '关于',

    // 首页 · 自我介绍式
    'home.greeting': 'Hi, 我是 JJ。',
    'home.intro':
      '武汉理工大学光电信息科学与工程本科生，2028 届。聚焦 Agent/RAG 开发与系统可靠性，向 n8n、DeepTutor 等开源项目贡献 7 个合并 PR，记录从真实工程协作到系统评测的实践。',
    'home.stackLabel': '当前栈',
    'home.currently': '代表项目与贡献',
    'home.currentlySub': '（更新于 2026.10.16）',
    'home.writing': '近期写作',
    'home.writingThinking': '思考',
    'home.writingEngineering': '工程',
    'home.elsewhere': '其他地方',
    'home.viewAll': '全部 →',
    'home.github': 'GitHub',
    'home.email': 'Email',
    'home.empty': '暂无内容',

    // 列表页
    'projects.eyebrow': '/projects',
    'projects.title': '项目',
    'projects.sub': '做过的东西。硬件、软件与研究的交叉实验。',
    'projects.count': '个',
    'thinking.eyebrow': '/thinking',
    'thinking.title': '思考',
    'thinking.sub': '技术趋势、产业观察与思考。',
    'thinking.count': '篇',
    'engineering.eyebrow': '/engineering',
    'engineering.title': '工程',
    'engineering.sub': '工程实践日志。踩坑、调试与硬件记录。',
    'engineering.count': '篇',

    'footer.tag': 'Technology · Investment · Thinking',
    'footer.built': 'Built with Astro',
  },
  en: {
    'nav.home': 'Home',
    'nav.projects': 'Projects',
    'nav.engineering': 'Engineering',
    'nav.thinking': 'Thinking',
    'nav.about': 'About',

    // Home · self-intro style
    'home.greeting': 'Hi, I\'m JJ.',
    'home.intro':
      'Optoelectronic Information Engineering undergraduate at Wuhan University of Technology, class of 2028. Focusing on Agent/RAG runtime reliability with 7 merged PRs to n8n, DeepTutor, and more.',
    'home.stackLabel': 'Stack',
    'home.currently': 'Selected projects & contributions',
    'home.currentlySub': '(updated 2026.10.16)',
    'home.writing': 'Recent writing',
    'home.writingThinking': 'Thinking',
    'home.writingEngineering': 'Engineering',
    'home.elsewhere': 'Elsewhere',
    'home.viewAll': 'all →',
    'home.github': 'GitHub',
    'home.email': 'Email',
    'home.empty': 'Nothing yet',

    // List pages
    'projects.eyebrow': '/projects',
    'projects.title': 'Projects',
    'projects.sub': 'What I have built. Experiments across hardware, software, and research.',
    'projects.count': 'items',
    'thinking.eyebrow': '/thinking',
    'thinking.title': 'Thinking',
    'thinking.sub': 'Tech trends, industry observations, and reflections.',
    'thinking.count': 'posts',
    'engineering.eyebrow': '/engineering',
    'engineering.title': 'Engineering',
    'engineering.sub': 'Engineering logs. Pitfalls, debugging, and hardware notes.',
    'engineering.count': 'posts',

    'footer.tag': 'Technology · Investment · Thinking',
    'footer.built': 'Built with Astro',
  },
};

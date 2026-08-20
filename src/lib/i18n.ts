export type Lang = 'zh' | 'en';

/** UI 外壳文案字典（MDX 内容不翻译，保持中文） */
export const translations: Record<Lang, Record<string, string>> = {
  zh: {
    'nav.home': '首页',
    'nav.projects': '项目',
    'nav.engineering': '工程',
    'nav.thinking': '思考',

    // 首页 · 自我介绍式
    'home.greeting': 'Hi, 我是 JJ。',
    'home.intro':
      '光电信息科学与工程本科生。在端侧 AI、近红外光谱传感与产业研究的交叉地带造东西、写东西。',
    'home.stackLabel': '当前栈',
    'home.currently': '正在构建',
    'home.currentlySub': '（在做的几个原型，状态实时）',
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

    // Home · self-intro style
    'home.greeting': 'Hi, I\'m JJ.',
    'home.intro':
      'Undergrad in Optoelectronic Information Engineering. Building and writing at the intersection of edge AI, NIR spectroscopy sensing, and industry research.',
    'home.stackLabel': 'Stack',
    'home.currently': 'Currently',
    'home.currentlySub': '(in-progress prototypes, status live)',
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

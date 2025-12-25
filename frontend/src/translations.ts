/**
 * Multi-language support for Todo AI Chatbot
 * Languages: English, Urdu, Chinese
 */

export type Language = 'en' | 'ur' | 'zh';

export interface Translations {
  // App Header
  appTitle: string;
  appSubtitle: string;

  // Authentication
  loginPlaceholder: string;
  loginButton: string;
  logoutButton: string;

  // Welcome Message
  welcomeTitle: string;
  welcomeDescription: string;
  exampleAdd: string;
  exampleList: string;
  exampleComplete: string;
  exampleDelete: string;
  exampleUpdate: string;

  // Chat Interface
  inputPlaceholder: string;
  sendButton: string;

  // Language Selector
  selectLanguage: string;
  languageEnglish: string;
  languageUrdu: string;
  languageChinese: string;

  // Error Messages
  errorPrefix: string;
}

export const translations: Record<Language, Translations> = {
  // English
  en: {
    appTitle: '🤖 Todo AI Chatbot',
    appSubtitle: 'Natural language task management',

    loginPlaceholder: "Enter auth token (use 'test' for demo)",
    loginButton: 'Login',
    logoutButton: 'Logout',

    welcomeTitle: '👋 Welcome!',
    welcomeDescription: 'I can help you manage your tasks using natural language.',
    exampleAdd: '"Add a task to buy groceries"',
    exampleList: '"Show me all my tasks"',
    exampleComplete: '"Mark task 1 as complete"',
    exampleDelete: '"Delete task 2"',
    exampleUpdate: '"Update task 3 to call mom at 6pm"',

    inputPlaceholder: "Type your message... (e.g., 'Add a task to buy groceries')",
    sendButton: 'Send',

    selectLanguage: 'Language',
    languageEnglish: 'English',
    languageUrdu: 'اردو',
    languageChinese: '中文',

    errorPrefix: '⚠️ Error:',
  },

  // Urdu
  ur: {
    appTitle: '🤖 ٹُوڈو اے آئی چیٹ بوٹ',
    appSubtitle: 'قدرتی زبان میں کام کی فہرست کا انتظام',

    loginPlaceholder: "توثیقی ٹوکن درج کریں (ڈیمو کے لیے 'test' استعمال کریں)",
    loginButton: 'لاگ ان',
    logoutButton: 'لاگ آؤٹ',

    welcomeTitle: '👋 خوش آمدید!',
    welcomeDescription: 'میں قدرتی زبان استعمال کرتے ہوئے آپ کے کاموں کو منظم کرنے میں مدد کر سکتا ہوں۔',
    exampleAdd: '"گروسری خریدنے کا کام شامل کریں"',
    exampleList: '"میرے تمام کام دکھائیں"',
    exampleComplete: '"کام نمبر 1 مکمل کریں"',
    exampleDelete: '"کام نمبر 2 حذف کریں"',
    exampleUpdate: '"کام نمبر 3 کو ماں کو 6 بجے فون کرنا میں تبدیل کریں"',

    inputPlaceholder: "اپنا پیغام ٹائپ کریں... (مثال: 'گروسری خریدنے کا کام شامل کریں')",
    sendButton: 'بھیجیں',

    selectLanguage: 'زبان',
    languageEnglish: 'English',
    languageUrdu: 'اردو',
    languageChinese: '中文',

    errorPrefix: '⚠️ خرابی:',
  },

  // Chinese (Simplified)
  zh: {
    appTitle: '🤖 待办事项 AI 聊天机器人',
    appSubtitle: '自然语言任务管理',

    loginPlaceholder: "输入认证令牌（演示使用 'test'）",
    loginButton: '登录',
    logoutButton: '登出',

    welcomeTitle: '👋 欢迎！',
    welcomeDescription: '我可以帮助您使用自然语言管理任务。',
    exampleAdd: '"添加购买杂货的任务"',
    exampleList: '"显示我所有的任务"',
    exampleComplete: '"将任务 1 标记为完成"',
    exampleDelete: '"删除任务 2"',
    exampleUpdate: '"将任务 3 更新为下午6点给妈妈打电话"',

    inputPlaceholder: "输入您的消息...（例如：'添加购买杂货的任务'）",
    sendButton: '发送',

    selectLanguage: '语言',
    languageEnglish: 'English',
    languageUrdu: 'اردو',
    languageChinese: '中文',

    errorPrefix: '⚠️ 错误：',
  },
};

// Helper function to get current translation
export const getTranslation = (lang: Language): Translations => {
  return translations[lang] || translations.en;
};

// Helper to detect browser language
export const detectLanguage = (): Language => {
  const browserLang = navigator.language.toLowerCase();

  if (browserLang.startsWith('ur')) return 'ur';
  if (browserLang.startsWith('zh')) return 'zh';
  return 'en'; // Default to English
};

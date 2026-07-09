# 🌐 翻译 Skills 合集

无论是静态网站还是动态网站，都能够识别和正确的翻译成国际化多语言，适合codex、claude code、workbuddy等 agent skills

两个**互补不重叠**的国际化/本地化 skill，覆盖「静态内容站点」和「编程框架源码」两大场景。
配套 AI 编码助手（ZCode / Claude / Trae 等）使用。

---

## 该用哪个？先看项目里有什么文件

| 项目特征 | 选哪个 skill |
|---------|------------|
| 只有 `.html` / `.css` / 图片，无源码、无构建配置 | ✅ **html-i18n** |
| 有 `.js` / `.jsx` / `.vue` / `.php` / `.py` / `.java` 等源码 | ✅ **i18n-helper** |
| 有 `package.json` / `composer.json` / `requirements.txt` | ✅ **i18n-helper** |
| React / Vue / Angular / Laravel / Symfony / WordPress 项目 | ✅ **i18n-helper** |
| 书籍、文档站、博客、官网落地页（纯 HTML） | ✅ **html-i18n** |

> **一句话区分**：要在代码里写 `t()` / `__()` 翻译函数 → `i18n-helper`；
> 要把 HTML 文件复制成多语言目录 → `html-i18n`。

---

## 1. html-i18n — 静态 HTML 站点翻译

**适用**：书籍、文档站、博客、官网落地页等**纯静态多页 HTML 站点**。

**做什么**：
- 扫描 HTML 提取可翻译文本（跳过代码块、URL、CSS）
- 生成各语言独立 HTML 目录（`en/`、`ja/`、`zh-TW/` 等）
- 共享 css 与图片资源，零 JS 依赖，SEO 友好
- 原中文版 HTML **零改动**

**产出结构**：
```
你的站点/
├─ index.html        (原版，保持不动)
├─ style.css         (多语言共享)
├─ assets/           (图片等资源，多语言共享)
├─ locales/
│  ├─ zh-CN.json     (翻译源)
│  ├─ en-US.json     (英文译文)
│  └─ ...
├─ en/               ← 英文站
├─ ja/               ← 日文站
└─ zh-TW/            ← 繁中站
```

**核心脚本**（仅依赖 Python 标准库，无需 pip）：

| 脚本 | 作用 |
|------|------|
| `scripts/extract.py` | 扫描 HTML → 生成翻译源 `zh-CN.json` |
| `scripts/apply.py` | 用译文回填 → 生成各语言 HTML 目录 |
| `scripts/check.py` | 检查翻译完整性（缺失/空值/完成度%） |
| `scripts/htmlscanner.py` | extract 与 apply 共用的扫描器 |
| `scripts/zhconv.py` | 简→繁转换（生成 zh-TW 用） |

**使用**：
```bash
# 1. 提取翻译源
python skills/html-i18n/scripts/extract.py 你的站点/

# 2. 复制 zh-CN.json 改名并填译文（如 en-US.json）

# 3. 应用生成各语言目录
python skills/html-i18n/scripts/apply.py 你的站点/ 你的站点/locales/en-US.json 你的站点/en --lang en

# 4. 检查完整性
python skills/html-i18n/scripts/check.py 你的站点/locales
```

---

## 2. i18n-helper — 编程框架源码国际化

**适用**：需要写翻译函数的**源码项目**。

**支持的语言/框架**：
- **前端**：React (`react-intl`)、Vue (`vue-i18n`)、Angular (`@ngx-translate`)、i18next
- **PHP**：Laravel (`__()` / `trans()`)、Symfony (`$translator->trans()`)、WordPress (`__()` / `_e()`)、原生 gettext
- **其它**：Python (gettext / Flask-Babel)、Java (ResourceBundle / Spring)、Go (go-i18n)

**做什么**：
- 扫描源码里的硬编码中/英文本
- 按框架生成对应语言文件（JSON / YAML / PO / XLIFF / PHP 数组 / Properties）
- 把硬编码替换成翻译函数调用（`t()` / `__()` / `trans()` 等）
- 检查翻译完整性

**PHP 各框架对照**（详见 `references/php-i18n.md`）：

| 框架 | 替换函数 | 语言文件 | 提取命令 |
|------|---------|---------|---------|
| Laravel | `__()` `trans()` | PHP 数组 / JSON | `php artisan lang:publish` |
| Symfony | `$translator->trans()` | XLIFF | `php bin/console translation:extract` |
| WordPress | `__()` `_e()` `_n()` | PO / MO | `wp i18n make-pot` |
| 原生 gettext | `gettext()` `_()` | PO / MO | `xgettext` |

---

## 安装

将本仓库的两个 skill 目录复制到你的 skills 目录即可被自动发现：

```bash
# 方式一：用户级（所有项目可用）
cp -r skills/html-i18n  ~/.agents/skills/
cp -r skills/i18n-helper ~/.agents/skills/

# 方式二：项目级（仅当前项目可用）
cp -r skills/html-i18n  你的项目/.agents/skills/
cp -r skills/i18n-helper 你的项目/.agents/skills/
```

支持的标准发现路径（优先级从高到低）：
- `<项目>/.zcode/skills/<name>/SKILL.md`
- `<项目>/.agents/skills/<name>/SKILL.md`
- `~/.zcode/skills/<name>/SKILL.md`
- `~/.agents/skills/<name>/SKILL.md`

---

## 目录结构

```
.claude/
├─ README.md                          ← 本文件
└─ skills/
   ├─ html-i18n/                      ← 静态 HTML 站点翻译
   │  ├─ SKILL.md
   │  ├─ references/
   │  │  ├─ extraction-rules.md       (提取规则 + 边界情况)
   │  │  └─ glossary.md               (术语表)
   │  └─ scripts/
   │     ├─ extract.py
   │     ├─ apply.py
   │     ├─ check.py
   │     ├─ htmlscanner.py
   │     └─ zhconv.py
   └─ i18n-helper/                    ← 编程框架源码国际化
      ├─ SKILL.md
      └─ references/
         └─ php-i18n.md               (PHP 4 大模式详解)
```

---

## License

MIT



## 感谢

- 参考skill: https://github.com/laolaoshiren/claude-code-skills-zh/blob/main/skills/i18n-helper/SKILL.md
- Linux.do佬友支持: https://linux.do/


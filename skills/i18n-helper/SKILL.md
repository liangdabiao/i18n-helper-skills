---
name: i18n-helper
description: 国际化/本地化助手 — 扫描代码中的硬编码文本、生成 i18n 配置、批量翻译
---

# 🌍 i18n-helper — 国际化/本地化助手

## 触发条件
当用户要求以下操作时激活此技能：
- 扫描代码中的硬编码中文/英文文本
- 为项目添加国际化支持（i18n）
- 批量提取和翻译语言文件
- 检查翻译完整性（缺失 key 检测）

## 工作流程

### 1. 项目分析
- 检测项目类型（React/Vue/Angular/Node.js/Python/Java/Go/PHP 等）
- 识别已使用的 i18n 框架（react-intl, vue-i18n, i18next, gettext 等）
- 扫描源代码目录结构
- **PHP 项目识别信号**（命中任一即按 PHP 流程处理，详见 [references/php-i18n.md](references/php-i18n.md)）：
  - `composer.json` → 看 `require` 是否含 `laravel/framework`、`symfony/translation`、`wordpress/*`
  - `wp-load.php` / `wp-config.php` → WordPress
  - `artisan` 文件 + `app/` 目录 → Laravel
  - `src/Kernel.php` + `translations/` 目录 → Symfony
  - `setlocale()` + `bindtextdomain()` → 原生 gettext

### 2. 硬编码文本扫描
- 在 `.js/.jsx/.ts/.tsx/.vue/.py/.java/.go/.php/.phtml/.blade.php` 等文件中搜索硬编码字符串
- 排除：变量名、URL、正则表达式、import/use 路径、日志调试信息、SQL 语句
- 标记：用户可见的 UI 文本、错误提示、通知消息
- **PHP 特别注意**：`.php` 文件常 HTML 与 PHP 混排，扫描时区分「HTML 文本节点」与「PHP 字符串字面量」；Blade 模板（`.blade.php`）还要处理 `{{ }}` `{!! !!}` 内的输出。详见 [references/php-i18n.md](references/php-i18n.md)。

### 3. 语言文件生成
根据项目框架生成对应格式：
- **JSON** (i18next/react-intl): `{ "key": "value" }`
- **YAML** (vue-i18n): `key: value`
- **PO/POT** (gettext/WordPress): 标准格式
- **Properties** (Java): `key=value`
- **PHP 数组** (Laravel): `<?php return ['key' => 'value']; ?>`
- **XLIFF** (Symfony): `messages.en.xlf`（XML 格式，带 `trans-unit`）

> PHP 项目按框架选格式：Laravel→PHP 数组/JSON、Symfony→XLIFF、WordPress/原生 gettext→PO/MO。
> 各格式样例见 [references/php-i18n.md](references/php-i18n.md)。

### 3.5 提取已有文本（PHP 优先用框架官方工具）
- **优先用框架自带的提取命令**，不要手写正则全量扫描：
  - Laravel: `php artisan lang:publish`（发布语言文件）+ 手动/包提取 key
  - Symfony: `php bin/console translation:extract en --dir=src`
  - WordPress: `wp i18n make-pot . languages/plugin.pot`（WP-CLI）或 `wp-pot`(npm)
  - 原生 gettext: `xgettext --language=PHP --from-code=UTF-8 -o messages.po *.php`
- 本 skill 的「硬编码扫描」（第 2 步）用于**补充发现**官方工具漏掉的、或尚未国际化的文本

### 4. 代码替换
- 将硬编码文本替换为 i18n 函数调用
- 保持原有格式和变量插值
- 示例：
  ```javascript
  // 替换前
  alert('保存成功');
  // 替换后
  alert(t('alert.saveSuccess'));
  ```
  ```php
  // PHP（Laravel）替换前
  echo '欢迎，' . $name;
  // 替换后（短键 + 占位符）
  echo __('Welcome, :name', ['name' => $name]);
  // 或用 lang 文件里的短键
  echo __('messages.welcome', ['name' => $name]);
  ```
  ```php
  // PHP（WordPress）替换前
  <h1>文章标题</h1>
  // 替换后（必须传 text domain）
  <h1><?php _e('Post Title', 'my-theme'); ?></h1>
  ```
- **PHP 各框架的替换函数不同**，切勿混用：Laravel 用 `__()`/`trans()`、Symfony 用 `$translator->trans()`、WordPress 用 `__()`/`_e()` 且**必须带 text domain**、原生 gettext 用 `gettext()`/`_()`。完整对照见 [references/php-i18n.md](references/php-i18n.md)。

### 5. 完整性检查
- 对比主语言文件与翻译文件的 key 差异
- 输出缺失翻译的 key 列表
- 统计翻译完成度百分比

## 输出格式
```markdown
## 📊 i18n 扫描报告

### 硬编码文本
| 文件 | 行号 | 内容 | 建议 key |
|------|------|------|----------|
| src/App.tsx | 42 | '欢迎使用' | page.welcome |

### 语言文件
已生成 `locales/zh-CN.json` 和 `locales/en-US.json`

### 翻译完整性
- zh-CN: 45/45 (100%) ✅
- en-US: 42/45 (93.3%) ⚠️ 缺少 3 个 key
```

## 支持的 i18n 框架
- react-intl / FormatJS
- vue-i18n
- i18next / react-i18next / next-i18next
- Angular @ngx-translate
- Python gettext / Flask-Babel
- Java ResourceBundle / Spring MessageSource
- Go go-i18n
- **PHP**（详见 [references/php-i18n.md](references/php-i18n.md)）：
  - Laravel 翻译（`__()` / `trans()`，PHP 数组或 JSON 语言文件）
  - Symfony Translation（`$translator->trans()`，XLIFF）
  - WordPress（`__()` / `_e()` / `_n()`，PO/MO，必须带 text domain）
  - 原生 gettext（`gettext()` / `_()`，PO/MO）

## 注意事项
- 不要翻译技术术语（API、SDK、HTTP 等）
- 保留变量占位符 `{name}` `{{count}}` `%s` `:name` 等格式（各框架占位符语法不同）
- 复数形式和性别变体需要特殊处理（WordPress 用 `_n()`，Laravel 用pluralization规则文件）
- 日期、数字、货币格式需使用 locale 感知的格式化函数
- **PHP 注意**：WordPress 的翻译函数**必须**第二个参数传 text domain；`.mo` 是 `.po` 编译后的二进制，部署前要 `msgfmt` 编译；Blade 模板替换后注意 `{{ }}` 转义与 `{!! !!}` 的区别

# PHP 国际化详解（4 大模式）

PHP 生态有 4 种**互不兼容**的 i18n 模式。检测到 PHP 项目后，先按下表确定属于哪一种，
再按对应章节处理。**切勿混用不同框架的替换函数与文件格式。**

## 快速判定表

| 信号文件 / 目录 | 框架 | 替换函数 | 语言文件格式 | 提取命令 |
|------|------|------|------|------|
| `artisan` + `composer.json` 含 `laravel/framework` | Laravel | `__()` `trans()` | PHP 数组 / JSON | 手动 / 第三方包 |
| `src/Kernel.php` 或 `composer.json` 含 `symfony/*` | Symfony | `$translator->trans()` | XLIFF (`.xlf`) | `translation:extract` |
| `wp-load.php` / `wp-config.php` / `wp-content/` | WordPress | `__()` `_e()` `_n()` | PO/MO | `wp i18n make-pot` |
| `setlocale()` + `bindtextdomain()` / `gettext()` 调用 | 原生 gettext | `gettext()` `_()` | PO/MO | `xgettext` |

> 若 `composer.json` 同时含多个，以**业务代码实际调用**的函数为准（grep 代码里出现哪种）。

---

## 1. Laravel

### 检测
- 根目录有 `artisan` 文件
- `composer.json` 的 `require` 含 `"laravel/framework"`
- 语言文件在 `lang/`（Laravel 9+）或 `resources/lang/`（旧版）目录

### 语言文件格式
**PHP 数组**（默认，推荐）—— `lang/en/messages.php`：
```php
<?php
return [
    'welcome' => 'Welcome, :name',
    'saved'   => 'Saved successfully',
];
```
**JSON**（按语言一文件，适合短键=原文）—— `lang/en.json`：
```json
{ "Welcome, :name": "Welcome, :name" }
```
两种可共存：PHP 数组用「短键」（`messages.welcome`），JSON 用「原文当 key」。

### 替换函数
```php
// 短键（走 PHP 数组文件，第二段是文件名）
echo __('messages.welcome', ['name' => $user->name]);
echo trans('messages.welcome');           // 等价于 __()

// JSON 键（key 本身是原文，走 lang/en.json）
echo __('Welcome, :name', ['name' => $user->name]);

// Blade 模板里
{{ __('messages.welcome', ['name' => $name]) }}

// 复数（Laravel 用 pluralization 规则，见下）
trans_choice('messages.apples', $count, ['count' => $count]);
```

### 占位符
- `:name` —— 直接替换（最常用）
- `:NAME` —— 全大写替换
- `:Name` —— 首字母大写
- 占位符**不**用 `{}` 或 `%s`，是 Laravel 特有的 `:camelCase`

### 复数
在 PHP 数组语言文件里，值为数组时按「1 个 / N 个」定义：
```php
'apples' => '{0} 没有苹果|{1} 一个苹果|[2,*] :count 个苹果',
```
代码用 `trans_choice('messages.apples', $count, ['count' => $count])`。

### 提取已有文本
Laravel **没有**官方 key 提取命令。常用方式：
```bash
# 发布默认语言文件骨架
php artisan lang:publish

# 第三方包扫描 __()/trans() 调用（需先 composer require）
composer require --dev laravel-lang/common
php artisan lang:update
```
本 skill 的硬编码扫描用于发现**尚未包裹 `__()`** 的中文字符串，逐条建议包裹。

### 常见坑
- ❌ `__()` 和 WordPress 的 `__()` **同名但签名不同**（Laravel 第二参数是占位符数组，WP 是 text domain）—— 不可混用
- ❌ Blade 的 `{{ }}` 会 HTML 转义，`{!! !!}` 不转义；翻译含 HTML 的字符串时注意用哪个
- ⚠️ Laravel 9 起 `resources/lang/` 改名为 `lang/`，老项目可能在旧路径

---

## 2. Symfony

### 检测
- `src/Kernel.php` 或 `composer.json` 含 `symfony/framework-bundle`
- 语言文件在 `translations/` 目录
- 代码里注入 `TranslatorInterface` / 用 `$translator->trans()`

### 语言文件格式（XLIFF，推荐）
`translations/messages.en.xlf`：
```xml
<?xml version="1.0"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
    <file source-language="en" target-language="en" datatype="plaintext" original="file.ext">
        <body>
            <trans-unit id="welcome">
                <source>Welcome, {name}</source>
                <target>Welcome, {name}</target>
            </trans-unit>
        </body>
    </file>
</xliff>
```
也支持 `.yaml` / `.php` / `.po`，但 `.xlf` 是官方推荐（支持元数据、注解）。

### 替换函数
```php
// 控制器/服务里注入 TranslatorInterface
public function index(TranslatorInterface $translator)
{
    echo $translator->trans('Welcome, {name}', ['{name}' => $user->getName()]);
    // 复数
    echo $translator->transChoice('{1} One apple|]1,Inf] %count% apples', $count);
}

// Twig 模板里
{{ 'Welcome, {name}'|trans({'{name}': name}) }}
```

### 占位符
- `{name}` —— 用花括号（注意：与 Laravel 的 `:name` 不同）
- 或 `%name%`（旧式，已弃用）

### 提取已有文本
```bash
# 从 src/ 提取所有 trans()/|trans 调用到 translations/messages.<locale>.xlf
php bin/console translation:extract en --dir=src --output-format=xlf

# 中文项目先提取中文源，再翻译成 en
php bin/console translation:extract zh_CN --dir=src
```

### 常见坑
- ⚠️ `transChoice` 在 Symfony 5+ 已弃用，新代码用 `trans(..., domain, locale)` + ICU 复数格式
- ❌ 占位符 `{name}` 与 Laravel `:name` 不同，翻译文件里要保持源文的占位符语法

---

## 3. WordPress

### 检测
- 根目录或上级有 `wp-load.php` / `wp-config.php`
- `wp-content/` 目录存在（`themes/` `plugins/`）
- 代码里有 `__()` ` _e()` 调用且**带 text domain**

### 语言文件格式（PO/MO）
主题/插件目录下 `languages/mytheme.pot`（模板）、`mytheme-zh_CN.po`（翻译）、`.mo`（编译后二进制）：
```po
msgid "Post Title"
msgstr "文章标题"

msgid "Welcome, %s"
msgstr "欢迎，%s"
```

### 替换函数（**必须带 text domain**）
```php
// 取译文不输出
$title = __('Post Title', 'my-theme');

// 取译文并直接 echo
_e('Post Title', 'my-theme');

// 带占位符
printf(__('Welcome, %s', 'my-theme'), $name);
// 或 esc_html（输出到 HTML 属性/文本时防 XSS）
echo esc_html__('Post Title', 'my-theme');
echo esc_attr__('Submit', 'my-theme');

// 复数
echo _n('One comment', '%s comments', $count, 'my-theme');
// 带上下文（消歧义，如同名英文词在不同场景译法不同）
echo _x('Post', 'noun (the post)', 'my-theme');
echo _x('Post', 'verb (to post)', 'my-theme');
```
**text domain** = 主题/插件的唯一标识（通常 slug），所有翻译函数都要传，否则不生效。

### 占位符
- `%s` `%d` —— `printf`/`sprintf` 风格（注意用 `sprintf` 时参数顺序）
- WordPress 用 PHP 原生 printf，**不**支持 Laravel 的 `:name`

### 复数 & 上下文
- `_n($single, $plural, $count, $domain)` —— 单复数
- `_x($text, $context, $domain)` —— 带上下文消歧义
- `_nx(...)` —— 单复数 + 上下文

### 提取已有文本
```bash
# WP-CLI（推荐，需安装 wp-cli）
wp i18n make-pot . languages/my-theme.pot --domain=my-theme

# 或用 npm 包 wp-pot（无需 PHP 环境）
npx wp-pot --domain my-theme --src '*.php' --dest languages/my-theme.pot
```
提取后会生成 `.pot` 模板，复制为 `my-theme-zh_CN.po` 填翻译，再编译 `.mo`。

### 编译 MO 文件
```bash
msgfmt my-theme-zh_CN.po -o my-theme-zh_CN.mo
```
WordPress 运行时只读 `.mo`（二进制），`.po` 是源文件。**部署前必须编译**。

### 常见坑
- ❌ **忘记传 text domain** —— `__('Post Title')` 不会走主题翻译文件（会 fallback 到 WP 核心）
- ❌ 把 Laravel 的 `__()` 误用到 WP —— 第二参数语义完全不同（占位符 vs domain）
- ⚠️ 用户输入要做 `esc_html__` / `esc_attr__`，避免 XSS；普通 `__()` 不转义
- ⚠️ 主题 text domain 要在 `style.css` 头部 `Text Domain:` 声明，且与函数调用一致

---

## 4. 原生 PHP gettext

### 检测
- 代码里有 `setlocale(LC_ALL, ...)` / `bindtextdomain()` / `textdomain()`
- 无框架，纯 PHP（老系统、内部工具常见）
- 语言文件是 `.po`/`.mo`

### 初始化代码（通常在入口文件）
```php
$locale = 'zh_CN.UTF-8';
putenv("LC_ALL=$locale");
setlocale(LC_ALL, $locale);
bindtextdomain('messages', __DIR__ . '/locale');
textdomain('messages');
```
对应目录结构：
```
locale/
└─ zh_CN.UTF-8/
   └─ LC_MESSAGES/
      ├─ messages.po    # 源
      └─ messages.mo    # 编译后（运行时读这个）
```

### 替换函数
```php
// 基础
echo gettext('Welcome');   // 等价于 _('Welcome')
echo _('Welcome');         // 常用简写

// 带占位符
printf(_('Welcome, %s'), $name);

// 复数
echo ngettext('One apple', '%s apples', $count);
```

### 占位符
- `%s` `%d` —— printf/sprintf 风格

### 提取已有文本
```bash
# 从所有 PHP 文件提取 _("...") / gettext("...") 调用
xgettext --language=PHP --from-code=UTF-8 \
         --keyword=_ --keyword=gettext --keyword=ngettext:1,2 \
         -o locale/messages.po \
         *.php **/*.php

# 更新已有 .po（合并新 key，保留已翻的）
msgmerge --update --backup=none locale/zh_CN.UTF-8/LC_MESSAGES/messages.po messages.po
```

### 编译
```bash
msgfmt messages.po -o messages.mo
```

### 常见坑
- ❌ 改了 `.po` **没重新 `msgfmt` 编译 `.mo`** —— 运行时仍用旧译文（最常见的新手坑）
- ⚠️ locale 名要带 `.UTF-8` 后缀，否则中文可能乱码；服务器要装对应 locale（`locale -a` 查看）
- ⚠️ `_()` 在 PHP 7+ 才是 `gettext()` 的别名；老代码用 `gettext()` 更保险

---

## 通用建议（所有 PHP 模式）

### 扫描顺序
处理 PHP 项目时，**先用框架官方提取工具**生成语言文件骨架，再用本 skill 的硬编码扫描**补充**未包裹的文本。顺序：
1. 跑提取命令（`translation:extract` / `wp i18n make-pot` / `xgettext`）
2. 用本 skill 扫描 `.php`，找出**漏网**的硬编码中文字符串
3. 把漏网的逐条包裹成对应框架的翻译函数
4. 重新提取，确认语言文件完整

### .php 文件的特殊性
- **HTML/PHP 混排**：`<h1>标题</h1>` 是 HTML 文本节点，`<?php echo '内容'; ?>` 是 PHP 字符串。两类都要扫，但替换方式不同：
  - HTML 文本 → 改成 `<?php _e('标题', 'domain'); ?>`（WP）或 `{{ __('标题') }}`（Laravel Blade）
  - PHP 字符串 → 包裹翻译函数
- **Blade 模板**（`.blade.php`）：`{{ }}` 输出会转义，`{!! !!}` 不转义；翻译含 HTML 的串用 `{!! !!}` 或显式 `@lang()`
- **Twig 模板**（Symfony）：`{{ 'key'|trans }}`，注意 `|trans` 过滤器

### 变量占位符速查
| 框架 | 占位符语法 | 示例 |
|------|-----------|------|
| Laravel | `:name` | `__('Hi :name', ['name' => $n])` |
| Symfony | `{name}` | `$t->trans('Hi {name}', ['{name}' => $n])` |
| WordPress | `%s` `%d` | `sprintf(__('Hi %s', 'd'), $n)` |
| 原生 gettext | `%s` `%d` | `sprintf(_('Hi %s'), $n)` |

翻译时**保留原文的占位符语法**，不要把 Laravel 的 `:name` 译成 `%s`。

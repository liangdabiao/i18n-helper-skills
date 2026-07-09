---
name: html-i18n
description: 静态多页 HTML 站点的国际化/本地化 —— 扫描提取可翻译文本、生成各语言 HTML 目录、检查翻译完整性。用于书籍/文档站/官网落地页等多语言翻译，产出零 JS 依赖的纯静态译文站点。Use when user asks to translate a static HTML website, make HTML pages multilingual, or generate localized HTML.
---

# 🌐 html-i18n — 静态 HTML 站点多语言助手

专注**静态多页 HTML 站点**的国际化翻译：书籍、文档站、博客、官网落地页等。
采用「目录/路由方案」—— 每种语言一个独立目录，纯静态、SEO 友好、零 JS 依赖。
与 `i18n-helper`（面向 React/Vue 等 JS 框架、依赖 `t()` 函数）**互补不重叠**。

## 触发条件
当用户要求以下任一操作时激活：
- 翻译一个 HTML 网站 / 静态网页站点
- 给这个网站/文档站做国际化、多语言
- 把这套 HTML 书翻成英文/日文/繁中等
- 生成网页的多语言版本（en/、ja/ 等语言目录）

> 若项目是 React/Vue/Angular 等前端框架（含 .jsx/.tsx/.vue、用 `t()` 函数），
> 改用 `i18n-helper`。本 skill 只处理**纯静态 HTML**（可含内联 CSS，但不应有构建框架）。

---

## 工作流程（五步）

翻译一个静态 HTML 站点，按此顺序执行：

1. **分析项目结构** —— 定位 HTML 根目录、确认是纯静态站（无框架）
2. **提取翻译源** —— 运行 `extract.py` 生成 `locales/zh-CN.json`
3. **翻译** —— 基于 zh-CN.json 产出各语言 json（本步由你 LLM 完成，见下「翻译规范」）
4. **应用生成** —— 运行 `apply.py` 把译文回填，生成 `en/`、`ja/` 等语言目录
5. **完整性检查** —— 运行 `check.py` 验证完成度，抽检关键页面

所有脚本在 `scripts/` 下，**仅依赖 Python 标准库**（无需 pip 安装）。

### 第 1 步：分析项目结构

- 确认目标目录是纯静态 HTML（`.html` + `.css` + 图片），无 `package.json`/框架文件
- 统计 HTML 文件数、识别共享资源（css、图片目录）
- 识别源语言（看 `<html lang="...">` 或正文，通常是 zh-CN）
- **问清目标语言**（如 en-US、ja-JP、zh-TW）—— 这是必填项

### 第 2 步：提取翻译源

```bash
python scripts/extract.py <html根目录>
# 例：python scripts/extract.py posthog版/
```

生成 `<根目录>/locales/` 三件套：
- `zh-CN.json` —— **翻译源**：`key -> 原文`。翻译时复制此文件改名（如 `en-US.json`）并替换值为译文。
- `_index.json` —— key 的元信息（文件/标签/属性），apply 定位用，**不要手改**。
- `_common.json` —— 跨文件重复文本（导航词等）已归并为 `common.*` key，保证全站一致。

> 默认源语言代码取 `zh-CN`。若站点源语言不是中文，用 `--out` 指定输出目录后，
> 把生成的 json 文件名改成你的源语言代码（如 `en.json`），翻译目标语言另存。

### 第 3 步：翻译（LLM 执行）

复制 `zh-CN.json` 为各目标语言文件（`en-US.json`、`ja-JP.json`、`zh-TW.json`），
**保持 key 不变，只替换 value 为译文**。必须遵守：

#### 翻译规范（强制）
- **必须先读** [references/glossary.md](references/glossary.md) —— 锁定技术术语译法，全站统一
- **必须先读** [references/extraction-rules.md](references/extraction-rules.md) —— 了解哪些内容被提取/跳过，避免误译代码与 URL
- 大型站点**分批翻译**（每批 ≤ 80 key），保证术语与风格一致
- 保留原文中的占位符、HTML 实体（`&amp;` `&lt;` `&gt;`）、数字编号（§01、Part 1）
- 译文应自然流畅，不是机器直译；书名/标题可意译

#### 绝不翻译这些（脚本已自动跳过，但翻译时也要注意）
- URL、`href`/`src` 路径、CSS class/id、`lang` 属性值
- `<pre><code>` 代码块（SQL/命令/配置）—— **默认整块保留**
- 技术术语（见 glossary）：PostHog、GA4、RFM、LTV、Docker、SQL、API、Webhook 等
- 图片文件名、变量名

### 第 4 步：应用生成

```bash
python scripts/apply.py <html根目录> <翻译json> <输出目录> --lang <代码>
# 例：
python scripts/apply.py posthog版/ posthog版/locales/en-US.json posthog版/en --lang en
python scripts/apply.py posthog版/ posthog版/locales/ja-JP.json posthog版/ja --lang ja
```

每种语言生成一个独立目录，内含译文后的 HTML，**共享根目录的 css 与图片**（子目录自动补 `../` 前缀）。
apply 会：① 把每个文本节点替换为译文 ② 改 `<html lang>` ③ 补资源相对路径。
缺失译文的 key 会**回退原文**（不破版）并告警。

### 第 5 步：完整性检查

```bash
python scripts/check.py <locales目录>
# 例：python scripts/check.py posthog版/locales
```

输出每种语言的完成度百分比、缺失/空值/疑似漏翻（译文与原文相同）的 key。
全部 100% 才算完成。之后**抽检**这些关键页面：
- 含代码块的页（验证代码未被破坏）
- 含 `<table>` 的页（验证单元格翻译）
- 首页/目录页（验证链接与封面文案）
- 含内联 `<strong>`/`<a>` 混排的页（验证嵌套标签未乱）

---

## 脚本说明

| 脚本 | 作用 | 关键设计 |
|------|------|----------|
| `scripts/extract.py` | 扫描 HTML 提取可翻译文本 | 共享 `htmlscanner`，跳过代码块/URL，跨文件重复归并 common key |
| `scripts/apply.py` | 用译文回填生成语言目录 | 字符串精确替换；用「已占用区间」追踪避免重叠替换（如 §短标题 嵌在 §完整标题内）；标签结构逐字保留；缺译文回退原文 |
| `scripts/check.py` | 检查翻译完整性 | 对比 key 集合，报告缺失/空值/漏翻 |
| `scripts/htmlscanner.py` | extract 与 apply 共用的扫描器 | 杜绝「提取漏抓、回填却看到」的不一致 |
| `scripts/zhconv.py` | 简→繁转换（可选，生成 zh-TW 时用） | 词级两岸术语替换 + 字符级字形映射，零依赖 |

> **关于字符映射类语言（如 zh-TW、ja-JP 的速成版）**：
> `zhconv.py` 与示例 `ja_dict.py` 采用「术语表 + 字形映射」，对**标题/导航/封面/术语**质量高，
> 但**长正文段落**可能残留少量未转换字（尤其 ja-JP 的中日汉字混排）。
> 生产级译文建议：结构性文本用字符映射即可，长正文段落由你（LLM）按 `references/glossary.md` 逐段精译后填入对应 json。

## 输出结构示例
```
posthog版/
├─ index.html          (原中文版，保持不动)
├─ 01.html ... 34.html
├─ style.css           (三语言共享)
├─ 图片和附件/         (三语言共享)
├─ locales/
│  ├─ zh-CN.json       (翻译源)
│  ├─ en-US.json       (英文译文)
│  ├─ ja-JP.json       (日文译文)
│  ├─ zh-TW.json       (繁中译文)
│  ├─ _index.json      (定位用，勿改)
│  └─ _common.json     (公共 key 参考)
├─ en/                 ← 英文站 (lang="en")
├─ ja/                 ← 日文站 (lang="ja")
└─ zh-TW/              ← 繁中站 (lang="zh-TW")
```

## 注意事项
- **零侵入**：原中文版 HTML 不改动，译文输出到独立子目录
- **不碰构建脚本**：若站点由 Markdown/脚本生成（如 `generate_site.py`），本 skill 只处理已生成的 HTML，不改源码生成逻辑
- **代码安全优先**：`<pre><code>` 默认整体跳过；若用户显式要求翻译代码注释，需人工逐条确认
- **术语一致性**：跨页重复的导航词（目录/上一章/下一章）由 common key 统一驱动，勿分散翻译
- 翻译完务必运行 check.py + 抽检，确认无破版

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html-i18n · htmlscanner.py  (共享模块)

extract.py 与 apply.py 共用的 HTML 扫描逻辑，确保「提取」与「回填」
对同一份 HTML 看到的可翻译文本完全一致 —— 否则会出现「提取漏抓、
回填却看到」的不一致，导致翻译缺失。

设计：
- 基于 html.parser，convert_charrefs=False（保留实体原样，apply 时不破坏）。
- 维护标签栈，跳过 <pre><code><script><style> 块。
- 对每个可翻译祖先标签下的直接/内联文本，记录：
    text       —— strip 后的原文
    occurrence —— 该 text 在本文件中第几次出现（apply 定位用）
    tag        —— 归属标签
    is_attr / attr_name —— 是否为属性值（img alt 等）
- 「归属标签」= 栈中最近的 TRANSLATABLE_TAGS，兼容 <a><span>§01</span>文本</a>
  这种内联混合：span 子节点的文本归属 span，<a> 的直接文本归属 a。
"""
import re
from html.parser import HTMLParser

TRANSLATABLE_TAGS = {
    "title", "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "li", "td", "th", "caption",
    "a", "blockquote", "strong", "em", "b", "i", "span",
    "figcaption", "label", "option", "button", "div",
}
SKIP_BLOCK_TAGS = {"pre", "code", "script", "style", "kbd", "samp"}
TRANSLATABLE_ATTRS = {
    "img": ("alt",),
    "area": ("alt",),
    "input": ("placeholder",),
}

URL_RE = re.compile(r"^\s*(https?|ftp|mailto|tel)://|^\s*www\.", re.I)
PCT_RE = re.compile(r"(?:%[0-9A-Fa-f]{2}){3,}")
SYMBOLS_RE = re.compile(r"[\s\d§※←→·•\-\.\(\)（）,，:：;；!！?？/\\]+")

# 弯引号归一化：把 “ ” ‘ ’ 统一映射为直引号，避免翻译者手敲时引号不一致导致漏匹配。
# 见 references/extraction-rules.md「弯引号」一节。
QUOTE_NORM = str.maketrans({
    "\u201c": '"', "\u201d": '"',   # “ ”
    "\u2018": "'", "\u2019": "'",   # ‘ ’
})


def norm_quotes(text):
    """把弯引号归一化为直引号。翻译 json 的 key/value 都应先过此函数再匹配。"""
    return text.translate(QUOTE_NORM)


def is_skip_text(text):
    """判定整段文本是否「不需要翻译」（URL / 百分号编码 / 纯符号数字）。"""
    if URL_RE.match(text):
        return True
    if PCT_RE.search(text) and len(text) < 200:
        return True
    if SYMBOLS_RE.fullmatch(text):
        return True
    return False


class Scanner(HTMLParser):
    """扫描一个 HTML，产出 records 列表。extract 与 apply 共用此类。"""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.records = []
        self._tag_stack = []
        self._skip_depth = 0
        self._text_count = {}
        self._line_offset_of = None  # 不需要 offset，定位靠 occurrence

    def _nearest_translatable(self):
        for t in reversed(self._tag_stack):
            if t in TRANSLATABLE_TAGS:
                return t
        return None

    def handle_starttag(self, tag, attrs):
        self._tag_stack.append(tag)
        if tag in SKIP_BLOCK_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        # 可翻译属性（自闭合或开始标签都处理）
        attr_names = TRANSLATABLE_ATTRS.get(tag)
        if attr_names:
            d = dict(attrs)
            for an in attr_names:
                val = d.get(an)
                if val and val.strip() and not is_skip_text(val.strip()):
                    self._record(tag, val.strip(), is_attr=True, attr_name=an)

    def handle_startendtag(self, tag, attrs):
        if tag in SKIP_BLOCK_TAGS:
            return
        if self._skip_depth:
            return
        attr_names = TRANSLATABLE_ATTRS.get(tag)
        if attr_names:
            d = dict(attrs)
            for an in attr_names:
                val = d.get(an)
                if val and val.strip() and not is_skip_text(val.strip()):
                    self._record(tag, val.strip(), is_attr=True, attr_name=an)

    def handle_endtag(self, tag):
        if tag in self._tag_stack:
            while self._tag_stack:
                popped = self._tag_stack.pop()
                if popped in SKIP_BLOCK_TAGS and self._skip_depth:
                    self._skip_depth -= 1
                if popped == tag:
                    break

    def handle_data(self, data):
        if self._skip_depth:
            return
        nearest = self._nearest_translatable()
        if nearest is None:
            return
        text = data.strip()
        if not text or is_skip_text(text):
            return
        self._record(nearest, text)

    def _record(self, tag, text, is_attr=False, attr_name=None):
        self._text_count[text] = self._text_count.get(text, 0) + 1
        self.records.append({
            "text": text,
            "tag": tag,
            "occurrence": self._text_count[text],
            "is_attr": is_attr,
            "attr_name": attr_name,
        })


def scan(source):
    """扫描 HTML 源文本，返回 records 列表。"""
    sc = Scanner()
    sc.feed(source)
    sc.close()
    return sc.records


# 常见 BCP47 语言代码（用于识别语言输出目录，避免写死具体语言）
_LANG_CODES = {
    "en", "en-us", "en-gb", "zh", "zh-cn", "zh-tw", "zh-hk", "ja", "ja-jp",
    "ko", "ko-kr", "fr", "fr-fr", "de", "de-de", "es", "es-es", "it", "pt",
    "pt-br", "ru", "ru-ru", "ar", "hi", "th", "vi", "tr", "nl", "pl", "sv",
}
_LANG_RE = re.compile(r"^[a-z]{2}(-[a-z]{2,4})?$")


def is_lang_dir(name):
    """判断目录名是否像语言输出目录（en / zh-TW / ja-JP 等）。"""
    low = name.lower()
    return low in _LANG_CODES or (bool(_LANG_RE.match(low)) and len(low) <= 5)


def find_html_files(root):
    """返回 [(绝对路径, 相对文件名)]，排除工具/输出子目录。

    排除规则：
    - 工具目录：locales / node_modules / .git / .claude / .agents / .zcode / .workbuddy
    - 语言输出目录：名为常见 BCP47 语言代码的目录（en, zh-TW, ja, fr, de, ...），
      通过 is_lang_dir() 判定，避免写死具体语言。
    - 不排除图片等资源目录（它们不含 .html，自然不会被扫到）。
    """
    EXCLUDE_DIRS = {"locales", "node_modules", ".git", ".claude",
                    ".agents", ".zcode", ".workbuddy", "vendor", "dist", "build"}
    out = []
    import os
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in EXCLUDE_DIRS and not is_lang_dir(d)]
        for fn in sorted(filenames):
            if fn.lower().endswith((".html", ".htm")):
                rel = os.path.relpath(os.path.join(dirpath, fn), root).replace("\\", "/")
                out.append((os.path.join(dirpath, fn), rel))
    return sorted(out, key=lambda x: x[1])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html-i18n · apply.py
用翻译 JSON 回填，生成各语言的 HTML 目录。

核心策略（字符串替换，最稳）：
- 用共享模块 htmlscanner 扫描（与 extract.py 完全一致）。
- 对每条 record（原文 text + occurrence），用译文替换源文件中该出现点。
- 只动文本本身，标签结构、属性、缩进、实体（&amp; &lt; 等）逐字保留。
- 额外处理：<html lang="..."> 改为目标语言；子目录页面补 ../ 资源前缀。
- 缺失译文 → 回退原文（不破版），并记录警告。

翻译 JSON 约定：
  key 与 extract.py 输出的 zh-CN.json 的 key 完全一致，value 为译文。
  apply 通过同目录 _index.json 把 key 还原成「原文 text」再做匹配。
  若 _index.json 不存在，则假定 key 本身就是原文 text。

用法：
    python apply.py <html根目录> <语言json> <输出目录> [--lang en]
    python apply.py your-site/ your-site/locales/en-US.json your-site/en --lang en
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from htmlscanner import scan, find_html_files, norm_quotes


def find_nth(haystack, needle, n):
    """返回 needle 在 haystack 中第 n 次出现的起始 index（找不到返回 -1）。"""
    start = 0
    count = 0
    while True:
        idx = haystack.find(needle, start)
        if idx == -1:
            return -1
        count += 1
        if count == n:
            return idx
        start = idx + len(needle)


def apply_translations(source, records, text_map):
    """对单个文件源文本执行替换，返回 (新文本, 命中数, 缺失列表)。

    records: htmlscanner.scan() 的输出（按文档顺序，含 occurrence）
    text_map: {原文text: 译文text}

    定位策略：用「已占用区间」跟踪。每条 record 的 occurrence 是它在源文件中
    第几次出现；但 find_nth 做的是子串匹配，可能误命中更早出现的、属于别的文本
    节点的子串（如 <title>「站点名·...」会先于 <h1>「站点名」被找到）。
    因此：按文档顺序处理，若命中的区间已被占用，则递增 occurrence 重试，找到第一个
    空闲区间为止。这样既避免重叠替换产生乱码，又不会漏掉真正独立的文本节点。
    """
    edits = []          # (start, end, new_text)
    occupied = []       # 已占用的 (start, end) 区间，按 start 排序
    missing = []

    def overlaps(s, e):
        for os, oe in occupied:
            if s < oe and os < e:   # 区间相交
                return True
        return False

    def in_attr(idx):
        """判断 idx 是否落在属性值内（= "..." 之间且无 intervening >）。
        避免把 <nav aria-label="目录"> 的属性值当成 <h2>目录</h2> 的文本节点误替换。
        """
        # 向左找最近的 = 或 > ；若先遇到 = 说明在属性值里
        seg = source.rfind(">", 0, idx)
        eq = source.rfind("=", 0, idx)
        return eq > seg

    for rec in records:
        text = rec["text"]
        trans = text_map.get(text)
        if trans is None:
            missing.append(text)
            continue
        if trans == text:
            continue
        # 从 rec.occurrence 开始找第一个未占用、且不在属性值内的出现
        occ = rec["occurrence"]
        placed = False
        for _try in range(occ, occ + 50):   # 最多回退若干次
            idx = find_nth(source, text, _try)
            if idx == -1:
                break
            s, e = idx, idx + len(text)
            # 跳过：落在属性值内（如 aria-label="目录"）或与已占用区间重叠
            if in_attr(s) or overlaps(s, e):
                continue
            edits.append((s, e, trans))
            occupied.append((s, e))
            occupied.sort()
            placed = True
            break
        # 放不下就跳过（保持原文，不破版）
    hits = len(edits)
    # 降序合并编辑，避免偏移
    edits.sort(key=lambda e: e[0], reverse=True)
    out = source
    for start, end, new in edits:
        out = out[:start] + new + out[end:]
    return out, hits, missing


def set_lang_attr(html, lang):
    """把 <html lang="..."> 改为目标语言代码。"""
    return re.sub(
        r'(<html[^>]*\blang=")[^"]*(")',
        lambda m: m.group(1) + lang + m.group(2),
        html, count=1)


def link_shared_resources(html, depth):
    """子目录页面补 ../ 前缀，以共享根目录 css 与 图片。

    depth: 子目录相对根的层数（your-site/en → depth=1）。
    只处理纯相对资源引用（style.css、assets/、images/ 等），不改站内 .html 链接
    与绝对路径（http://、//、#、mailto: 等）。
    """
    if depth <= 0:
        return html
    prefix = "../" * depth

    def fix_attr(match):
        attr = match.group(1)
        val = match.group(2)
        # 跳过：绝对路径、锚点、协议链接、已是 ../ 开头、站内 .html 链接
        if val.startswith(("../", "http://", "https://", "//", "#", "mailto:", "data:")):
            return match.group(0)
        if re.match(r"^[A-Za-z0-9_\-]+\.html", val):
            return match.group(0)
        # 其余相对资源引用（css/js/图片/字体等）补前缀
        return f'{attr}="{prefix}{val}"'

    return re.sub(r'(href|src)="([^"]+)"', fix_attr, html)


def main():
    ap = argparse.ArgumentParser(description="用翻译 JSON 生成目标语言 HTML 目录")
    ap.add_argument("root", help="源 HTML 根目录（中文原版）")
    ap.add_argument("json", help="翻译 JSON 路径（如 locales/en-US.json）")
    ap.add_argument("outdir", help="输出目录（如 your-site/en）")
    ap.add_argument("--lang", default=None,
                    help="目标语言代码，写入 <html lang>（如 en / zh-TW / ja）。"
                         "默认取 json 文件名。")
    ap.add_argument("--depth", type=int, default=1,
                    help="输出子目录相对根的层数（默认 1，用于补 ../ 资源前缀）")
    args = ap.parse_args()

    root = os.path.abspath(args.root.rstrip("/\\"))
    if not os.path.isdir(root):
        sys.exit(f"错误：源目录不存在 {root}")
    if not os.path.isfile(args.json):
        sys.exit(f"错误：翻译文件不存在 {args.json}")

    lang = args.lang or os.path.splitext(os.path.basename(args.json))[0]

    with open(args.json, "r", encoding="utf-8") as f:
        translations = json.load(f)

    # 通过 _index.json 把 key 还原为「原文 text」，构造 text->译文 映射
    index_path = os.path.join(os.path.dirname(args.json), "_index.json")
    if os.path.isfile(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
        text_map = {}
        for key, trans in translations.items():
            src = index.get(key, {}).get("text", key)
            text_map[src] = trans
    else:
        text_map = dict(translations)

    # 引号归一化兜底：补一份「弯引号→直引号」的键，避免翻译者手敲引号不一致导致漏匹配。
    # 例如原文 “维度灾难” 被敲成 "维度灾难"，或反之。见 extraction-rules.md「弯引号」。
    _extra = {}
    for src, trans in text_map.items():
        n = norm_quotes(src)
        if n != src and n not in text_map:
            _extra[n] = trans
    text_map.update(_extra)

    os.makedirs(args.outdir, exist_ok=True)
    outdir = os.path.abspath(args.outdir)

    files = find_html_files(root)
    total_hits = 0
    all_missing = set()
    for abspath, relname in files:
        with open(abspath, "r", encoding="utf-8") as f:
            source = f.read()
        records = scan(source)
        new_html, hits, missing = apply_translations(source, records, text_map)
        new_html = set_lang_attr(new_html, lang)
        new_html = link_shared_resources(new_html, args.depth)

        out_path = os.path.join(outdir, os.path.basename(relname))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(new_html)
        total_hits += hits
        all_missing.update(missing)
        print(f"  {relname}: {hits} 处替换")

    print()
    print(f"✅ 生成完成 → {outdir}（lang={lang}）")
    print(f"   总替换：{total_hits} 处")
    if all_missing:
        print(f"   ⚠️ 未翻译（回退原文）：{len(all_missing)} 条")
        for m in sorted(all_missing)[:20]:
            print(f"      - {repr(m[:60])}")
        if len(all_missing) > 20:
            print(f"      ... 还有 {len(all_missing)-20} 条")
    else:
        print(f"   ✅ 无缺失，全部命中")


if __name__ == "__main__":
    main()

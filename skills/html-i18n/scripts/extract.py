#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html-i18n · extract.py
扫描静态 HTML 站点，提取「需翻译的文本节点」生成翻译源 JSON。

核心策略：
- 用共享模块 htmlscanner 扫描（与 apply.py 完全一致，杜绝提取/回填不一致）。
- 跳过 <pre><code> 代码块、URL、纯符号数字。
- 跨文件重复文本（导航词等）自动归并为 common.* key，保证全站一致。
- 输出三件套：
    locales/zh-CN.json   —— key -> 原文（翻译源，翻译者填值）
    locales/_index.json  —— key -> {file, tag, text, is_attr, common?}（定位/审计）
    locales/_common.json —— text -> common key（参考）

用法：
    python extract.py <html根目录> [--out locales] [--common-min 2]
    python extract.py your-site/
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from htmlscanner import scan, find_html_files


def make_key(filename, tag, seq):
    """生成稳定 key：{文件名}:{标签}:{序号}"""
    return f"{filename}:{tag}:{seq}"


def extract_file(html_path, filename):
    """提取单个 HTML，返回 (records, source)。records 与 apply 看到的一致。"""
    with open(html_path, "r", encoding="utf-8") as f:
        source = f.read()
    records = scan(source)
    return records, source


def assign_keys(all_records_by_file):
    """为每个文件分配 key。同一文件内按出现顺序，每条一个唯一 key。

    返回 items: [{key, text, file, tag, is_attr, attr_name, occurrence}]
    occurrence 记录该 text 在该文件内第几次出现（apply 定位用，但不进 json）。
    """
    items = []
    counters = {}  # (file, tag) -> seq
    for filename, records in all_records_by_file.items():
        for rec in records:
            ck = (filename, rec["tag"])
            counters[ck] = counters.get(ck, 0) + 1
            key = make_key(filename, rec["tag"], counters[ck])
            items.append({
                "key": key,
                "text": rec["text"],
                "file": filename,
                "tag": rec["tag"],
                "is_attr": rec["is_attr"],
                "attr_name": rec["attr_name"],
                "occurrence": rec["occurrence"],
            })
    return items


def dedupe_to_common(items, common_min):
    """跨 >= common_min 个文件出现的相同文本 -> common.* key。"""
    text_to_files = {}
    for it in items:
        text_to_files.setdefault(it["text"], set()).add(it["file"])

    common_map = {}
    counter = 0
    for text, files in text_to_files.items():
        if len(files) >= common_min:
            counter += 1
            common_map[text] = f"common.str{counter}"

    for it in items:
        ck = common_map.get(it["text"])
        if ck:
            it["key"] = ck
            it["common"] = True
    return common_map


def main():
    ap = argparse.ArgumentParser(description="提取静态 HTML 站点可翻译文本")
    ap.add_argument("root", help="HTML 根目录")
    ap.add_argument("--out", default=None, help="输出 locales 目录（默认 <root>/locales）")
    ap.add_argument("--common-min", type=int, default=2,
                    help="跨 N 个文件出现则归并为 common key（默认 2）")
    args = ap.parse_args()

    root = os.path.abspath(args.root.rstrip("/\\"))
    if not os.path.isdir(root):
        sys.exit(f"错误：目录不存在 {root}")

    out_dir = args.out or os.path.join(root, "locales")
    os.makedirs(out_dir, exist_ok=True)

    files = find_html_files(root)
    if not files:
        sys.exit(f"错误：在 {root} 未找到 HTML 文件")

    all_records = {}
    for abspath, relname in files:
        records, _ = extract_file(abspath, relname)
        all_records[relname] = records
        print(f"  {relname}: {len(records)} 条")

    items = assign_keys(all_records)
    common_map = dedupe_to_common(items, args.common_min)

    # zh-CN.json: key -> text（翻译源）
    zh = {it["key"]: it["text"] for it in items}
    # _index.json: key -> 元信息
    index = {}
    for it in items:
        index[it["key"]] = {
            "file": it["file"],
            "tag": it["tag"],
            "text": it["text"],
            "is_attr": it["is_attr"],
            "attr_name": it["attr_name"],
            "common": it.get("common", False),
        }

    zh_path = os.path.join(out_dir, "zh-CN.json")
    idx_path = os.path.join(out_dir, "_index.json")
    common_path = os.path.join(out_dir, "_common.json")
    with open(zh_path, "w", encoding="utf-8") as f:
        json.dump(zh, f, ensure_ascii=False, indent=2, sort_keys=True)
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2, sort_keys=True)
    with open(common_path, "w", encoding="utf-8") as f:
        json.dump(common_map, f, ensure_ascii=False, indent=2, sort_keys=True)

    print()
    print(f"✅ 提取完成")
    print(f"   文件数：{len(files)}")
    print(f"   文本条目：{len(items)} → 去重后 {len(zh)} 个 key")
    print(f"   公共 key（跨文件重复）：{len(common_map)}")
    print(f"   输出：{zh_path}")
    print(f"        {idx_path}")
    print(f"        {common_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html-i18n · check.py
检查翻译完整性：对比 zh-CN.json 与各语言 json，输出缺失 key 与完成度。

用法：
    python check.py <locales目录>
    python check.py posthog版/locales
"""
import argparse
import json
import os
import sys


def main():
    ap = argparse.ArgumentParser(description="检查翻译完整性")
    ap.add_argument("locales", help="locales 目录（含 zh-CN.json 等）")
    args = ap.parse_args()

    d = args.locales
    if not os.path.isdir(d):
        sys.exit(f"错误：目录不存在 {d}")

    zh_path = os.path.join(d, "zh-CN.json")
    if not os.path.isfile(zh_path):
        sys.exit(f"错误：未找到 zh-CN.json（翻译源）{zh_path}")
    with open(zh_path, "r", encoding="utf-8") as f:
        zh = json.load(f)
    base_keys = set(zh.keys())

    # 收集所有语言 json（排除 zh-CN 与 _ 开头的辅助文件）
    lang_files = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".json"):
            continue
        if fn in ("zh-CN.json",) or fn.startswith("_"):
            continue
        lang_files.append(fn)

    if not lang_files:
        print("（未发现翻译文件，只有 zh-CN.json）")
        print(f"翻译源 key 数：{len(base_keys)}")
        return

    print(f"翻译源 zh-CN.json：{len(base_keys)} 个 key\n")
    all_complete = True
    for fn in lang_files:
        path = os.path.join(d, fn)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        keys = set(data.keys())
        missing = base_keys - keys
        extra = keys - base_keys
        # 空值也算未翻译
        empty = [k for k in (base_keys & keys) if not str(data.get(k, "")).strip()]
        # 与原文相同（可能漏翻）
        same_as_src = [k for k in (base_keys & keys)
                       if str(data.get(k, "")).strip() == zh.get(k, "")]
        done = len(base_keys) - len(missing) - len(empty)
        pct = done / len(base_keys) * 100 if base_keys else 100
        status = "✅" if pct == 100 else "⚠️"
        if pct < 100:
            all_complete = False
        print(f"{status} {fn}: {done}/{len(base_keys)} ({pct:.1f}%)")
        if missing:
            print(f"     缺失 key: {len(missing)} 个，例：{sorted(missing)[:5]}")
        if empty:
            print(f"     空值 key: {len(empty)} 个，例：{sorted(empty)[:5]}")
        if same_as_src:
            print(f"     与原文相同（疑似漏翻）: {len(same_as_src)} 个，例：{sorted(same_as_src)[:5]}")
        if extra:
            print(f"     多余 key（源中不存在）: {len(extra)} 个，例：{sorted(extra)[:5]}")

    print()
    if all_complete:
        print("🎉 所有语言均 100% 完成度。")
    else:
        print("⏳ 仍有语言未完成，请补齐上述缺失/空值 key。")
        sys.exit(1)


if __name__ == "__main__":
    main()

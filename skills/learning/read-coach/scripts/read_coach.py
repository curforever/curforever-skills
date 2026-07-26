#!/usr/bin/env python3
"""Inspect learning materials and maintain a single Read Coach report."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


SECTIONS = (
    ("quick", "1. 30 秒结论"),
    ("scores", "2. 质量评分与依据"),
    ("map", "3. 核心知识地图"),
    ("learning", "4. 互动学习记录"),
    ("practice", "5. 应用练习与答案要点"),
    ("summary", "6. 最终掌握总结与下一步"),
)
SECTION_KEYS = {key: title for key, title in SECTIONS}
TEXT_ENCODINGS = ("utf-8-sig", "utf-8", "utf-16", "gb18030")


def fail(message: str) -> None:
    print(f"错误：{message}", file=sys.stderr)
    raise SystemExit(2)


def read_text(path: Path) -> str:
    if not path.exists():
        fail(f"找不到文件：{path}")
    if not path.is_file():
        fail(f"不是文件：{path}")
    if path.stat().st_size == 0:
        fail(f"文件为空：{path}")
    for encoding in TEXT_ENCODINGS:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            fail(f"无法读取文件：{exc}")
    fail("文件不是受支持的文本编码；请使用 UTF-8、UTF-16 或 GB18030，或直接粘贴正文。")


def title_from_text(text: str, fallback: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1)
    return fallback


def inspect(source: Path) -> None:
    text = read_text(source)
    lines = text.splitlines()
    headings = []
    in_code_fence = False
    code_blocks = 0
    nonblank_paragraphs = 0
    paragraph_open = False

    for index, line in enumerate(lines, start=1):
        if line.strip().startswith("```") or line.strip().startswith("~~~"):
            if not in_code_fence:
                code_blocks += 1
            in_code_fence = not in_code_fence
        if not in_code_fence:
            match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if match:
                headings.append(
                    {"line": index, "level": len(match.group(1)), "text": match.group(2)}
                )
        if line.strip() and not in_code_fence:
            if not paragraph_open and not re.match(r"^#{1,6}\s+", line):
                nonblank_paragraphs += 1
                paragraph_open = True
        else:
            paragraph_open = False

    result = {
        "source": str(source.resolve()),
        "title": title_from_text(text, source.stem),
        "characters": len(text),
        "nonblank_lines": sum(1 for line in lines if line.strip()),
        "estimated_words": len(re.findall(r"\w+", text, flags=re.UNICODE)),
        "paragraphs": nonblank_paragraphs,
        "code_blocks": code_blocks,
        "headings": headings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def default_report_path(source: Path) -> Path:
    return source.with_name(f"{source.stem}.read-coach.md")


def timestamped_path(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return path.with_name(f"{path.stem}.{stamp}{path.suffix}")


def build_report(title: str, source_label: str) -> str:
    created = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z")
    parts = [
        f"# Read Coach 学习报告：{title}",
        "",
        f"- 来源：{source_label}",
        f"- 创建时间：{created}",
        "- 状态：进行中",
        "",
    ]
    for key, heading in SECTIONS:
        parts.extend(
            [
                f"## {heading}",
                f"<!-- read-coach:{key} -->",
                "_尚未记录。_",
                "",
            ]
        )
    return "\n".join(parts)


def init_report(args: argparse.Namespace) -> None:
    source = Path(args.source).expanduser().resolve() if args.source else None
    if source:
        text = read_text(source)
        title = args.title or title_from_text(text, source.stem)
        source_label = f"`{source}`"
        report = Path(args.report).expanduser().resolve() if args.report else default_report_path(source)
    else:
        if not args.source_label:
            fail("粘贴正文模式需要 --source-label。")
        if not args.report:
            fail("粘贴正文模式需要 --report。")
        title = args.title or args.source_label
        source_label = args.source_label
        report = Path(args.report).expanduser().resolve()

    if report.exists():
        if args.mode == "fail":
            fail(f"报告已存在：{report}。请选择 overwrite 或 timestamp 模式。")
        if args.mode == "timestamp":
            report = timestamped_path(report)
    try:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(build_report(title, source_label), encoding="utf-8")
    except OSError as exc:
        fail(f"无法创建报告：{exc}")
    print(report)


def append_section(args: argparse.Namespace) -> None:
    report = Path(args.report).expanduser().resolve()
    if args.section not in SECTION_KEYS:
        fail(f"未知章节：{args.section}")
    content = read_text(Path(args.content_file).expanduser().resolve()).strip()
    if not content:
        fail("追加内容为空。")
    report_text = read_text(report)
    marker = f"<!-- read-coach:{args.section} -->"
    if marker not in report_text:
        fail("报告不是有效的 Read Coach 报告，或章节标记已缺失。")
    placeholder = f"{marker}\n_尚未记录。_"
    if placeholder in report_text:
        report_text = report_text.replace(placeholder, f"{marker}\n{content}", 1)
    else:
        report_text = report_text.replace(marker, f"{marker}\n{content}", 1)
    try:
        report.write_text(report_text.rstrip() + "\n", encoding="utf-8")
    except OSError as exc:
        fail(f"无法更新报告：{exc}")
    print(report)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="输出材料的结构摘要 JSON")
    inspect_parser.add_argument("--source", required=True, help="Markdown 或纯文本文件")
    inspect_parser.set_defaults(func=lambda args: inspect(Path(args.source).expanduser().resolve()))

    init_parser = subparsers.add_parser("init", help="创建单一学习报告")
    source_group = init_parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--source", help="本地原文路径")
    source_group.add_argument("--source-label", help="粘贴正文的来源说明")
    init_parser.add_argument("--report", help="报告路径；本地原文时默认同目录")
    init_parser.add_argument("--title", help="报告标题")
    init_parser.add_argument(
        "--mode", choices=("fail", "overwrite", "timestamp"), default="fail", help="目标已存在时的处理方式"
    )
    init_parser.set_defaults(func=init_report)

    append_parser = subparsers.add_parser("append", help="向指定报告章节追加 Markdown")
    append_parser.add_argument("--report", required=True, help="学习报告路径")
    append_parser.add_argument("--section", required=True, choices=tuple(SECTION_KEYS), help="目标章节")
    append_parser.add_argument("--content-file", required=True, help="UTF-8 Markdown 内容文件")
    append_parser.set_defaults(func=append_section)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

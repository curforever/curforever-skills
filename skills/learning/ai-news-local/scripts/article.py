#!/usr/bin/env python3
"""Validate and save a local AI news article while preserving existing Q&A."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from reading import save_portable, qa_boundary

QA = re.compile(r'^##\s+延伸问答\s*$', re.MULTILINE)
TITLE = re.compile(r'^# (\d{4})年(\d{1,2})月(\d{1,2})日 AI资讯日报$')

def split_qa(text):
    boundary = qa_boundary(text)
    return (text[:boundary].rstrip() + '\n', text[boundary:].rstrip() + '\n') if boundary is not None else (text.rstrip() + '\n', '')


def check_article(text, path):
    match = TITLE.fullmatch(text.splitlines()[0])
    if not match:
        raise ValueError('First line must be # YYYY年M月D日 AI资讯日报')
    date = f'{int(match[1]):04d}-{int(match[2]):02d}-{int(match[3]):02d}'
    if path.name != f'{date}-AI资讯日报.md':
        raise ValueError('Article date and archive filename do not match')
    main, _ = split_qa(text)
    numbers = [int(n) for n in re.findall(r'^###\s+(?:[🟠🔵🟣🟢]\s+)?(\d+)\.', main, re.MULTILINE)]
    if not numbers or numbers != list(range(1, len(numbers) + 1)):
        raise ValueError('News item numbers must be consecutive')
    images = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', main)
    for image in images:
        if not re.match(r'https?://', image) and not (path.parent / image).is_file():
            raise ValueError('Referenced local image does not exist: ' + image)
    if '## 今日导读' in main:
        required = ['## 今日导读', '## 🟠 行业资讯', '## 🔵 实践工具', '## 🟣 方法启发', '## 🟢 跨界发现']
        positions = [main.find(h) for h in required]
        if -1 in positions or positions != sorted(positions):
            raise ValueError('New article sections missing or out of order')
        guide = main[positions[0]:positions[1]]
        listed = [int(n) for n in re.findall(r'^- [🟠🔵🟣🟢]\s+(?:\*\*)?(\d+)\b', guide, re.MULTILINE)]
        if listed != numbers:
            raise ValueError('Guide and body numbering differ')
        if f'*统计时间：{date}（北京时间）*' not in main:
            raise ValueError('Display the statistics date without hours or minutes')
    elif not all(h in main for h in ['## 近 1 天', '## 近 7 天', '**今日看点：**']):
        raise ValueError('Required article sections missing')


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name('.' + path.name + '.writing')
    temporary.write_text(text, encoding='utf-8')
    temporary.replace(path)


def save(draft, target):
    text = draft.read_text(encoding='utf-8')
    main, draft_qa = split_qa(text)
    old_qa = split_qa(target.read_text(encoding='utf-8'))[1] if target.exists() else ''
    if draft_qa and old_qa and draft_qa != old_qa:
        raise ValueError('Daily regeneration cannot replace existing Q&A; edit that section separately')
    result = main.rstrip() + ('\n\n' + (old_qa or draft_qa) if old_qa or draft_qa else '\n')
    check_article(result, target)
    target.parent.mkdir(parents=True, exist_ok=True)
    result = save_portable(target, result)
    print(json.dumps({'saved': str(target), 'qa_preserved': bool(old_qa), 'sha256': hashlib.sha256(result.encode()).hexdigest()}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    saving = sub.add_parser('save')
    saving.add_argument('--draft', type=Path, required=True)
    saving.add_argument('--target', type=Path, required=True)
    args = parser.parse_args()
    save(args.draft, args.target)


if __name__ == '__main__':
    main()

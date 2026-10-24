#!/usr/bin/env python3
"""Keep portable Markdown and derive a styled browser reading page."""
import argparse
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path

QA = re.compile(r'^##\s+延伸问答\s*$', re.MULTILINE)
SPAN = re.compile(r'<span\s+style="[^"]*">(.*?)</span>', re.DOTALL)

def qa_boundary(text):
    """Keep the separator immediately before Q&A with Q&A, not the news body."""
    match = QA.search(text)
    if not match:
        return None
    prefix = text[:match.start()].rstrip()
    separators = list(re.finditer(r'^---[ \t]*$', prefix, re.MULTILINE))
    if separators and not prefix[separators[-1].end():].strip():
        return separators[-1].start()
    return match.start()

def main_body(text):
    boundary = qa_boundary(text)
    return text[:boundary].rstrip() + '\n' if boundary is not None else text.rstrip() + '\n'

def plain(text):
    text = re.sub(r'^\s*<br\s*/?>\s*$', '\u200b', text, flags=re.MULTILINE)
    text = SPAN.sub(lambda m: m[1], text)
    text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text, flags=re.DOTALL)
    return html.unescape(text)

def digest(text):
    return hashlib.sha256(main_body(plain(text)).encode()).hexdigest()

def sidecar(source):
    return source.parent / '_assets' / (source.name[:10] + '-AI资讯样式.json')

def styled_text(source):
    text = source.read_text(encoding='utf-8')
    metadata = sidecar(source)
    if not metadata.exists():
        return text
    data = json.loads(metadata.read_text(encoding='utf-8'))
    if data['main_sha256'] != digest(text):
        raise ValueError('Article body changed; refresh the style sidecar from the new styled draft before rendering')
    suffix = text[len(main_body(text).rstrip()):].lstrip()
    return data['styled_main'].rstrip() + ('\n\n' + suffix if suffix else '\n')

def save_portable(source, text):
    cleaned = plain(text)
    metadata = sidecar(source)
    if '<span' in main_body(text):
        metadata.parent.mkdir(parents=True, exist_ok=True)
        metadata.write_text(json.dumps({'version':1, 'main_sha256':digest(cleaned), 'styled_main':main_body(text)}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    elif metadata.exists():
        data=json.loads(metadata.read_text(encoding='utf-8'))
        if data['main_sha256'] != digest(cleaned):
            raise ValueError('New article body requires a refreshed style sidecar; do not silently discard colors')
    temporary=source.with_name('.'+source.name+'.writing')
    temporary.write_text(cleaned, encoding='utf-8')
    temporary.replace(source)
    return cleaned

def render(source):
    styled=styled_text(source)
    styled=re.sub(r'\(_assets/([^\)]+)\)', r'(\1)', styled)
    try:
        import markdown
    except ImportError as exc:
        raise RuntimeError('Optional HTML rendering requires Python Markdown in this environment; Markdown file is preserved.') from exc
    rendered = markdown.markdown(styled, extensions=['tables', 'fenced_code'])
    qa_heading=re.search(r'<h2(?:\s+[^>]*)?>延伸问答</h2>',rendered)
    if qa_heading:
        qa=rendered[qa_heading.start():]
        qa=re.sub(r'<p><strong>((?:[一二三四五六七八九十]+、)[^<]+)</strong></p>',r'<p class="qa-theme"><strong>\1</strong></p>',qa)
        qa=re.sub(r'<h3>(Q\d+[｜|])',r'<h3 class="qa-question"><span class="qa-number">\1</span>',qa)
        qa=re.sub(r'<p><em>(关联[：:])',r'<p class="qa-association"><em>\1',qa)
        qa=re.sub(r'<p>(来源[：:])',r'<p class="qa-source">\1',qa)
        rendered=rendered[:qa_heading.start()]+'<section class="qa">'+qa+'</section>'
    title=html.escape(source.read_text(encoding='utf-8').splitlines()[0].removeprefix('# '))
    page='''<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+title+'''</title><style>
body{margin:0;background:#faf9f6;color:#252525;font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}main{max-width:900px;margin:32px auto;padding:36px 44px;background:white;border-radius:14px}h1{font-size:30px}h2{font-size:25px;margin-top:40px}h3{font-size:20px;line-height:1.6;margin-top:28px}img{display:block;max-width:100%;height:auto;border-radius:10px}a{color:#2563eb}code{font-size:.92em;background:#f1f3f5;padding:2px 5px;border-radius:4px}p:has(>em:only-child){color:#667085}li{margin:5px 0}@media(max-width:650px){main{margin:0;padding:20px;border-radius:0}h1{font-size:25px}}table{border-collapse:collapse}td,th{border:1px solid #ddd;padding:8px}hr{border:0;border-top:1px solid #d0d5dd;margin:36px 0 28px}.qa h2,.qa h3{color:#252525}.qa-theme{font-size:19px;font-weight:700;color:#252525;margin:0 0 2px}.qa .qa-question{font-size:18px;color:#252525;margin:18px 0 4px;line-height:1.5}.qa-number{color:#2563eb}.qa blockquote{margin:0 0 14px;padding:0 0 0 14px;border-left:3px solid #cbd5e1;color:#475467;font-size:15px}.qa blockquote p{margin:0}.qa-association{font-size:14px;color:#667085;margin:0 0 12px}.qa-source{font-size:16px;color:#667085;font-style:italic}.qa-source a{color:#2563eb}
</style></head><body><main>'''+rendered+'''</main></body></html>'''
    output=source.parent/'_assets'/(source.name[:10]+'-AI资讯阅读.html')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page,encoding='utf-8')
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    args=parser.parse_args()
    save_portable(args.source,args.source.read_text(encoding='utf-8'))
    print(json.dumps({'markdown':str(args.source),'html':str(render(args.source)),'styles':str(sidecar(args.source))},ensure_ascii=False))

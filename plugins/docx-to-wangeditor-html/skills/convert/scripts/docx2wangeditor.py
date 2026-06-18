# -*- coding: utf-8 -*-
"""
docx2wangeditor.py — Convert Word .docx into clean HTML that pastes correctly
into a wangEditor (v4) rich-text editor.

Target framework: wangEditor (the contenteditable `<div class="w-e-text">` rich
text editor, widely used by Chinese SaaS admin panels). One real-world instance
is the stepos OMS protocol/policy editor, but this works for any wangEditor box.

Required input for that editor: clean SEMANTIC HTML — headings as <h1>/<h2>/<h3>,
emphasis as <strong>, tables as <table> — and URLs WITHOUT an http(s):// scheme.

Stdlib only (no python-docx needed). Usage:
    py docx2wangeditor.py <file.docx | directory> [--center-title]

For each .docx it writes, next to the source:
    <name>.html           full standalone page  (open in browser -> Ctrl+A/C -> paste)
    <name>_fragment.html  body-only HTML        (for raw HTML-source fields)

Why this exists / the critical gotcha:
  On paste, wangEditor STRIPS inline styles but KEEPS tags (h1/h2/h3/strong/table)
  and styles them with its own CSS -- so headings & bold survive a browser copy.
  BUT if the pasted content contains an `http(s)://` URL, wangEditor auto-links it;
  when the URL is glued to following CJK text it mangles the link, `insertHTML`
  fails, and the ENTIRE document collapses into one <p> + <br>... (all formatting
  lost). Fix: render URLs WITHOUT the scheme and WITHOUT <a>.
  See validate_paste.js to re-verify against a live editor.
"""
import zipfile, html, os, re, sys
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

CSS = """
body{{font-family:-apple-system,"Microsoft YaHei",sans-serif;line-height:1.75;max-width:900px;margin:40px auto;padding:0 20px;color:#222;text-align:left;}}
h1{{font-size:24px;margin:0 0 6px;{title_align}}}
h2{{font-size:19px;margin-top:28px;border-bottom:1px solid #ddd;padding-bottom:4px;text-align:left;}}
h3{{font-size:16px;margin-top:20px;text-align:left;}}
p{{margin:8px 0;text-align:left;}}
p.meta{{color:#666;margin:2px 0;{meta_align}}}
table{{border-collapse:collapse;width:100%;margin:16px 0;}}
th,td{{border:1px solid #999;padding:8px 10px;vertical-align:top;text-align:left;}}
th{{background:#f2f2f2;font-weight:bold;}}
strong{{font-weight:bold;}}
"""

# Strip the scheme so wangEditor does NOT auto-link (which crashes its paste). No <a>.
DESCHEME = re.compile(r'https?://(?=[A-Za-z0-9])')

def stylemap(z):
    sr = ET.fromstring(z.read('word/styles.xml').decode('utf-8'))
    m = {}
    for s in sr.findall(W + 'style'):
        nm = s.find(W + 'name')
        ol = s.find(W + 'pPr/' + W + 'outlineLvl')
        m[s.get(W + 'styleId')] = (nm.get(W + 'val') if nm is not None else '',
                                   ol.get(W + 'val') if ol is not None else '')
    return m

def run_html(r):
    txt = ''.join(t.text or '' for t in r.iter(W + 't'))
    if txt == '':
        if r.find(W + 'br') is not None: return '<br>'
        if r.find(W + 'tab') is not None: return ' '
        return ''
    esc = html.escape(txt)
    rPr = r.find(W + 'rPr')
    bold = False
    if rPr is not None:
        b = rPr.find(W + 'b')
        if b is not None and b.get(W + 'val') not in ('0', 'false'):
            bold = True
    return ('<strong>%s</strong>' % esc) if bold else esc

def para_inline(p):
    parts = []
    for ch in p:
        if ch.tag == W + 'r':
            parts.append(run_html(ch))
        elif ch.tag == W + 'hyperlink':
            for r in ch.findall(W + 'r'):
                parts.append(run_html(r))
    s = ''.join(parts).replace('</strong><strong>', '')
    return DESCHEME.sub('', s)            # de-scheme URLs (wangEditor-safe)

def para_text(p):
    return ''.join(t.text or '' for t in p.iter(W + 't')).strip()

def heading_level(p, sm):
    pPr = p.find(W + 'pPr'); sid = ''; pol = ''
    if pPr is not None:
        ps = pPr.find(W + 'pStyle'); sid = ps.get(W + 'val') if ps is not None else ''
        ol = pPr.find(W + 'outlineLvl'); pol = ol.get(W + 'val') if ol is not None else ''
    nm, sol = sm.get(sid, ('', ''))
    if nm.lower() == 'title':
        return 1
    out = pol if pol != '' else sol
    if out not in ('', None):
        try: return min(max(int(out) + 1, 1), 4)
        except ValueError: pass
    m = re.match(r'heading\s*(\d)', nm.lower())
    if m:
        return min(int(m.group(1)) + 1, 4)
    return 0  # body paragraph

def convert(path, center_title=False):
    z = zipfile.ZipFile(path)
    sm = stylemap(z)
    body = ET.fromstring(z.read('word/document.xml').decode('utf-8')).find(W + 'body')
    hp = []
    for el in body:
        if el.tag == W + 'p':
            t = para_text(el)
            if t == '':
                continue
            inline = para_inline(el)
            lvl = heading_level(el, sm)
            if lvl == 1:
                hp.append('<h1>' + inline + '</h1>')
            elif lvl >= 2:
                if t.startswith('版本：') or t.startswith('发布时间：'):
                    hp.append('<p class="meta">' + inline + '</p>')
                else:
                    hp.append('<h%d>%s</h%d>' % (lvl, inline, lvl))
            else:
                hp.append('<p>' + inline + '</p>')
        elif el.tag == W + 'tbl':
            hp.append('<table>')
            for ri, tr in enumerate(el.findall(W + 'tr')):
                tag = 'th' if ri == 0 else 'td'
                hp.append('  <tr>')
                for tc in tr.findall(W + 'tc'):
                    cell = ' '.join(para_inline(p) for p in tc.findall(W + 'p') if para_text(p) != '')
                    hp.append('    <%s>%s</%s>' % (tag, cell, tag))
                hp.append('  </tr>')
            hp.append('</table>')
    body_html = '\n'.join(hp)
    title = next((para_text(p) for p in body.iter(W + 'p')
                  if heading_level(p, sm) == 1 and para_text(p)), 'document')
    css = CSS.format(title_align=('text-align:center;' if center_title else 'text-align:left;'),
                     meta_align=('text-align:center;' if center_title else 'text-align:left;'))
    doc = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n<title>'
           + html.escape(title) + '</title>\n<style>' + css + '</style>\n</head>\n<body>\n'
           + body_html + '\n</body>\n</html>')
    return doc, body_html

def process(path, center_title):
    base = os.path.splitext(path)[0]
    doc, frag = convert(path, center_title)
    open(base + '.html', 'w', encoding='utf-8').write(doc)
    open(base + '_fragment.html', 'w', encoding='utf-8').write(frag)
    print('OK  %s  (h1+h2+h3=%d, urls de-schemed)' % (
        os.path.basename(path),
        doc.count('<h1>') + doc.count('<h2>') + doc.count('<h3>')))

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    center = '--center-title' in sys.argv
    target = args[0] if args else '.'
    if os.path.isdir(target):
        files = [os.path.join(target, f) for f in os.listdir(target)
                 if f.lower().endswith('.docx') and not f.startswith('~$')]
    else:
        files = [target]
    if not files:
        print('No .docx found in', target); return
    for f in sorted(files):
        try:
            process(f, center)
        except Exception as e:
            print('FAIL %s: %s' % (os.path.basename(f), e))

if __name__ == '__main__':
    main()

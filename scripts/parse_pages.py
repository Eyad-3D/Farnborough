#!/usr/bin/env python3
"""Provenance: parser run 2026-07-23 against the 65 fetched listing pages.
Splits each page's grid into per-card chunks (robust to cards lacking a
description modal), extracting name, stand, description and links.
Yielded exactly 1,292 records; per-page counts 20 (pages 1-64) and 12 (page 65)."""
import re, json, html as H

def txt(s):
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()

def parse_page(n):
    h = open(f'p{n}.html', encoding='utf-8', errors='replace').read()
    g = h.find('grid-listing'); end = h.find('pagination', g)
    if end == -1: end = len(h)
    chunks = h[g:end].split('col-md-6 col-lg-3 exhibitor-list-card')[1:]
    recs = []
    for c in chunks:
        m = re.search(r'FIASubTitle[^>]*>(.*?)</p>', c, re.S)
        name = txt(m.group(1)) if m else ''
        m = re.search(r'stand-number[^>]*>(.*?)</span>', c, re.S)
        stand = re.sub(r'^[,\s]+|[,\s]+$', '', txt(m.group(1)) if m else '')
        desc = ''
        mb = re.search(r'modal-body[^>]*>', c)
        if mb:
            t = txt(c[mb.end():])
            t = re.sub(r'^\s*' + re.escape(name) + r'\s*Stand No:\s*[^ ]*\s*', '', t)
            t = re.sub(r'\s*Close\s*$', '', t)
            desc = t[:2000]
        hrefs = []
        for x in re.findall(r'href="(https?://[^"]+)"', c):
            if 'farnboroughairshow' not in x and x not in hrefs:
                hrefs.append(x)
        recs.append({'page': n, 'name': name, 'stand': stand, 'desc': desc, 'hrefs': hrefs[:5]})
    return recs

if __name__ == '__main__':
    allrecs = []
    for n in range(1, 66):
        rs = parse_page(n)
        allrecs.extend(rs)
        with open(f'parsed_p{n}.jsonl', 'w') as f:
            for r in rs:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open('entries.tsv', 'w') as f:
        for r in allrecs:
            f.write(f"{r['page']}\t{r['name']}\t{r['stand']}\n")
    print('total', len(allrecs))

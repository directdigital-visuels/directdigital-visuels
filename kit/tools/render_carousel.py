#!/usr/bin/env python3
"""Rendu des carrousels, visuels et stories Direct Digital à partir d'une spec JSON.

Usage : python3 kit/tools/render_carousel.py spec.json dossier_sortie

Spec :
{
  "name": "2026-11-03_carrousel_hotel",       # préfixe des fichiers
  "format": "post" | "story",                 # post = 1080x1350, story = 1080x1920
  "slides": [ { "type": ..., ... }, ... ]
}

Types de slides (le texte accepte du HTML simple ; <span class="hl">mot</span> = mot mis en avant en bleu) :
- cover    : kicker, title, lead, items[] (optionnel, liste numérotée), swipe (texte, optionnel)
- task     : label, title, problem, actions[], tools[], level   (fond clair)
- question : crit, question, good, example, example_label        (fond clair)
- text     : kicker, title, body, dark (bool)                    (slide simple)
- cta      : kicker, title, lead, keyword (ex. "GUIDE") OU action (ex. "Enregistre ce post"), foot
- ask      : kicker, title, chips[], action                      (visuel question, fond sombre)
"""
import json, os, sys, html
from playwright.sync_api import sync_playwright

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = os.path.join(KIT, 'templates', 'carousel.css')
MARK = os.path.join(KIT, 'brand', 'mark.png')

SAVE_ICON = '<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#2563FF" stroke-width="2.4" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>'
CHAT_ICON = '<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#2563FF" stroke-width="2.4" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>'
CHECK = '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'


def top(dark, n, tot):
    b = (f'<span class="tile"><img src="file://{MARK}"></span>' if dark
         else f'<span class="bare"><img src="file://{MARK}"></span>')
    c = f'<div class="count">{n}/{tot}</div>' if tot > 1 else ''
    return f'<div class="top"><div class="brand">{b}</div>{c}</div>'


def fr(t):
    """Espaces insécables avant ? ! : ; et autour des guillemets."""
    for p in ['?', '!', ';']:
        t = t.replace(' ' + p, '&nbsp;' + p)
    t = t.replace('« ', '«&nbsp;').replace(' »', '&nbsp;»')
    return t


def slide(s, i, tot, story):
    t = s['type']
    st = ' style="height:1920px;padding-top:200px;padding-bottom:300px"' if story else ''
    if t == 'cover':
        items = ''
        if s.get('items'):
            items = '<div class="recap" style="margin-top:44px;gap:12px">' + ''.join(
                f'<div><span>{k+1}</span>{fr(x)}</div>' for k, x in enumerate(s['items'])) + '</div>'
        size = ' style="font-size:86px"' if s.get('items') else ''
        sw = s.get('swipe', 'Glisse pour voir')
        swipe = '' if tot == 1 else f'<div class="swipe"><div class="arr">→</div>{sw}</div>'
        return (f'<div class="s dark" id="s{i}"{st}>{top(1,i,tot)}<div class="kicker">{fr(s.get("kicker",""))}</div>'
                f'<h1{size}>{fr(s["title"])}</h1><p class="lead" style="font-size:34px;margin-top:30px">{fr(s.get("lead",""))}</p>'
                f'{items}<div class="grow"></div>{swipe}</div>')
    if t == 'task':
        lis = ''.join(f'<li>{fr(a)}</li>' for a in s['actions'])
        tl = ''.join(f'<span class="t">{x}</span>' for x in s.get('tools', []))
        lvl = f'<span class="lvl">{s["level"]}</span>' if s.get('level') else ''
        return (f'<div class="s light" id="s{i}"{st}>{top(0,i,tot)}<div class="task"><span class="tn">{s.get("n",i-1)}</span>{s["label"]}</div>'
                f'<h2 style="font-size:64px">{fr(s["title"])}</h2><p class="prob"><b>Le problème :</b> {fr(s["problem"])}</p>'
                f'<div class="act"><div class="lb">À faire</div><ol>{lis}</ol></div>'
                f'<div class="tools"><span class="l">Outils</span>{tl}{lvl}</div></div>')
    if t == 'question':
        return (f'<div class="s light" id="s{i}"{st}>{top(0,i,tot)}<div class="qn">{s.get("n",i-1)}</div><div class="crit">{s["crit"]}</div>'
                f'<h2>{fr(s["question"])}</h2><div class="good"><div class="ic">{CHECK}</div><div class="t"><b>Bon signe</b>{fr(s["good"])}</div></div>'
                f'<div class="exl"><b>{s.get("example_label","Dans un restaurant")}</b>{fr(s["example"])}</div></div>')
    if t == 'text':
        cls = 'dark' if s.get('dark') else 'light'
        return (f'<div class="s {cls}" id="s{i}"{st}>{top(cls=="dark",i,tot)}<div class="kicker">{fr(s.get("kicker",""))}</div>'
                f'<h2>{fr(s["title"])}</h2><p class="lead">{fr(s.get("body",""))}</p></div>')
    if t == 'cta':
        if s.get('keyword'):
            box = (f'<div class="ctabox"><div class="l">{fr(s.get("box_text","Écris ce mot<br>en message privé"))}</div>'
                   f'<div class="kw">{s["keyword"]}</div></div>')
        else:
            box = f'<div class="save">{SAVE_ICON}{fr(s.get("action","Enregistre ce post"))}</div>'
        foot = f'<div class="foot">{fr(s["foot"])}</div>' if s.get('foot') else ''
        return (f'<div class="s dark" id="s{i}"{st}>{top(1,i,tot)}<div class="kicker">{fr(s.get("kicker",""))}</div>'
                f'<h2>{fr(s["title"])}</h2><p class="lead" style="font-size:34px">{fr(s.get("lead",""))}</p>'
                f'<div class="grow"></div>{box}{foot}</div>')
    if t == 'ask':
        chips = ''.join(f'<div class="chip" style="background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.16);color:#fff">{fr(c)}</div>' for c in s.get('chips', []))
        return (f'<div class="s dark" id="s{i}"{st}>{top(1,i,tot)}<div class="kicker">{fr(s.get("kicker",""))}</div>'
                f'<h1 style="font-size:92px">{fr(s["title"])}</h1><div class="chips" style="margin-top:60px">{chips}</div>'
                f'<div class="grow"></div><div class="save">{CHAT_ICON}{fr(s.get("action","Dis-le-nous en commentaire"))}</div></div>')
    raise ValueError('type inconnu : ' + t)


def main():
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    story = spec.get('format') == 'story'
    W, H = 1080, (1920 if story else 1350)
    slides = spec['slides']
    body = '\n'.join(slide(s, i + 1, len(slides), story) for i, s in enumerate(slides))
    page = (f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><link rel="stylesheet" href="file://{CSS}">'
            f'<style>.s{{width:{W}px;height:{H}px}}</style></head><body>{body}</body></html>')
    tmp = os.path.join(out, '_render.html')
    open(tmp, 'w').write(page)
    files = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': W, 'height': H})
        pg.goto('file://' + os.path.abspath(tmp), wait_until='commit')
        pg.wait_for_load_state('domcontentloaded')
        pg.wait_for_timeout(700)
        for i in range(len(slides)):
            el = pg.locator(f'#s{i+1}')
            over = pg.evaluate(f'(()=>{{const e=document.getElementById("s{i+1}");return e.scrollHeight>e.clientHeight+2}})()')
            f = os.path.join(out, f'{spec["name"]}_{i+1}.png')
            el.screenshot(path=f)
            files.append(f)
            if over:
                print(f'ATTENTION : la slide {i+1} déborde, raccourcis son texte.', file=sys.stderr)
        b.close()
    os.remove(tmp)
    print('\n'.join(files))


if __name__ == '__main__':
    main()

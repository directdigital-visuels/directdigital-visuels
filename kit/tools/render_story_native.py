#!/usr/bin/env python3
"""Stories Direct Digital — DA « native » : on doit croire que Yohan l'a postée depuis son téléphone.

Usage : python3 render_story_native.py spec.json dossier_sortie

Spec :
{
  "name": "2026-11-04_story_chatbot",
  "bg": "chemin/vers/photo.jpg",          # vraie photo / image de vie (jamais un fond uni de marque)
  "tag": "Question du soir 👀",            # petit texte en haut, style « étiquette » Instagram (fond blanc)
  "lines": ["Quand tu réserves un hôtel,", "tu préfères parler à…"],   # texte principal, style surligné Instagram
  "hl": "parler à…",                       # (optionnel) morceau mis en bleu #2563FF façon surligneur
  "options": ["🤖 un chatbot", "🙋 quelqu'un de la réception"],       # (optionnel) choix, un bloc chacun
  "sticker_space": true,                   # (optionnel) laisse une zone vide pour un sondage ajouté à la main
  "foot": "Réponds-moi en message, je lis tout 👇"                    # petit texte en bas, sans bouton
}
Règles de la DA : pas de logo, pas de bouton, pas de kicker en capitales, « je » plutôt que « nous »,
texte court (≤ 25 mots), une photo réelle légèrement assombrie, le bleu seulement en surlignage d'un mot.
"""
import json, os, sys, html
from playwright.sync_api import sync_playwright

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;overflow:hidden;font-family:'Inter',sans-serif;-webkit-font-smoothing:antialiased}
.st{position:relative;width:1080px;height:1920px;overflow:hidden;background:#111}
.bg{position:absolute;inset:-20px;background-size:cover;background-position:center;filter:saturate(1.05) contrast(1.02)}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.45) 0%,rgba(0,0,0,.05) 28%,rgba(0,0,0,.05) 55%,rgba(0,0,0,.55) 100%)}
.grain{position:absolute;inset:0;opacity:.07;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}
.wrap{position:absolute;left:0;right:0;top:860px;display:flex;flex-direction:column;align-items:center;padding:0 90px}
.tag{display:inline-block;background:#fff;color:#111;font-weight:700;font-size:40px;padding:14px 26px;border-radius:14px;transform:rotate(-2deg);margin-bottom:46px}
.main{display:flex;flex-direction:column;align-items:center;gap:0}
.main span.l{display:inline;background:rgba(0,0,0,.72);color:#fff;font-weight:700;font-size:62px;line-height:1.32;padding:6px 22px;border-radius:16px;box-decoration-break:clone;-webkit-box-decoration-break:clone;text-align:center}
.main .row{margin:2px 0;text-align:center}
.hl{background:#2563FF;border-radius:10px;padding:0 10px}
.opts{display:flex;flex-direction:column;align-items:center;gap:18px;margin-top:44px}
.opt{background:#fff;color:#111;font-weight:700;font-size:42px;padding:16px 30px;border-radius:999px;box-shadow:0 8px 30px rgba(0,0,0,.25)}
.space{height:260px}
.foot{position:absolute;left:0;right:0;bottom:215px;text-align:center;color:#fff;font-weight:600;font-size:42px;text-shadow:0 2px 12px rgba(0,0,0,.7)}
"""

def esc(t):
    return html.escape(t)

def build(s):
    bg = os.path.abspath(s['bg'])
    rows = []
    for line in s['lines']:
        t = esc(line)
        if s.get('hl') and esc(s['hl']) in t:
            t = t.replace(esc(s['hl']), f'<span class="hl">{esc(s["hl"])}</span>')
        rows.append(f'<div class="row"><span class="l">{t}</span></div>')
    opts = ''
    if s.get('options'):
        opts = '<div class="opts">' + ''.join(f'<div class="opt">{esc(o)}</div>' for o in s['options']) + '</div>'
    space = '<div class="space"></div>' if s.get('sticker_space') else ''
    tag = f'<div class="tag">{esc(s["tag"])}</div>' if s.get('tag') else ''
    foot = f'<div class="foot">{esc(s["foot"])}</div>' if s.get('foot') else ''
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="st">'
            f'<div class="bg" style="background-image:url(\'file://{bg}\')"></div><div class="shade"></div><div class="grain"></div>'
            f'<div class="wrap">{tag}<div class="main">{"".join(rows)}</div>{space}{opts}</div>{foot}</div></body></html>')

def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[1])))
    tmp = os.path.join(os.path.abspath(out), '_story.html'); open(tmp, 'w').write(build(spec))
    f = os.path.join(os.path.abspath(out), spec['name'] + '.png')
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--no-sandbox']); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.goto('file://' + tmp); pg.wait_for_timeout(600)
        over = pg.evaluate("(()=>{const w=document.querySelector('.wrap');return w.getBoundingClientRect().bottom>1620})()")
        pg.screenshot(path=f); b.close()
    os.remove(tmp)
    if over: print('ATTENTION : le texte descend dans la zone basse (réponse / barre Instagram), raccourcis-le.', file=sys.stderr)
    print(f)

if __name__ == '__main__':
    main()

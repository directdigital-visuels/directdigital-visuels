#!/usr/bin/env python3
"""Rendu d'un Reel en motion design Direct Digital (1080x1920, 30 i/s, sans son) + sa couverture.

Usage : python3 kit/tools/render_reel.py spec.json dossier_sortie

Spec :
{
  "name": "2026-11-04_reel_privatisation",
  "cover": {"kicker": "Version restaurant", "title": "Ta question <span>?</span>", "tags": ["Tag1","Tag2"]},
  "scenes": [
    {"type": "hook",  "dur": 3.5, "kicker": "...", "lines": ["Ligne 1", "Ligne 2 mise en avant"]},
    {"type": "point", "dur": 4.5, "num": "1", "title": "...", "text": "...", "ex_label": "Exemple",
        "chips": ["Départ", "Arrivée"]   # OU "ex_text": "phrase d'exemple"
    },
    {"type": "end",   "dur": 5,   "lines": ["Phrase finale", "partie mise en avant"], "cta": "Enregistre pour t'en souvenir"}
  ]
}
La dernière ligne de "lines" est mise en avant en bleu. Durée totale conseillée : 15 à 30 s.
Le texte reste entre 330 px et 1440 px de hauteur (zone que l'interface Instagram ne masque pas).
"""
import json, os, sys, shutil, subprocess
from playwright.sync_api import sync_playwright

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = os.path.join(KIT, 'brand', 'mark.png')

CSS = """
:root{--blue:#2563FF;--night:#10172A}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden;background:var(--night)}
body{font-family:Inter,sans-serif;color:#fff;-webkit-font-smoothing:antialiased}
.bg{position:absolute;inset:0;background:radial-gradient(70% 45% at 85% 10%,#1d2f7a 0%,rgba(16,23,42,0) 70%),radial-gradient(70% 45% at 10% 95%,#1f2350 0%,rgba(16,23,42,0) 70%),var(--night);animation:drift var(--T) linear both}
@keyframes drift{from{transform:scale(1)}to{transform:scale(1.12)}}
.bar{position:absolute;top:110px;left:90px;right:90px;height:6px;border-radius:3px;background:rgba(255,255,255,.12);overflow:hidden}
.bar i{display:block;height:100%;width:100%;background:var(--blue);transform-origin:left;animation:prog var(--T) linear both}
@keyframes prog{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.tile{position:absolute;top:140px;left:90px;width:96px;height:96px;border-radius:24px;background:#fff;display:flex;align-items:center;justify-content:center}
.tile img{height:64px}
.sc{position:absolute;left:90px;right:150px;top:360px;bottom:520px;display:flex;flex-direction:column;justify-content:center;opacity:0}
.in{opacity:0;transform:translateY(60px);animation:up .6s cubic-bezier(.2,.8,.2,1) both}
@keyframes up{to{opacity:1;transform:none}}
@keyframes vis{0%{opacity:0}4%{opacity:1}96%{opacity:1}100%{opacity:0}}
.kick{font-size:34px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#7FA2FF;margin-bottom:34px}
h1{font-family:Poppins;font-weight:700;font-size:100px;line-height:1.04;letter-spacing:-2.5px}
h2{font-family:Poppins;font-weight:700;font-size:88px;line-height:1.05;letter-spacing:-2px}
.hl{color:#6F95FF}
.def{font-size:48px;font-weight:600;line-height:1.3;margin-top:36px}
.ex{margin-top:56px;border-radius:30px;padding:40px 44px;background:rgba(255,255,255,.06);border:2px solid rgba(255,255,255,.14)}
.ex .l{font-size:28px;font-weight:700;letter-spacing:3px;color:#8FA6E6;text-transform:uppercase;margin-bottom:22px}
.flow{display:flex;align-items:center;gap:22px;font-size:38px;font-weight:600;flex-wrap:wrap;line-height:1.3}
.chip{background:#fff;color:var(--night);padding:14px 26px;border-radius:18px}
.chip.b{background:var(--blue);color:#fff}
.arr{color:#7FA2FF;font-weight:700}
.num{font-family:Poppins;font-weight:700;font-size:200px;line-height:1;color:#6F95FF;margin-bottom:10px}
.cta{display:inline-flex;align-items:center;gap:22px;margin-top:70px;background:#fff;color:var(--night);font-size:46px;font-weight:700;padding:30px 44px;border-radius:26px;align-self:flex-start}
"""
SAVE = '<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#2563FF" stroke-width="2.4" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>'


def fr(t):
    for p in ['?', '!', ';', ':']:
        t = t.replace(' ' + p, '&nbsp;' + p)
    return t


def lines_html(lines, tag, t0, step=0.5):
    out = []
    for k, l in enumerate(lines):
        cls = 'in hl' if k == len(lines) - 1 and len(lines) > 1 else 'in'
        out.append(f'<{tag} class="{cls}" style="animation-delay:{t0+0.15+k*step:.2f}s">{fr(l)}</{tag}>')
    return ''.join(out)


def scene(s, t0):
    d = s['dur']
    head = f'<div class="sc" style="animation:vis {d}s {t0}s both">'
    if s['type'] == 'hook':
        return head + f'<div class="kick in" style="animation-delay:{t0+.1:.2f}s">{s.get("kicker","")}</div>' + lines_html(s['lines'], 'h1', t0, .65) + '</div>'
    if s['type'] == 'point':
        if s.get('chips'):
            c = s['chips']
            body = f'<div class="flow"><span class="chip">{c[0]}</span><span class="arr">→</span><span class="chip b">{c[1]}</span></div>'
        else:
            body = f'<div class="flow" style="display:block">{fr(s.get("ex_text",""))}</div>'
        ex = f'<div class="ex in" style="animation-delay:{t0+.8:.2f}s"><div class="l">{s.get("ex_label","Exemple")}</div>{body}</div>'
        num = f'<div class="num in" style="animation-delay:{t0+.1:.2f}s">{s["num"]}</div>' if s.get('num') else ''
        return (head + num + f'<h2 class="in" style="animation-delay:{t0+.25:.2f}s">{fr(s["title"])}</h2>'
                f'<p class="def in" style="animation-delay:{t0+.6:.2f}s">{fr(s.get("text",""))}</p>' + ex + '</div>')
    if s['type'] == 'end':
        cta = f'<div class="cta in" style="animation-delay:{t0+1.4:.2f}s">{SAVE}{fr(s.get("cta","Enregistre pour t’en souvenir"))}</div>'
        return head + lines_html(s['lines'], 'h2', t0, .5) + cta + '</div>'
    raise ValueError(s['type'])


def cover_html(c):
    tags = ''.join(f'<div>{t}</div>' for t in c.get('tags', []))
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}} html,body{{width:1080px;height:1920px;overflow:hidden}}
body{{font-family:Inter,sans-serif;color:#fff;background:radial-gradient(70% 45% at 85% 10%,#1d2f7a 0%,rgba(16,23,42,0) 70%),radial-gradient(70% 45% at 10% 95%,#1f2350 0%,rgba(16,23,42,0) 70%),#10172A}}
.wrap{{position:absolute;left:90px;right:90px;top:285px;height:1350px;display:flex;flex-direction:column;justify-content:center}}
.tile{{display:inline-flex;align-items:center;justify-content:center;width:110px;height:110px;border-radius:28px;background:#fff;margin-bottom:70px}} .tile img{{height:74px}}
.k{{font-size:36px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#7FA2FF;margin-bottom:34px}}
h1{{font-family:Poppins;font-weight:700;font-size:118px;line-height:1.03;letter-spacing:-3px}} h1 span{{color:#6F95FF}}
.tags{{display:flex;gap:18px;margin-top:70px;flex-wrap:wrap}} .tags div{{font-size:34px;font-weight:600;padding:16px 30px;border-radius:999px;border:2px solid rgba(255,255,255,.2);background:rgba(255,255,255,.06)}}
</style></head><body><div class="wrap"><div><span class="tile"><img src="file://{MARK}"></span></div>
<div class="k">{c.get('kicker','')}</div><h1>{fr(c['title'])}</h1><div class="tags">{tags}</div></div></body></html>"""


def main():
    spec = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    total, t, parts = 0.0, 0.0, []
    for s in spec['scenes']:
        parts.append(scene(s, t))
        t += s['dur']
    total = t
    page = (f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body style="--T:{total}s"><div class="bg"></div><div class="bar"><i></i></div>'
            f'<div class="tile"><img src="file://{MARK}"></div>{"".join(parts)}</body></html>')
    work = os.path.join(out, '_frames')
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    html_path = os.path.join(out, '_reel.html')
    open(html_path, 'w').write(page)
    fps = 30
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.goto('file://' + os.path.abspath(html_path), wait_until='commit')
        pg.wait_for_load_state('domcontentloaded')
        pg.wait_for_timeout(700)
        pg.evaluate('document.getAnimations().forEach(a=>a.pause())')
        for i in range(int(total * fps)):
            pg.evaluate(f'document.getAnimations().forEach(a=>a.currentTime={i*1000/fps})')
            pg.screenshot(path=f'{work}/f{i:04d}.jpg', type='jpeg', quality=92)
        if spec.get('cover'):
            cp = os.path.join(out, '_cover.html')
            open(cp, 'w').write(cover_html(spec['cover']))
            pg.goto('file://' + os.path.abspath(cp), wait_until='commit')
            pg.wait_for_load_state('domcontentloaded')
            pg.wait_for_timeout(500)
            pg.screenshot(path=os.path.join(out, f'{spec["name"]}_couverture.png'))
            os.remove(cp)
        b.close()
    mp4 = os.path.join(out, f'{spec["name"]}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(fps), '-i', f'{work}/f%04d.jpg',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', mp4], check=True)
    shutil.rmtree(work)
    os.remove(html_path)
    print(mp4)


if __name__ == '__main__':
    main()

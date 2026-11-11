#!/usr/bin/env python3
"""Reels Direct Digital — moteur de motion design v2 (1080x1920, 30 i/s, son libre de droits) + couverture.

Usage :
  python3 kit/tools/render_reel.py spec.json dossier_sortie            # rendu complet
  python3 kit/tools/render_reel.py spec.json dossier_sortie --preview  # planche d'images clés seulement (à regarder AVANT le rendu)
  options : --no-audio (vidéo muette)   --no-cache (recalcule toutes les scènes)

Spec (les anciens specs v1 hook / point / end fonctionnent tels quels) :
{
  "name": "2026-11-17_reel_sujet",
  "audio": true,                      # true = musique + effets générés (libres de droits) · false = muet · "fichier.mp3"
  "cover": {"kicker": "Restaurants", "title": "Ta question <span>?</span>", "tags": ["Tag 1", "Tag 2"]},
  "scenes": [ ... ]
}

Types de scènes ("dur" en secondes ; "theme": "light" possible sur toutes sauf clip, pour casser le rythme) :
  hook    {"kicker", "lines": [...]}                       accroche, typo cinétique mot à mot ; dernière ligne en bleu
  clip    {"src": "plan.mp4|photo.jpg", "start": 0, "lines": [...], "tag": "..."}
                                                           plan vidéo ou photo plein écran (visage / avatar) + sous-titres natifs.
                                                           C'est la brique des réels HYBRIDES : clip en accroche, motion design ensuite.
  point   {"num", "title", "text", "ex_label", "chips": [a, b] | "ex_text"}    une idée + un exemple
  list    {"kicker", "title", "items": [...]}              liste qui se coche ligne par ligne
  compare {"title", "left": {"label", "items"}, "right": {"label", "items"}}   avant / après
  phone   {"title", "name", "sub", "messages": [{"side": "in|out", "text"}]}   conversation SMS / message dans un téléphone
  notif   {"title", "notifs": [{"app", "title", "text", "time"}]}              notifications qui tombent
  counter {"kicker", "from", "to", "decimals", "prefix", "suffix", "label"}    chiffre qui défile — UNIQUEMENT un chiffre réel et sourcé
  end     {"lines": [...], "cta": "Enregistre pour t'en souvenir"}             phrase finale + une seule action

Dans les textes, *un mot entre étoiles* passe en bleu.
Règles : « tu », jamais de chiffre / client / témoignage inventé, une seule action, 15 à 30 s au total.
Le moteur garde le texte entre 330 et 1440 px (zone que l'interface Instagram ne masque pas) : il réduit
automatiquement un contenu trop long et te prévient s'il a dû trop réduire.
"""
import hashlib, html as htmllib, json, os, shutil, subprocess, sys, tempfile
import numpy as np
from playwright.sync_api import sync_playwright

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = os.path.join(KIT, 'brand', 'mark.png')
FPS, W, H = 30, 1080, 1920
ENC = ['-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-video_track_timescale', '15360']
VERSION = 'v2.0'

CSS = """
:root{--blue:#2563FF;--night:#10172A;--fg:#fff;--mut:#B9C4E4;--hl:#6F95FF;--card:rgba(255,255,255,.07);--line:rgba(255,255,255,.16);--soft:#8FA6E6}
body.light{--fg:#10172A;--mut:#4A5578;--hl:#2563FF;--card:#fff;--line:#DCE3F5;--soft:#5E72B0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden;background:var(--night)}
body{font-family:Inter,sans-serif;color:var(--fg);-webkit-font-smoothing:antialiased}
i{font-style:normal}
/* fond vivant : deux halos qui dérivent + trame de points */
.bg{position:absolute;inset:-80px;background:radial-gradient(60% 38% at 86% 12%,#22379a 0%,rgba(16,23,42,0) 70%),radial-gradient(64% 40% at 8% 92%,#2a2466 0%,rgba(16,23,42,0) 70%),var(--night);animation:drift var(--T) linear both;animation-delay:calc(var(--t0) * -1)}
@keyframes drift{0%{transform:translate(0,0) scale(1)}50%{transform:translate(-30px,24px) scale(1.07)}100%{transform:translate(20px,-30px) scale(1.14)}}
.dots{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.07) 2px,transparent 2.5px);background-size:54px 54px;animation:dots var(--T) linear both;animation-delay:calc(var(--t0) * -1);-webkit-mask-image:linear-gradient(180deg,transparent 0,#000 30%,#000 70%,transparent 100%)}
@keyframes dots{to{transform:translateY(-108px)}}
.panel{position:absolute;inset:0;background:#F3F6FD;clip-path:circle(0 at 50% 62%);animation:wipe .7s cubic-bezier(.7,0,.2,1) both}
@keyframes wipe{to{clip-path:circle(150% at 50% 62%)}}
/* barre de progression segmentée */
.bar{position:absolute;top:112px;left:90px;right:90px;height:6px;display:flex;gap:10px;z-index:5}
.bar s{flex:1;border-radius:3px;background:rgba(255,255,255,.2);overflow:hidden}
.bar s.done{background:var(--blue)}
.bar s b{display:block;height:100%;background:var(--blue);transform-origin:left;animation:prog var(--d) linear both}
body.light .bar s{background:rgba(16,23,42,.14)} body.light .bar s.done{background:var(--blue)}
@keyframes prog{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.tile{position:absolute;top:146px;left:90px;width:92px;height:92px;border-radius:24px;background:#fff;display:flex;align-items:center;justify-content:center;z-index:5;box-shadow:0 10px 30px rgba(0,0,0,.18)}
.tile img{height:62px}
/* scène : zone sûre 330 → 1440 */
.sc{position:absolute;left:90px;right:150px;top:330px;height:1110px;display:flex;flex-direction:column;justify-content:center}
.sc.exit{animation:exit .32s cubic-bezier(.6,0,.9,.4) both;animation-delay:calc(var(--d) - .32s)}
@keyframes exit{to{opacity:0;transform:translateY(-70px) scale(.97)}}
.inn{display:flex;flex-direction:column;align-items:flex-start}
/* briques d'animation */
.up{opacity:0;transform:translateY(54px);animation:up .6s cubic-bezier(.2,.8,.2,1) both}
@keyframes up{to{opacity:1;transform:none}}
.pop{opacity:0;transform:scale(.55);animation:pop .5s cubic-bezier(.34,1.56,.64,1) both}
@keyframes pop{to{opacity:1;transform:none}}
.side{opacity:0;transform:translateX(120px);animation:up .65s cubic-bezier(.2,.8,.2,1) both}
.w{display:inline-block;overflow:hidden;vertical-align:top;padding:0 .05em .16em;margin:0 -.05em -.16em}
.w i{display:inline-block;transform:translateY(108%);animation:rise .55s cubic-bezier(.2,.85,.2,1) both}
@keyframes rise{to{transform:none}}
.hl{color:var(--hl)}
.rule{height:12px;border-radius:6px;background:var(--blue);margin-top:26px;width:260px;transform-origin:left;transform:scaleX(0);animation:grow .6s cubic-bezier(.2,.8,.2,1) both}
@keyframes grow{to{transform:scaleX(1)}}
.kick{display:inline-flex;align-items:center;gap:16px;font-size:32px;font-weight:700;letter-spacing:3.5px;text-transform:uppercase;color:var(--soft);margin-bottom:36px}
.kick::before{content:"";width:16px;height:16px;border-radius:50%;background:var(--blue);box-shadow:0 0 0 8px rgba(37,99,255,.22)}
h1{font-family:Poppins;font-weight:700;font-size:104px;line-height:1.05;letter-spacing:-2.8px}
h2{font-family:Poppins;font-weight:700;font-size:84px;line-height:1.07;letter-spacing:-2px}
h3{font-family:Poppins;font-weight:700;font-size:68px;line-height:1.1;letter-spacing:-1.4px}
.def{font-size:46px;font-weight:500;line-height:1.32;margin-top:34px;color:var(--mut)}
.def b,.it b,.bb b{color:var(--hl);font-weight:700}
/* point */
.num{font-family:Poppins;font-weight:700;font-size:210px;line-height:.9;color:transparent;-webkit-text-stroke:5px var(--hl);margin-bottom:26px;letter-spacing:-6px}
.ex{align-self:stretch;margin-top:54px;border-radius:32px;padding:38px 42px;background:var(--card);border:2px solid var(--line)}
body.light .ex,body.light .card,body.light .row,body.light .nt{box-shadow:0 18px 50px rgba(16,23,42,.08)}
.lab{font-size:27px;font-weight:700;letter-spacing:3px;color:var(--soft);text-transform:uppercase;margin-bottom:22px}
.flow{display:flex;align-items:center;gap:20px;font-size:38px;font-weight:600;flex-wrap:wrap;line-height:1.3}
.quote{font-size:42px;font-weight:600;line-height:1.32}
.chip{background:#fff;color:#10172A;padding:14px 26px;border-radius:18px;border:2px solid var(--line)}
.chip.b{background:var(--blue);color:#fff;border-color:var(--blue)}
.arr{display:inline-block;width:70px;height:6px;border-radius:3px;background:var(--hl);position:relative;transform-origin:left;transform:scaleX(0);animation:grow .4s ease-out both}
.arr::after{content:"";position:absolute;right:-2px;top:-9px;width:18px;height:18px;border-top:6px solid var(--hl);border-right:6px solid var(--hl);transform:rotate(45deg);border-radius:2px}
/* liste */
.rows{align-self:stretch;display:flex;flex-direction:column;gap:22px;margin-top:50px}
.row{display:flex;align-items:center;gap:28px;padding:30px 34px;border-radius:28px;background:var(--card);border:2px solid var(--line)}
.it{font-size:42px;font-weight:600;line-height:1.25}
.ck{flex:none;width:64px;height:64px;border-radius:50%;background:var(--blue);display:flex;align-items:center;justify-content:center}
.ck.no{background:rgba(143,166,230,.22)} body.light .ck.no{background:#E7EBF7}
.ck svg{width:36px;height:36px;fill:none;stroke:#fff;stroke-width:3.4;stroke-linecap:round;stroke-linejoin:round}
.ck.no svg{stroke:var(--soft)}
.ck path{stroke-dasharray:40;stroke-dashoffset:40;animation:draw .35s ease-out both}
@keyframes draw{to{stroke-dashoffset:0}}
/* avant / après */
.cards{align-self:stretch;display:flex;flex-direction:column;gap:26px;margin-top:46px}
.card{border-radius:32px;padding:34px 38px;background:var(--card);border:2px solid var(--line)}
.card.good{border-color:var(--blue);background:rgba(37,99,255,.16)} body.light .card.good{background:#EEF3FF}
.card .it{display:flex;align-items:center;gap:22px;margin-top:18px;font-size:39px}
.card .ck{width:50px;height:50px} .card .ck svg{width:28px;height:28px}
.card.bad .it span{opacity:.72}
/* téléphone */
.phone{align-self:center;width:760px;height:680px;margin-top:46px;border-radius:70px 70px 0 0;border:12px solid #2B3555;border-bottom:0;background:#0B1022;padding:34px 30px 0;overflow:hidden;-webkit-mask-image:linear-gradient(180deg,#000 82%,transparent 100%);color:#fff}
body.light .phone{border-color:#10172A}
.ph{display:flex;align-items:center;gap:20px;padding:0 6px 26px;border-bottom:2px solid rgba(255,255,255,.1);margin-bottom:28px}
.av{width:72px;height:72px;border-radius:50%;background:var(--blue);display:flex;align-items:center;justify-content:center;font-family:Poppins;font-weight:700;font-size:34px}
.ph .n{font-size:32px;font-weight:700} .ph .s{font-size:24px;color:#8FA6E6;margin-top:2px}
.msgs{display:flex;flex-direction:column;gap:18px}
.bb{max-width:580px;font-size:39px;line-height:1.3;font-weight:500;padding:20px 26px;border-radius:30px;background:#1D2745;align-self:flex-start;border-bottom-left-radius:8px;transform-origin:left bottom}
.bb.out{align-self:flex-end;background:var(--blue);border-radius:30px;border-bottom-right-radius:8px;transform-origin:right bottom}
/* notifications */
.nts{align-self:stretch;display:flex;flex-direction:column;gap:22px;margin-top:50px}
.nt{display:flex;gap:26px;align-items:flex-start;padding:30px 32px;border-radius:34px;background:var(--card);border:2px solid var(--line);opacity:0;transform:translateY(-70px) scale(.94);animation:up .55s cubic-bezier(.34,1.4,.64,1) both}
.nt .ic{flex:none;width:78px;height:78px;border-radius:20px;background:var(--blue);color:#fff;display:flex;align-items:center;justify-content:center;font-family:Poppins;font-weight:700;font-size:36px}
.nt .a{display:flex;justify-content:space-between;font-size:25px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--soft)}
.nt .t{font-size:36px;font-weight:700;margin-top:6px} .nt .x{font-size:33px;line-height:1.3;color:var(--mut);margin-top:4px}
.nt>div:last-child{flex:1}
/* chiffre */
.big{font-family:Poppins;font-weight:700;font-size:300px;line-height:.95;letter-spacing:-10px;color:var(--hl);font-variant-numeric:tabular-nums}
/* fin */
.cta{display:inline-flex;align-items:center;gap:22px;margin-top:66px;background:#fff;color:#10172A;font-size:44px;font-weight:700;padding:30px 44px;border-radius:26px;box-shadow:0 18px 50px rgba(37,99,255,.35)}
body.light .cta{background:var(--blue);color:#fff} body.light .cta svg{stroke:#fff}
.pulse{animation:pulse 1.5s ease-in-out infinite both}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.045)}}
/* clip : plan filmé / photo plein écran + sous-titres natifs */
.media{position:absolute;inset:0;width:1080px;height:1920px;object-fit:cover}
.media.kb{animation:kb var(--d) linear both;transform-origin:50% 40%}
@keyframes kb{from{transform:scale(1.02)}to{transform:scale(1.12)}}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.5) 0%,rgba(0,0,0,0) 22%,rgba(0,0,0,0) 45%,rgba(0,0,0,.62) 100%)}
.cap{position:absolute;left:70px;right:70px;top:980px;display:flex;flex-direction:column;align-items:center;gap:6px;color:#fff}
.cap.exit{animation:exit .3s ease-in both;animation-delay:calc(var(--d) - .3s)}
.tag{background:#fff;color:#111;font-weight:700;font-size:38px;padding:12px 24px;border-radius:14px;transform:rotate(-2deg);margin-bottom:30px}
.cl{font-family:Poppins;font-weight:700;font-size:70px;line-height:1.16;letter-spacing:-1px;text-align:center;text-shadow:0 4px 22px rgba(0,0,0,.75),0 0 3px rgba(0,0,0,.9)}
.cl .cw{display:inline-block;opacity:0;transform:scale(.7) translateY(18px);animation:pop .32s cubic-bezier(.34,1.56,.64,1) both}
.cl .hl{color:#fff;background:var(--blue);border-radius:14px;padding:0 16px}
"""
CHECK = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" style="animation-delay:{t:.2f}s"/></svg>'
CROSS = '<svg viewBox="0 0 24 24"><path d="M7 7l10 10M17 7L7 17" style="animation-delay:{t:.2f}s"/></svg>'
SAVE = '<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#2563FF" stroke-width="2.4" stroke-linejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>'

JS = """
window.__tick = async (ms) => {
  document.getAnimations().forEach(a => { a.pause(); a.currentTime = ms; });
  document.querySelectorAll('[data-count]').forEach(e => {
    const c = JSON.parse(e.dataset.count); let p = Math.min(1, Math.max(0, (ms / 1000 - c.t) / c.d)); p = 1 - Math.pow(1 - p, 3);
    e.textContent = c.pre + (c.from + (c.to - c.from) * p).toFixed(c.dec).replace('.', ',') + c.suf; });
  const v = document.querySelector('img[data-frames]');
  if (v) { const n = +v.dataset.frames, k = Math.min(n - 1, Math.floor(ms / 1000 * 30 + 0.001)) + 1;
    v.src = v.dataset.dir + '/f' + String(k).padStart(4, '0') + '.jpg'; await v.decode(); }
};
window.__fit = async (ms) => {
  await window.__tick(ms); const sc = document.querySelector('.sc'), inn = document.querySelector('.inn');
  if (!sc || !inn) return 1; let z = 1;
  while (inn.getBoundingClientRect().height > sc.clientHeight && z > .6) { z -= .03; inn.style.zoom = z; }
  return z;
};
"""


def esc(t):
    """Texte → HTML : espaces insécables français, *mot* en bleu. Les balises <br> / <span> des anciens specs passent."""
    t = str(t)
    for p in ['?', '!', ';', ':', '»']:
        t = t.replace(' ' + p, ' ' + p)
    t = t.replace('« ', '« ')
    parts = t.split('*')
    return ''.join(f'<b>{p}</b>' if k % 2 else p for k, p in enumerate(parts)) if len(parts) > 2 else t


def words(line, t, step=.075, cw=False):
    """Découpe une ligne en mots animés un par un. Renvoie (html, instant de fin)."""
    line = str(line)
    for p in ['?', '!', ';', ':', '»']:
        line = line.replace(' ' + p, ' ' + p)
    line = line.replace('« ', '« ')
    out, on = [], False
    for tok in line.split(' '):
        if not tok:
            continue
        start = tok.startswith('*'); end = tok.rstrip('.,!?…').endswith('*') or tok.endswith('*')
        on = on or start
        txt = tok.replace('*', '')
        c = ' hl' if on else ''
        if cw:
            out.append(f'<span class="cw{c}" style="animation-delay:{t:.2f}s">{txt}</span>')
        else:
            out.append(f'<span class="w{c}"><i style="animation-delay:{t:.2f}s">{txt}</i></span>')
        if end:
            on = False
        t += step
    if cw:   # sous-titres : les mots surlignés forment un seul bloc bleu (pas une case par mot)
        merged = []
        for o in out:
            if 'class="cw hl"' in o and merged and 'class="cw hl"' in merged[-1]:
                inner = o.split('>', 1)[1].rsplit('</span>', 1)[0]
                merged[-1] = merged[-1].rsplit('</span>', 1)[0] + ' ' + inner + '</span>'
            else:
                merged.append(o)
        out = merged
    return ' '.join(out), t


def D(t):
    return f'style="animation-delay:{t:.2f}s"'


# ---------- scènes : chaque fonction renvoie (html, [(instant, son)]) ----------
def sc_hook(s, first):
    t = -0.6 if first else 0.12          # 1re scène : la 1re ligne est déjà lisible à l'image 0 (vignette + rétention)
    cues, h = [], ''
    if s.get('kicker'):
        h += f'<div class="kick up" {D(t)}>{esc(s["kicker"])}</div>'
    n = len(s['lines'])
    for k, l in enumerate(s['lines']):
        last = k == n - 1 and n > 1
        w, te = words(l, t + .1)
        h += f'<h1 class="{"hl" if last else ""}">{w}</h1>'
        if t > 0:
            cues.append((t + .1, 'tick'))
        t = max(te, t + .55)
    h += f'<div class="rule" {D(t)}></div>'
    cues.append((max(t, 0), 'pop'))
    return h, cues


def sc_point(s, first):
    cues, h, t = [], '', .1
    if s.get('num'):
        h += f'<div class="num pop" {D(t)}>{str(s["num"]).zfill(2)}</div>'; cues.append((t, 'pop'))
    w, te = words(s['title'], t + .2)
    h += f'<h2>{w}</h2>'
    if s.get('text'):
        h += f'<p class="def up" {D(te + .05)}>{esc(s["text"])}</p>'
    t = te + .55
    if s.get('chips'):
        a, b = s['chips'][:2]
        body = (f'<div class="flow"><span class="chip pop" {D(t + .3)}>{esc(a)}</span><span class="arr" {D(t + .6)}></span>'
                f'<span class="chip b pop" {D(t + .85)}>{esc(b)}</span></div>')
        cues += [(t + .3, 'tick'), (t + .85, 'pop')]
    elif s.get('ex_text'):
        body = f'<div class="quote">{esc(s["ex_text"])}</div>'
    else:
        body = None
    if body:
        h += f'<div class="ex side" {D(t)}><div class="lab">{esc(s.get("ex_label", "Exemple"))}</div>{body}</div>'
        cues.append((t, 'whoosh2'))
    return h, cues


def head(s, t=.1, tag='h3'):
    h = ''
    if s.get('kicker'):
        h += f'<div class="kick up" {D(t)}>{esc(s["kicker"])}</div>'
    te = t
    if s.get('title'):
        w, te = words(s['title'], t + .1)
        h += f'<{tag}>{w}</{tag}>'
    return h, te + .25


def sc_list(s, first):
    h, t = head(s)
    cues, rows = [], ''
    step = max(.45, min(.9, (s['dur'] - t - 1.2) / max(1, len(s['items']))))
    for it in s['items']:
        rows += (f'<div class="row up" {D(t)}><div class="ck pop" {D(t + .22)}>{CHECK.format(t=t + .42)}</div>'
                 f'<div class="it">{esc(it)}</div></div>')
        cues.append((t + .3, 'pop')); t += step
    return h + f'<div class="rows">{rows}</div>', cues


def sc_compare(s, first):
    h, t = head(s)
    cues, cards = [], ''
    for side, cls, ico in (('left', 'bad', CROSS), ('right', 'good', CHECK)):
        c = s[side]
        its = ''
        tt = t + .3
        for it in c['items']:
            its += (f'<div class="it up" {D(tt)}><div class="ck {"no" if cls == "bad" else ""}">{ico.format(t=tt + .2)}</div>'
                    f'<span>{esc(it)}</span></div>')
            tt += .28
        cards += f'<div class="card {cls} {"up" if cls == "bad" else "side"}" {D(t)}><div class="lab">{esc(c["label"])}</div>{its}</div>'
        cues.append((t, 'whoosh2' if cls == 'good' else 'tick'))
        t = tt + .35
    return h + f'<div class="cards">{cards}</div>', cues


def sc_phone(s, first):
    h, t = head(s)
    name = s.get('name', 'Client')
    cues, ms = [], ''
    step = max(.7, min(1.3, (s['dur'] - t - 1.0) / max(1, len(s['messages']))))
    t += .35
    for m in s['messages']:
        out = m.get('side') == 'out'
        ms += f'<div class="bb pop {"out" if out else ""}" {D(t)}>{esc(m["text"])}</div>'
        cues.append((t, 'pop' if out else 'msg')); t += step
    ph = (f'<div class="phone up" {D(.35)}><div class="ph"><div class="av">{htmllib.escape(name[:1].upper())}</div>'
          f'<div><div class="n">{esc(name)}</div><div class="s">{esc(s.get("sub", "maintenant"))}</div></div></div>'
          f'<div class="msgs">{ms}</div></div>')
    return h + ph, cues


def sc_notif(s, first):
    h, t = head(s)
    cues, ns = [], ''
    step = max(.6, min(1.1, (s['dur'] - t - 1.0) / max(1, len(s['notifs']))))
    for n in s['notifs']:
        app = n.get('app', 'Message')
        ns += (f'<div class="nt" {D(t)}><div class="ic">{htmllib.escape(app[:1].upper())}</div><div>'
               f'<div class="a"><span>{esc(app)}</span><span>{esc(n.get("time", "maintenant"))}</span></div>'
               f'<div class="t">{esc(n.get("title", ""))}</div><div class="x">{esc(n.get("text", ""))}</div></div></div>')
        cues.append((t, 'msg')); t += step
    return h + f'<div class="nts">{ns}</div>', cues


def sc_counter(s, first):
    h, t = '', .1
    if s.get('kicker'):
        h += f'<div class="kick up" {D(t)}>{esc(s["kicker"])}</div>'
    c = {'t': t + .2, 'd': min(1.6, s['dur'] * .4), 'from': s.get('from', 0), 'to': s['to'], 'dec': s.get('decimals', 0),
         'pre': s.get('prefix', ''), 'suf': s.get('suffix', '')}
    h += f"<div class=\"big pop\" {D(t + .1)} data-count='{json.dumps(c)}'></div>"
    if s.get('label'):
        w, _ = words(s['label'], c['t'] + c['d'] - .2)
        h += f'<h3 style="margin-top:20px">{w}</h3>'
    return h, [(t + .1, 'pop'), (c['t'] + c['d'], 'ding')]


def sc_end(s, first):
    cues, h, t = [], '', .12
    n = len(s['lines'])
    for k, l in enumerate(s['lines']):
        w, te = words(l, t)
        h += f'<h2 class="{"hl" if k == n - 1 and n > 1 else ""}">{w}</h2>'
        t = max(te, t + .45)
    if s.get('cta', True):
        cta = s.get('cta') if isinstance(s.get('cta'), str) else 'Enregistre pour t’en souvenir'
        h += f'<div class="pop" {D(t + .2)}><div class="cta pulse" {D(t + .7)}>{SAVE}{esc(cta)}</div></div>'
        cues.append((t + .2, 'ding'))
    return h, cues


SCENES = {'hook': sc_hook, 'point': sc_point, 'list': sc_list, 'compare': sc_compare, 'phone': sc_phone,
          'notif': sc_notif, 'counter': sc_counter, 'end': sc_end}


def bar(i, n):
    return '<div class="bar">' + ''.join('<s class="done"></s>' if j < i else ('<s><b></b></s>' if j == i else '<s></s>')
                                          for j in range(n)) + '</div>'


def page(spec, i, t0, total, work, base):
    """HTML complet d'une scène (sa propre ligne de temps démarre à 0) + sons."""
    s = spec['scenes'][i]; n = len(spec['scenes']); last = i == n - 1
    var = f'--T:{total}s;--t0:{t0}s;--d:{s["dur"]}s'
    if s['type'] == 'clip':
        src = s['src'] if os.path.isabs(s['src']) else os.path.join(base, s['src'])
        if not os.path.exists(src):
            sys.exit(f'Scène {i + 1} : fichier introuvable → {src}')
        if src.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            media = f'<img class="media kb" src="file://{src}">'
        else:
            fd = os.path.join(work, f'clip{i}'); os.makedirs(fd, exist_ok=True)
            nf = int(round(s['dur'] * FPS))
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(s.get('start', 0)), '-i', src, '-frames:v', str(nf), '-vf',
                            f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}',
                            '-q:v', '2', f'{fd}/f%04d.jpg'], check=True)
            got = len(os.listdir(fd))
            if got == 0:
                sys.exit(f'Scène {i + 1} : aucune image extraite de {src}')
            media = f'<img class="media" data-frames="{got}" data-dir="file://{fd}" src="file://{fd}/f0001.jpg">'
        t = -0.5 if i == 0 else .15
        cap, cues = '', []
        if s.get('tag'):
            cap += f'<div class="tag pop" {D(t)}>{esc(s["tag"])}</div>'
        for l in s.get('lines', []):
            w, te = words(l, t + .1, step=.13, cw=True)
            cap += f'<div class="cl">{w}</div>'
            if t > 0:
                cues.append((t + .1, 'tick'))
            t = te + .12
        body = f'{media}<div class="shade"></div>{bar(i, n)}<div class="cap {"" if last else "exit"}" style="top:{s.get("top", 980)}px">{cap}</div>'
        cls = ''
    else:
        inner, cues = SCENES[s['type']](s, i == 0)
        cls = 'light' if s.get('theme') == 'light' else ''
        panel = f'<div class="panel" style="{"clip-path:none;animation:none" if i == 0 else ""}"></div>' if cls else ''
        body = (f'<div class="bg"></div><div class="dots"></div>{panel}{bar(i, n)}<div class="tile"><img src="file://{MARK}"></div>'
                f'<div class="sc {"" if last else "exit"}"><div class="inn">{inner}</div></div>')
    if i > 0:
        cues.append((0, 'whoosh'))
    doc = (f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}</style></head>'
           f'<body class="{cls}" style="{var}">{body}<script>{JS}</script></body></html>')
    return doc, [(t0 + max(0, c), k) for c, k in cues if c < s['dur']]


def cover_html(c):
    tags = ''.join(f'<div>{t}</div>' for t in c.get('tags', []))
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}} html,body{{width:1080px;height:1920px;overflow:hidden}}
body{{font-family:Inter,sans-serif;color:#fff;background:radial-gradient(60% 38% at 86% 12%,#22379a 0%,rgba(16,23,42,0) 70%),radial-gradient(64% 40% at 8% 92%,#2a2466 0%,rgba(16,23,42,0) 70%),#10172A}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.07) 2px,transparent 2.5px);background-size:54px 54px;-webkit-mask-image:linear-gradient(180deg,transparent 0,#000 30%,#000 70%,transparent 100%)}}
.wrap{{position:absolute;left:90px;right:90px;top:285px;height:1350px;display:flex;flex-direction:column;justify-content:center}}
.tile{{display:inline-flex;align-items:center;justify-content:center;width:110px;height:110px;border-radius:28px;background:#fff;margin-bottom:70px}} .tile img{{height:74px}}
.k{{display:flex;align-items:center;gap:16px;font-size:36px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#8FA6E6;margin-bottom:34px}}
.k::before{{content:"";width:18px;height:18px;border-radius:50%;background:#2563FF;box-shadow:0 0 0 8px rgba(37,99,255,.22)}}
h1{{font-family:Poppins;font-weight:700;font-size:118px;line-height:1.03;letter-spacing:-3px}} h1 span{{color:#6F95FF}}
.r{{height:14px;width:280px;border-radius:7px;background:#2563FF;margin-top:44px}}
.tags{{display:flex;gap:18px;margin-top:60px;flex-wrap:wrap}} .tags div{{font-size:34px;font-weight:600;padding:16px 30px;border-radius:999px;border:2px solid rgba(255,255,255,.2);background:rgba(255,255,255,.06)}}
</style></head><body><div class="dots"></div><div class="wrap"><div><span class="tile"><img src="file://{MARK}"></span></div>
<div class="k">{c.get('kicker', '')}</div><h1>{esc(c['title'])}</h1><div class="r"></div><div class="tags">{tags}</div></div></body></html>"""


# ---------- son : musique + effets générés, libres de droits ----------
def soundtrack(total, starts, cues, path):
    from scipy.signal import butter, sosfilt
    from scipy.io import wavfile
    SR = 48000; N = int(total * SR); rng = np.random.default_rng(7)
    lp = lambda x, f: sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
    hp = lambda x, f: sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    mus, fx = np.zeros(N), np.zeros(N)

    def add(buf, sig, at, g=1.0):
        a = int(at * SR); b = min(N, a + len(sig))
        if 0 <= a < N:
            buf[a:b] += sig[:b - a] * g
    BPM = 100; beat = 60 / BPM
    prog = [([57, 60, 64, 67], 45), ([53, 57, 60, 64], 41), ([48, 55, 60, 64], 48), ([55, 59, 62, 66], 43)]   # Am7 Fmaj7 C G
    nb = int(total / beat) + 1
    body0 = starts[1] if len(starts) > 1 else 0          # la rythmique entre à la 2e scène
    for b in range(nb):
        t0 = b * beat; ch, root = prog[(b // 4) % 4]; pos = b % 4
        if pos == 0:                                       # nappe + basse
            L = int(beat * 4.4 * SR); tt = np.arange(L) / SR
            env = np.minimum(1, tt / .5) * np.minimum(1, (beat * 4.4 - tt) / .6)
            pad = sum(np.sin(2 * np.pi * hz(m) * 2 ** (d / 12) * tt) for m in ch for d in (-.07, .07))
            add(mus, lp(pad * env, 1400), t0, .022)
            add(mus, np.sin(2 * np.pi * hz(root - 12) * tt) * env, t0, .11)
        for e in range(2):                                 # arpège pincé en croches
            m = ch[(b * 2 + e) * 3 % len(ch)] + 12
            tt = np.arange(int(.5 * SR)) / SR
            pl = (np.sin(2 * np.pi * hz(m) * tt) + .3 * np.sin(4 * np.pi * hz(m) * tt)) * np.exp(-tt * 7) * np.minimum(1, tt / .004)
            add(mus, pl, t0 + e * beat / 2, .055)
        if t0 >= body0 - 1e-6:
            tt = np.arange(int(.3 * SR)) / SR
            if pos in (0, 2):
                add(mus, np.sin(2 * np.pi * np.cumsum(46 * (1 + 2.2 * np.exp(-tt * 38))) / SR) * np.exp(-tt * 9), t0, .34)
            if pos in (1, 3):
                add(mus, hp(rng.standard_normal(len(tt)), 2500) * np.exp(-tt * 26), t0, .05)
            hh = hp(rng.standard_normal(int(.04 * SR)), 8000) * np.exp(-np.arange(int(.04 * SR)) / SR * 90)
            add(mus, hh, t0 + beat / 2, .035)
    for at, kind in cues:
        if kind in ('whoosh', 'whoosh2'):
            L = int(.42 * SR); tt = np.arange(L) / SR
            nz = hp(rng.standard_normal(L), 900 if kind == 'whoosh' else 1800)
            add(fx, nz * np.sin(np.pi * tt / .42) ** 2, at - .2, .11 if kind == 'whoosh' else .06)
        elif kind in ('pop', 'tick', 'msg'):
            f0, d, g = {'pop': (620, .09, .2), 'tick': (1400, .03, .07), 'msg': (880, .13, .16)}[kind]
            tt = np.arange(int(d * SR)) / SR
            add(fx, np.sin(2 * np.pi * np.cumsum(f0 * (1 + .6 * tt / d)) / SR) * np.exp(-tt / d * 4), at, g)
            if kind == 'msg':
                add(fx, np.sin(2 * np.pi * 1320 * tt) * np.exp(-tt / d * 4), at + .09, g * .8)
        elif kind == 'ding':
            tt = np.arange(int(.9 * SR)) / SR
            add(fx, (np.sin(2 * np.pi * 1318.5 * tt) + .5 * np.sin(2 * np.pi * 1975.5 * tt)) * np.exp(-tt * 5), at, .12)
    t = np.arange(N) / SR
    mix = (mus + fx) * np.minimum(1, t / .25) * np.minimum(1, (total - t) / .9)
    mix = np.tanh(mix * 1.6); mix = mix / (np.abs(mix).max() + 1e-9) * .7
    wavfile.write(path, SR, (np.stack([mix, np.roll(mix, 180)], 1) * 32767).astype(np.int16))


def encode(frames, dst):
    """Images JPEG → un .mp4 par scène ; nom temporaire puis renommage quand ffmpeg a réussi."""
    tmp = dst[:-4] + '.part.mp4'
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-'] + ENC + [tmp],
                          stdin=subprocess.PIPE)
    for f in frames:
        ff.stdin.write(f)
    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit('ffmpeg a échoué sur ' + dst)
    os.replace(tmp, dst)


def sheet(shots, path):
    from PIL import Image
    import io
    tw, th = 360, 640
    im = Image.new('RGB', (tw * len(shots) + 8 * (len(shots) - 1), th), (40, 40, 40))
    for k, b in enumerate(shots):
        im.paste(Image.open(io.BytesIO(b)).resize((tw, th), Image.LANCZOS), (k * (tw + 8), 0))
    im.save(path, quality=90)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = {a for a in sys.argv[1:] if a.startswith('--')}
    if len(args) != 2:
        sys.exit(__doc__)
    spec = json.load(open(args[0])); out = os.path.abspath(args[1]); base = os.path.dirname(os.path.abspath(args[0]))
    os.makedirs(out, exist_ok=True)
    for i, s in enumerate(spec['scenes']):
        if s['type'] != 'clip' and s['type'] not in SCENES:
            sys.exit(f'Scène {i + 1} : type inconnu « {s["type"]} »')
    total = round(sum(s['dur'] for s in spec['scenes']), 3)
    cache = os.path.join(tempfile.gettempdir(), 'dd_reel_cache'); os.makedirs(cache, exist_ok=True)
    work = tempfile.mkdtemp(prefix='dd_reel_')
    preview = '--preview' in flags
    parts, cues, starts, shots, t0 = [], [], [], [], 0.0
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': W, 'height': H})
        for i, s in enumerate(spec['scenes']):
            doc, cs = page(spec, i, t0, total, work, base)
            cues += cs; starts.append(t0)
            key = hashlib.sha1((VERSION + doc + str(os.path.getmtime(os.path.join(base, s['src'])) if s['type'] == 'clip' and not os.path.isabs(s['src']) else '')).encode()).hexdigest()[:16]
            dst = os.path.join(cache, key + '.mp4')
            if preview or '--no-cache' in flags or not os.path.exists(dst):
                hp_ = os.path.join(work, f's{i}.html'); open(hp_, 'w').write(doc)
                pg.goto('file://' + hp_); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(250)
                end_ms = (s['dur'] - .45) * 1000
                z = pg.evaluate('ms=>window.__fit(ms)', end_ms)
                if z < .8:
                    print(f'ATTENTION scène {i + 1} ({s["type"]}) : contenu trop long, réduit à {int(z * 100)} % — raccourcis le texte.', file=sys.stderr)
                if preview:
                    if i == 0:
                        pg.evaluate('ms=>window.__tick(ms)', 0); shots.append(pg.screenshot(type='jpeg', quality=88))
                    pg.evaluate('ms=>window.__tick(ms)', end_ms); shots.append(pg.screenshot(type='jpeg', quality=88))
                else:
                    def gen():
                        for k in range(int(round(s['dur'] * FPS))):
                            pg.evaluate('ms=>window.__tick(ms)', k * 1000 / FPS)
                            yield pg.screenshot(type='jpeg', quality=92)
                    encode(gen(), dst)
                    print(f'  scène {i + 1}/{len(spec["scenes"])} ({s["type"]}, {s["dur"]} s)', file=sys.stderr)
            parts.append(dst); t0 += s['dur']
        if spec.get('cover') and not preview:
            cp = os.path.join(work, 'cover.html'); open(cp, 'w').write(cover_html(spec['cover']))
            pg.goto('file://' + cp); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(250)
            pg.screenshot(path=os.path.join(out, f'{spec["name"]}_couverture.png'))
        b.close()
    if preview:
        f = os.path.join(out, f'{spec["name"]}_apercu.jpg'); sheet(shots, f); shutil.rmtree(work); print(f); return
    lst = os.path.join(work, 'list.txt'); open(lst, 'w').write(''.join(f"file '{x}'\n" for x in parts))
    silent = os.path.join(work, 'silent.mp4')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', silent], check=True)
    final = os.path.join(out, f'{spec["name"]}.mp4'); tmp = final[:-4] + '.part.mp4'
    audio = spec.get('audio', True) if '--no-audio' not in flags else False
    if audio:
        if isinstance(audio, str):
            a = audio if os.path.isabs(audio) else os.path.join(base, audio)
            af = ['-af', f'afade=t=in:d=0.3,afade=t=out:st={max(0, total - 1):.2f}:d=1']
        else:
            a = os.path.join(work, 'son.wav'); soundtrack(total, starts, cues, a); af = []
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', a, '-map', '0:v', '-map', '1:a', '-c:v', 'copy'] + af +
                       ['-c:a', 'aac', '-b:a', '192k', '-t', str(total), '-movflags', '+faststart', tmp], check=True)
    else:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-c', 'copy', '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, final); shutil.rmtree(work)
    print(final)


if __name__ == '__main__':
    main()

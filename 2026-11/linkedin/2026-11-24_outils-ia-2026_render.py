import os
from playwright.sync_api import sync_playwright
R=''+os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))+''
CSS=open(R+'/kit/templates/carousel.css').read()
MARK=R+'/kit/brand/mark.png'
cats=[("Assistants IA","Avis, publications, e‑mails",["ChatGPT","Claude","Mistral"]),
      ("Automatisation","Relier vos outils, sans ressaisie",["Make","n8n","Zapier"]),
      ("Messages privés","Réponses et tri sur Instagram",["ManyChat"]),
      ("Avis et visibilité","Suivre et répondre aux avis",["Malou","MARA"]),
      ("Stocks et coûts","Inventaires, coût matière",["Apicbase","MarketMan"]),
      ("Tableaux","Gratuits, pour démarrer",["Google Sheets","Forms"])]
cards=''.join(f'''<div class="c"><div class="h"><span class="n">{i+1}</span><span class="t">{t}</span></div>
<div class="d">{d}</div><div class="tl">{''.join(f'<span>{x}</span>' for x in tools)}</div></div>''' for i,(t,d,tools) in enumerate(cats))
html=f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>{CSS}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:38px}}
.c{{background:rgba(255,255,255,.06);border:2px solid rgba(255,255,255,.13);border-radius:28px;padding:24px 26px 24px}}
.c .h{{display:flex;align-items:center;gap:16px}}
.c .n{{flex:none;width:46px;height:46px;border-radius:14px;background:#2563FF;display:flex;align-items:center;justify-content:center;font-family:Poppins;font-weight:700;font-size:24px}}
.c .t{{font-family:Poppins;font-weight:700;font-size:33px;letter-spacing:-.5px}}
.c .d{{font-size:22px;color:#B9C4E4;margin:10px 0 14px;white-space:nowrap;line-height:1.3}}
.c .tl{{display:flex;flex-wrap:wrap;gap:10px}}
.c .tl span{{background:#fff;color:#10172A;font-weight:700;font-size:22px;padding:8px 14px;border-radius:12px}}
.rule{{margin-top:auto;display:flex;align-items:center;gap:18px;background:#fff;color:#10172A;border-radius:24px;padding:24px 30px;font-size:29px;font-weight:600}}
.rule b{{color:#2563FF}}
.top{{margin-bottom:40px}} .s{{padding:72px 80px 70px}} .brand img{{height:40px}}
</style></head><body style="margin:0">
<div class="s dark" id="s1"><div class="top"><div class="brand"><span class="tile"><img src="file://{MARK}"></span></div></div>
<div class="kicker">Restaurants · Hôtels · Outils 2026</div>
<h2 style="font-size:64px">Les outils IA et automatisation <span class="hl">pour vous équiper</span></h2>
<div class="grid">{cards}</div>
<div class="rule" style="margin-top:30px">Une règle : <b>l'IA prépare, un humain valide.</b></div>
</div></body></html>'''
open('/home/claude/li48/outils.html','w').write(html)
out=R+'/2026-11/linkedin/2026-11-24_linkedin_outils-ia-2026_1.png'
with sync_playwright() as p:
    b=p.chromium.launch(args=['--no-sandbox']);pg=b.new_page(viewport={'width':1080,'height':1350})
    pg.goto('file:///home/claude/li48/outils.html');pg.evaluate('document.fonts.ready');pg.wait_for_timeout(400)
    h=pg.evaluate("document.getElementById('s1').scrollHeight")
    print('hauteur contenu',h)
    pg.locator('#s1').screenshot(path=out);b.close()
print(out)

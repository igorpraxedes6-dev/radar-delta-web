#!/usr/bin/env python3
"""
blog.py — o "Funding Diary": publica 1 post/dia (EN + PT) com os dados do funding,
gera o indice e o RSS. Roda no GitHub Actions DENTRO do repo radar-delta-web e
commita nele mesmo (sem PAT, sem cross-repo).

Por que existe: cada post vira pagina indexavel no Google (SEO global, em ingles),
o RSS deixa a galera seguir, e tudo puxa publico mundial pro canal. Ativo que cresce
sozinho, custo zero.

Modos:
  python3 blog.py            # gera o post de hoje + reconstroi index + rss
  python3 blog.py --dry-run  # so imprime o resumo, nao escreve arquivo

Saida (relativa ao diretorio atual):
  blog/YYYY-MM-DD.html   um post por dia
  blog/index.html        lista de todos os posts (mais novo primeiro)
  blog/rss.xml           feed RSS
  blog/posts.json        manifest (nao reparseia HTML)
"""
import json, os, sys, html, urllib.request
from datetime import datetime, timezone

BASE = "https://igorpraxedes6-dev.github.io/radar-delta-web"
TOOL = BASE + "/"
CHAN = "https://t.me/radardeltabr"
OG   = BASE + "/og.png"
OUT  = os.path.join(os.getcwd(), "blog")

def gj(u):
    r = urllib.request.Request(u, headers={"User-Agent":"radardelta/1.0"})
    return json.loads(urllib.request.urlopen(r, timeout=20).read())

def coleta_binance():
    prem = gj("https://fapi.binance.com/fapi/v1/premiumIndex")
    vol  = {d["symbol"]: float(d.get("quoteVolume",0)) for d in gj("https://fapi.binance.com/fapi/v1/ticker/24hr")}
    itv  = {d["symbol"]: int(d.get("fundingIntervalHours",8)) for d in gj("https://fapi.binance.com/fapi/v1/fundingInfo")}
    out = []
    for d in prem:
        s = d["symbol"]
        if not s.endswith("USDT"): continue
        r = float(d["lastFundingRate"]); h = itv.get(s,8); v = vol.get(s,0)
        if v >= 50e6 and r > 0:
            out.append({"sym":s.replace("USDT",""),"apr":r*(24/h)*365*100,"vol":v,"rate":r,"ex":"Binance"})
    return out

def coleta_bybit():
    l = gj("https://api.bybit.com/v5/market/tickers?category=linear")["result"]["list"]
    out = []
    for d in l:
        s = d["symbol"]
        if not s.endswith("USDT") or not d.get("fundingRate"): continue
        r = float(d["fundingRate"]); v = float(d.get("turnover24h",0))
        if v >= 50e6 and r > 0:
            out.append({"sym":s.replace("USDT",""),"apr":r*3*365*100,"vol":v,"rate":r,"ex":"Bybit"})
    return out

def coleta():
    for fonte in (coleta_binance, coleta_bybit):
        try:
            out = fonte()
            if out:
                out.sort(key=lambda x: x["apr"], reverse=True)
                return out
        except Exception as e:
            print(f"[{fonte.__name__} falhou: {e}] proxima fonte", file=sys.stderr)
    return []

def fvol(v): return f"${v/1e9:.1f}B" if v>=1e9 else f"${v/1e6:.0f}M"

CSS = """*{box-sizing:border-box}body{margin:0;background:#0b0e14;color:#e6edf3;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.6}
a{color:#58a6ff;text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:760px;margin:0 auto;padding:28px 20px 70px}
header{border-bottom:1px solid #232a36;padding-bottom:16px;margin-bottom:24px}
.logo{font-weight:700;font-size:19px}.logo span{color:#e3b341}
.muted{color:#8b98a9;font-size:13px}
h1{font-size:25px;line-height:1.25;margin:6px 0 4px}
h2{font-size:16px;color:#8b98a9;text-transform:uppercase;letter-spacing:.5px;margin:30px 0 10px;border-bottom:1px solid #232a36;padding-bottom:6px}
table{width:100%;border-collapse:collapse;font-size:14px;margin:12px 0}
th{text-align:right;color:#8b98a9;font-size:11px;text-transform:uppercase;letter-spacing:.5px;padding:8px 10px;border-bottom:1px solid #232a36}
th.l,td.l{text-align:left}td{padding:9px 10px;border-bottom:1px solid #1a212c}
.g{color:#3fb950;font-weight:700}.tag{background:#1b2230;color:#8b98a9;font-size:11px;padding:2px 7px;border-radius:5px}
.cta{display:inline-block;background:#2f81f7;color:#fff;font-weight:600;padding:10px 18px;border-radius:999px;margin:8px 8px 0 0}
.cta.alt{background:transparent;border:1px solid #3fb950;color:#3fb950}
.disc{color:#8b98a9;font-size:12.5px;border-left:3px solid #e3b341;padding:6px 12px;margin:22px 0;background:#121826}
.postlist a{display:block;padding:13px 0;border-bottom:1px solid #1a212c;font-size:16px}
.postlist .muted{display:block}
footer{margin-top:40px;color:#8b98a9;font-size:12px;border-top:1px solid #232a36;padding-top:16px}"""

def head(title, desc, canon, og_title):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<link rel="alternate" type="application/rss+xml" title="Radar Delta — Funding Diary" href="{BASE}/blog/rss.xml">
<meta property="og:type" content="article"><meta property="og:site_name" content="Radar Delta">
<meta property="og:title" content="{html.escape(og_title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{OG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(og_title)}"><meta name="twitter:image" content="{OG}">
<style>{CSS}</style></head><body><div class="wrap">
<header><div class="logo">📡 Radar <span>Delta</span></div>
<div class="muted">Funding Diary · live funding rates, Binance + Bybit · <a href="{TOOL}">live radar</a> · <a href="{BASE}/blog/">all posts</a></div></header>"""

FOOT = f"""<footer>Radar Delta — data, not financial advice. Funding rates change by the hour.<br>
Live tool: <a href="{TOOL}">{BASE.replace('https://','')}</a> · Free channel: <a href="{CHAN}">t.me/radardeltabr</a></footer>
</div></body></html>"""

def tabela(rows):
    out = ['<table><tr><th class="l">#</th><th class="l">Coin</th><th class="l">Exchange</th><th>Funding</th><th>APR / year</th><th>24h vol</th></tr>']
    for i,r in enumerate(rows,1):
        out.append(f'<tr><td class="l muted">{i}</td><td class="l"><b>{html.escape(r["sym"])}</b></td>'
                   f'<td class="l"><span class="tag">{r["ex"]}</span></td>'
                   f'<td>{r["rate"]*100:.3f}%</td><td class="g">+{r["apr"]:.0f}%</td><td>{fvol(r["vol"])}</td></tr>')
    out.append('</table>')
    return "".join(out)

def gerar_post(rows, dry=False):
    rows = rows[:6]
    if not rows: return None
    now = datetime.now(timezone.utc)
    slug = now.strftime("%Y-%m-%d")
    dstr = now.strftime("%b %d, %Y")
    top = rows[0]; liq = max(rows, key=lambda x:x["vol"])
    title = f"Top funding rates today — {dstr} (Binance + Bybit) | Radar Delta"
    ogt   = f"Top funding rates — {dstr}"
    desc  = (f"{top['sym']} leads at +{top['apr']:.0f}%/yr funding. "
             f"Most liquid: {liq['sym']} ({fvol(liq['vol'])}). Live delta-neutral funding radar, free.")
    canon = f"{BASE}/blog/{slug}.html"
    body = f"""{head(title,desc,canon,ogt)}
<h1>Top funding rates today — {dstr}</h1>
<div class="muted">{now.strftime('%H:%M UTC')} · ranked by annualized funding · 24h volume ≥ $50M</div>

<p><b>{html.escape(top['sym'])}</b> is paying the most right now: funding of {top['rate']*100:.3f}% per interval
(~<span class="g">+{top['apr']:.0f}%/year</span> if it held). The most liquid name on the board is
<b>{html.escape(liq['sym'])}</b> at {fvol(liq['vol'])} 24h volume — the easiest to enter and exit without the spread eating you.</p>

{tabela(rows)}

<p><b>How to read this (delta-neutral):</b> buy the coin on spot and short the same size on the perpetual.
The price can go anywhere — one leg covers the other — and you collect the funding. High funding decays in
hours, so this is a snapshot of where the carry is fat, not a buy signal.</p>

<a class="cta" href="{TOOL}">Open the live radar →</a>
<a class="cta alt" href="{CHAN}">Join the free channel</a>

<div class="disc">Data, not financial advice. Funding rates change every few hours — always check the live radar before acting.</div>

<h2>Em português</h2>
<p><b>{html.escape(top['sym'])}</b> é quem mais paga funding agora: {top['rate']*100:.3f}% por intervalo
(~<span class="g">+{top['apr']:.0f}%/ano</span> se mantivesse). O mais líquido da lista é
<b>{html.escape(liq['sym'])}</b> com {fvol(liq['vol'])} de volume 24h — o mais fácil de entrar e sair sem o spread te comer.</p>
<p><b>Como ler (delta-neutro):</b> compra no spot e vende o mesmo tamanho no perpétuo. O preço vai pra onde quiser —
um lado cobre o outro — e você fica com o funding. Funding alto decai em horas: é foto de onde o carry tá gordo, não sinal de compra.</p>
<a class="cta" href="{TOOL}">Abrir o radar ao vivo →</a>
<a class="cta alt" href="{CHAN}">Entrar no canal grátis</a>
<div class="disc">Dado, não recomendação. O funding muda de hora em hora — confira o radar ao vivo antes de operar.</div>
{FOOT}"""
    meta = {"slug":slug,"title":ogt,"date":now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pub":now.strftime("%a, %d %b %Y %H:%M:%S +0000"),"desc":desc}
    if dry:
        print(f"[dry-run] {slug}: {ogt}\n  {desc}\n  top={top['sym']} +{top['apr']:.0f}% · liq={liq['sym']} {fvol(liq['vol'])}")
        return meta
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT,f"{slug}.html"),"w") as f: f.write(body)
    return meta

def manifest_upsert(meta):
    p = os.path.join(OUT,"posts.json")
    posts = []
    if os.path.exists(p):
        posts = json.load(open(p))
    posts = [x for x in posts if x["slug"] != meta["slug"]]  # hoje sobrescreve
    posts.append(meta)
    posts.sort(key=lambda x:x["slug"], reverse=True)
    json.dump(posts, open(p,"w"), indent=2)
    return posts

def gerar_index(posts):
    title = "Radar Delta — Funding Diary (daily funding rate reports)"
    desc  = "Daily report of the highest crypto funding rates on Binance and Bybit. Delta-neutral, no hype. Free."
    canon = f"{BASE}/blog/"
    items = ['<div class="postlist">']
    for x in posts:
        items.append(f'<a href="{x["slug"]}.html">{html.escape(x["title"])}'
                     f'<span class="muted">{html.escape(x["desc"])}</span></a>')
    items.append('</div>')
    body = f"""{head(title,desc,canon,"Radar Delta — Funding Diary")}
<h1>Funding Diary</h1>
<p class="muted">Daily snapshot of where crypto funding is fattest — Binance + Bybit, delta-neutral.
Follow via <a href="rss.xml">RSS</a> or the <a href="{CHAN}">free Telegram</a>. / Relatório diário do funding mais gordo em cripto.</p>
{"".join(items)}
{FOOT}"""
    with open(os.path.join(OUT,"index.html"),"w") as f: f.write(body)

def gerar_rss(posts):
    its = []
    for x in posts[:40]:
        link = f"{BASE}/blog/{x['slug']}.html"
        its.append(f"""<item><title>{html.escape(x['title'])}</title>
<link>{link}</link><guid>{link}</guid>
<pubDate>{x['pub']}</pubDate>
<description>{html.escape(x['desc'])}</description></item>""")
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>Radar Delta — Funding Diary</title>
<link>{BASE}/blog/</link>
<description>Daily highest crypto funding rates, Binance + Bybit. Data, not advice.</description>
<language>en</language>
{"".join(its)}
</channel></rss>"""
    with open(os.path.join(OUT,"rss.xml"),"w") as f: f.write(rss)

if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    meta = gerar_post(coleta(), dry)
    if not meta:
        print("sem dado de funding agora — nao gera post (integridade)"); sys.exit(0)
    if dry: sys.exit(0)
    posts = manifest_upsert(meta)
    gerar_index(posts)
    gerar_rss(posts)
    print(f"post gerado: blog/{meta['slug']}.html · {len(posts)} post(s) no total")

#!/usr/bin/env python3
"""
seo.py — ativos de atracao organica do Radar Delta (roda no repo radar-delta-web):

  #1  cards/card.svg        card do dia "Top Funding" (o workflow vira PNG via Chrome)
  #2  coin/<MOEDA>.html     1 pagina por moeda-major -> SEO ("BTC funding rate live")
  #3  vs-binance-bybit.html comparativo Binance x Bybit (SEO alta-intencao + afiliado)
      sitemap.xml + robots.txt   pro Google achar e indexar tudo rapido

Modo:
  python3 seo.py             # gera tudo
  python3 seo.py --dry-run   # so imprime o resumo

Self-contained (coleta propria, fallback Binance->Bybit). Nao posta nada.
"""
import json, os, sys, html, urllib.request
from datetime import datetime, timezone

BASE = "https://igorpraxedes6-dev.github.io/radar-delta-web"
TOOL = BASE + "/"
CHAN = "https://t.me/radardeltabr"
OGIMG = BASE + "/cards/card.png"
CWD  = os.getcwd()
# trocar pelos links REAIS de afiliado (ponto unico aqui + no radar-painel.html)
AFF_BNC = "https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00DDWW0Y3L"
AFF_BYB = "https://www.bybit.com/invite"

# moedas-major que a galera realmente pesquisa (nao alt obscura = evita conteudo fino)
COINS = ["BTC","ETH","SOL","XRP","BNB","DOGE","ADA","AVAX","LINK","DOT",
         "LTC","TRX","NEAR","APT","ARB","OP","SUI","PEPE","INJ","TIA"]
NOMES = {"BTC":"Bitcoin","ETH":"Ethereum","SOL":"Solana","XRP":"XRP","BNB":"BNB",
         "DOGE":"Dogecoin","ADA":"Cardano","AVAX":"Avalanche","LINK":"Chainlink",
         "DOT":"Polkadot","LTC":"Litecoin","TRX":"TRON","NEAR":"NEAR","APT":"Aptos",
         "ARB":"Arbitrum","OP":"Optimism","SUI":"Sui","PEPE":"Pepe","INJ":"Injective","TIA":"Celestia"}

def gj(u):
    r = urllib.request.Request(u, headers={"User-Agent":"radardelta/1.0"})
    return json.loads(urllib.request.urlopen(r, timeout=20).read())

def mapa_binance():
    prem = gj("https://fapi.binance.com/fapi/v1/premiumIndex")
    vol  = {d["symbol"]: float(d.get("quoteVolume",0)) for d in gj("https://fapi.binance.com/fapi/v1/ticker/24hr")}
    itv  = {d["symbol"]: int(d.get("fundingIntervalHours",8)) for d in gj("https://fapi.binance.com/fapi/v1/fundingInfo")}
    m = {}
    for d in prem:
        s = d["symbol"]
        if not s.endswith("USDT"): continue
        r = float(d["lastFundingRate"]); h = itv.get(s,8)
        m[s[:-4]] = {"rate":r, "apr":r*(24/h)*365*100, "vol":vol.get(s,0)}
    return m

def mapa_bybit():
    l = gj("https://api.bybit.com/v5/market/tickers?category=linear")["result"]["list"]
    m = {}
    for d in l:
        s = d["symbol"]
        if not s.endswith("USDT") or not d.get("fundingRate"): continue
        r = float(d["fundingRate"])
        m[s[:-4]] = {"rate":r, "apr":r*3*365*100, "vol":float(d.get("turnover24h",0))}
    return m

def coleta_maps():
    bnc, byb = {}, {}
    try: bnc = mapa_binance()
    except Exception as e: print(f"[binance falhou: {e}]", file=sys.stderr)
    try: byb = mapa_bybit()
    except Exception as e: print(f"[bybit falhou: {e}]", file=sys.stderr)
    return bnc, byb

def fvol(v): return f"${v/1e9:.1f}B" if v>=1e9 else (f"${v/1e6:.0f}M" if v>=1e6 else f"${v/1e3:.0f}K")
def fapr(a): return ("+" if a>=0 else "") + f"{a:.0f}%"
def cls(a):  return "g" if a>0 else ("r" if a<0 else "")

CSS = """*{box-sizing:border-box}body{margin:0;background:#0b0e14;color:#e6edf3;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.6}
a{color:#58a6ff;text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:820px;margin:0 auto;padding:28px 20px 70px}
header{border-bottom:1px solid #232a36;padding-bottom:16px;margin-bottom:24px}
.logo{font-weight:700;font-size:19px}.logo span{color:#e3b341}
.muted{color:#8b98a9;font-size:13px}
h1{font-size:26px;line-height:1.22;margin:6px 0 4px}
h2{font-size:16px;color:#8b98a9;text-transform:uppercase;letter-spacing:.5px;margin:30px 0 10px;border-bottom:1px solid #232a36;padding-bottom:6px}
table{width:100%;border-collapse:collapse;font-size:14px;margin:12px 0}
th{text-align:right;color:#8b98a9;font-size:11px;text-transform:uppercase;letter-spacing:.5px;padding:8px 10px;border-bottom:1px solid #232a36}
th.l,td.l{text-align:left}td{padding:9px 10px;border-bottom:1px solid #1a212c}
.g{color:#3fb950;font-weight:700}.r{color:#f85149;font-weight:700}.tag{background:#1b2230;color:#8b98a9;font-size:11px;padding:2px 7px;border-radius:5px}
.big{font-size:30px;font-weight:800}.win{color:#3fb950}
.cta{display:inline-block;background:#2f81f7;color:#fff;font-weight:600;padding:10px 18px;border-radius:999px;margin:8px 8px 0 0}
.cta.alt{background:transparent;border:1px solid #3fb950;color:#3fb950}
.cta.bnc{background:#f0b90b;color:#121212}.cta.byb{background:#f7a600;color:#121212}
.disc{color:#8b98a9;font-size:12.5px;border-left:3px solid #e3b341;padding:6px 12px;margin:22px 0;background:#121826}
.grid{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}
.grid a{background:#121826;border:1px solid #232a36;border-radius:8px;padding:10px 14px;font-weight:600}
footer{margin-top:40px;color:#8b98a9;font-size:12px;border-top:1px solid #232a36;padding-top:16px}"""

def head(title, desc, canon):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Radar Delta">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{OGIMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}"><meta name="twitter:image" content="{OGIMG}">
<style>{CSS}</style></head><body><div class="wrap">
<header><div class="logo">📡 Radar <span>Delta</span></div>
<div class="muted">Live funding rates · Binance + Bybit · <a href="{TOOL}">live radar</a> · <a href="{BASE}/blog/">blog</a> · <a href="{BASE}/vs-binance-bybit.html">Binance vs Bybit</a></div></header>"""

def FOOT():
    return (f'<footer>Radar Delta — data, not financial advice. Funding rates change by the hour.<br>'
            f'Live tool: <a href="{TOOL}">radar</a> · Free channel: <a href="{CHAN}">t.me/radardeltabr</a></footer></div></body></html>')

# ---------- #2 paginas por moeda ----------
def pagina_moeda(sym, bnc, byb, dstr):
    nome = NOMES.get(sym, sym)
    b = bnc.get(sym); y = byb.get(sym)
    title = f"{sym} funding rate live — {nome} perpetual (Binance + Bybit) | Radar Delta"
    desc  = f"Live {sym} ({nome}) perpetual funding rate on Binance and Bybit, updated daily. See who pays and how to run it delta-neutral. Free."
    canon = f"{BASE}/coin/{sym}.html"
    rows = []
    for ex,d in (("Binance",b),("Bybit",y)):
        if d: rows.append(f'<tr><td class="l"><span class="tag">{ex}</span></td>'
                          f'<td class="{cls(d["rate"])}">{d["rate"]*100:.4f}%</td>'
                          f'<td class="{cls(d["apr"])}">{fapr(d["apr"])}</td><td>{fvol(d["vol"])}</td></tr>')
        else: rows.append(f'<tr><td class="l"><span class="tag">{ex}</span></td><td class="muted">—</td><td class="muted">—</td><td class="muted">—</td></tr>')
    # leitura
    best = None
    if b and y: best = ("Binance" if b["apr"]>=y["apr"] else "Bybit")
    elif b: best = "Binance"
    elif y: best = "Bybit"
    lead = (f'On the snapshot below, <b>{best}</b> pays the higher {sym} funding right now.' if best
            else f'No liquid {sym} perp funding on the tracked venues at this snapshot.')
    body = f"""{head(title,desc,canon)}
<h1>{sym} funding rate — live ({nome})</h1>
<div class="muted">snapshot {dstr} · updates daily · <a href="{TOOL}">see it live</a></div>
<p>{lead} Funding is what longs and shorts pay each other on the perpetual — when it is positive, longs pay shorts, so a delta-neutral trader who is short the perp (and long spot) collects it.</p>
<table><tr><th class="l">Exchange</th><th>Funding / interval</th><th>APR / year</th><th>24h vol</th></tr>
{''.join(rows)}</table>
<p><b>How to capture it (delta-neutral):</b> buy {sym} on spot and short the same size on the {sym} perpetual.
Price moves cancel out between the two legs; you keep the funding. High funding decays fast, so check the live radar before acting.</p>
<a class="cta" href="{TOOL}">Open the live {sym} radar →</a>
<a class="cta alt" href="{CHAN}">Get daily alerts (free)</a>
<h2>Trade {sym} funding</h2>
<a class="cta bnc" href="{AFF_BNC}" rel="sponsored nofollow">Open Binance account</a>
<a class="cta byb" href="{AFF_BYB}" rel="sponsored nofollow">Open Bybit account</a>
<p class="muted">Partner links. Operating perps carries risk.</p>
<div class="disc">Data, not financial advice. {sym} funding changes every few hours.</div>
<h2>Other coins</h2>
<div class="grid">{''.join(f'<a href="{c}.html">{c}</a>' for c in COINS if c!=sym)}</div>
{FOOT()}"""
    return canon, body

# ---------- #3 comparativo ----------
def pagina_vs(bnc, byb, dstr):
    title = "Binance vs Bybit funding rates — live comparison | Radar Delta"
    desc  = "Compare funding rates on Binance and Bybit side by side for the major coins, updated daily. See which exchange pays more for delta-neutral carry."
    canon = f"{BASE}/vs-binance-bybit.html"
    rows=[]; bwin=ywin=0
    for c in COINS:
        b=bnc.get(c); y=byb.get(c)
        if not b and not y: continue
        ba = b["apr"] if b else None; ya = y["apr"] if y else None
        win=""
        if ba is not None and ya is not None:
            if ba>ya: win="Binance"; bwin+=1
            elif ya>ba: win="Bybit"; ywin+=1
        rows.append(f'<tr><td class="l"><b>{c}</b></td>'
                    f'<td class="{cls(ba) if ba is not None else ""}">{fapr(ba) if ba is not None else "—"}</td>'
                    f'<td class="{cls(ya) if ya is not None else ""}">{fapr(ya) if ya is not None else "—"}</td>'
                    f'<td class="l win">{win}</td></tr>')
    body = f"""{head(title,desc,canon)}
<h1>Binance vs Bybit — funding rates compared</h1>
<div class="muted">snapshot {dstr} · annualized funding (APR) · updates daily · <a href="{TOOL}">live radar</a></div>
<p>Both exchanges run perpetual funding, but the rate for the same coin often differs — and that gap is exactly
what a delta-neutral trader hunts. Below, the APR each venue pays right now on the major coins. On this snapshot,
<b>Binance</b> pays more on {bwin} and <b>Bybit</b> on {ywin}.</p>
<table><tr><th class="l">Coin</th><th>Binance APR</th><th>Bybit APR</th><th class="l">Higher</th></tr>
{''.join(rows)}</table>
<p><b>The cross-exchange play:</b> you can even go long the funding on the cheaper venue and short it on the richer
one. The live radar has a dedicated Cross-Exchange tab for exactly this.</p>
<a class="cta" href="{TOOL}">Open the live radar →</a>
<a class="cta alt" href="{CHAN}">Daily funding alerts (free)</a>
<h2>Open accounts</h2>
<a class="cta bnc" href="{AFF_BNC}" rel="sponsored nofollow">Binance</a>
<a class="cta byb" href="{AFF_BYB}" rel="sponsored nofollow">Bybit</a>
<p class="muted">Partner links. Perps carry risk.</p>
<div class="disc">Data, not financial advice. Rates change every few hours — check the live radar.</div>
{FOOT()}"""
    return canon, body

# ---------- #1 card do dia (SVG; workflow vira PNG) ----------
def card_svg(bnc, byb, dstr):
    top=[]
    for c in COINS:
        for ex,m in (("Binance",bnc),("Bybit",byb)):
            d=m.get(c)
            if d and d["vol"]>=30e6: top.append({"sym":c,"ex":ex,"apr":d["apr"]})
    top.sort(key=lambda x:x["apr"], reverse=True); top=top[:5]
    linhas=[]
    y=250
    med=["1","2","3","4","5"]
    for i,r in enumerate(top):
        linhas.append(
            f'<text x="90" y="{y}" fill="#8b98a9" font-size="34" font-family="Helvetica,Arial" font-weight="700">{med[i]}</text>'
            f'<text x="140" y="{y}" fill="#f4f2ea" font-size="38" font-family="Helvetica,Arial" font-weight="800">{html.escape(r["sym"])}</text>'
            f'<text x="430" y="{y}" fill="#8b98a9" font-size="26" font-family="Helvetica,Arial">{r["ex"]}</text>'
            f'<text x="1110" y="{y}" fill="#3fb950" font-size="38" font-family="Helvetica,Arial" font-weight="800" text-anchor="end">+{r["apr"]:.0f}%/yr</text>')
        y+=74
    return f"""<svg width="1200" height="630" viewBox="0 0 1200 630" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
<stop offset="0%" stop-color="#121a28"/><stop offset="100%" stop-color="#080b11"/></linearGradient></defs>
<rect width="1200" height="630" fill="url(#bg)"/>
<g transform="translate(1060,120)" stroke="#3fb950" fill="none" opacity="0.18">
<circle r="60" stroke-width="2"/><circle r="105" stroke-width="2"/></g>
<text x="90" y="95" fill="#f4f2ea" font-size="46" font-family="Helvetica,Arial" font-weight="800">📡 RADAR DELTA</text>
<text x="90" y="140" fill="#3fb950" font-size="27" font-family="Helvetica,Arial" font-weight="700">TOP FUNDING TODAY · {dstr}</text>
<line x1="90" y1="175" x2="1110" y2="175" stroke="#232a36" stroke-width="2"/>
{''.join(linhas)}
<text x="90" y="592" fill="#e3b341" font-size="24" font-family="Helvetica,Arial" font-weight="700">{BASE.replace('https://','')}</text>
<text x="1110" y="592" fill="#8b98a9" font-size="22" font-family="Helvetica,Arial" text-anchor="end">delta-neutral · free channel</text>
</svg>"""

# ---------- sitemap + robots ----------
def sitemap(coin_urls, extra):
    urls = [TOOL, f"{BASE}/blog/", f"{BASE}/vs-binance-bybit.html"] + coin_urls + extra
    # posts do blog, se existirem
    pj = os.path.join(CWD,"blog","posts.json")
    if os.path.exists(pj):
        for p in json.load(open(pj)): urls.append(f"{BASE}/blog/{p['slug']}.html")
    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for u in dict.fromkeys(urls):
        body.append(f"<url><loc>{u}</loc><lastmod>{today}</lastmod></url>")
    body.append("</urlset>")
    open(os.path.join(CWD,"sitemap.xml"),"w").write("\n".join(body))
    open(os.path.join(CWD,"robots.txt"),"w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")

def main(dry):
    bnc, byb = coleta_maps()
    if not bnc and not byb:
        print("sem dado agora — nao gera (integridade)"); return
    dstr = datetime.now(timezone.utc).strftime("%b %d, %Y")
    if dry:
        n=sum(1 for c in COINS if c in bnc or c in byb)
        print(f"[dry-run] {n}/{len(COINS)} moedas com dado · comparativo + card + sitemap"); return
    os.makedirs(os.path.join(CWD,"coin"), exist_ok=True)
    os.makedirs(os.path.join(CWD,"cards"), exist_ok=True)
    coin_urls=[]
    for c in COINS:
        if c not in bnc and c not in byb: continue
        canon, bodyhtml = pagina_moeda(c, bnc, byb, dstr)
        open(os.path.join(CWD,"coin",f"{c}.html"),"w").write(bodyhtml)
        coin_urls.append(canon)
    canon, vs = pagina_vs(bnc, byb, dstr)
    open(os.path.join(CWD,"vs-binance-bybit.html"),"w").write(vs)
    open(os.path.join(CWD,"cards","card.svg"),"w").write(card_svg(bnc, byb, dstr))
    sitemap(coin_urls, [])
    print(f"ok: {len(coin_urls)} paginas de moeda · vs-binance-bybit.html · cards/card.svg · sitemap.xml · robots.txt")

if __name__ == "__main__":
    main("--dry-run" in sys.argv)

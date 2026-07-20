#!/usr/bin/env python3
"""
Longevity Command Center — weekly dashboard refresh.
Step 1: rebuild news_data.json (5 AI top-development cards + ~25 articles).
Step 2: refresh 11 ETF prices in finance.html and bump the "Jan 2 to <date>" refs.
Runs inside a GitHub Action; the workflow commits/pushes any changes.
Full reference: /05_Longevity/longevity_command_center_spec.md
"""
import json, os, re, datetime, sys
import yfinance as yf
from anthropic import Anthropic

TODAY = datetime.date.today()
YDAY  = TODAY - datetime.timedelta(days=1)
TICKERS = ["AGNG","ARKG","IBB","XBI","XLV","SBIO","BBH","IHI","IDNA","HTEC","THNR"]

# ---- STEP 1: NEWS -> news_data.json ----
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
prompt = f"""Search the last 7 days of anti-aging/longevity/aging-science news. Queries:
'longevity anti-aging research news today', 'aging science clinical trial results',
'longevity biotech funding news', 'rapamycin aging trial update',
'senolytic geroprotector discovery', and 'most significant longevity wellness developments this week'.
Also probe X voices @davidsinclair @PeterAttiaMD @hubaborjan @FoundMyFitness @BryanJohnson @VICELongevity @LongevityTech,
and sources longevity.technology, agingbiotech.info, fightaging.org, lifespan.io, statnews.com, endpts.com.
Return a JSON array: FIRST 4-5 AI top-development cards (source "AI Analysis", date {YDAY}, importance "high", top_development true),
THEN the ~25 most significant articles across Clinical Trials|Research|Biotech|Funding|Industry|Protocols.
Each item: title (<=130 chars), source, date YYYY-MM-DD, category, importance high|normal, description, url,
and top_development (true only on the cards). Output ONLY the JSON array (29-35 items)."""

resp = client.messages.create(
    model="claude-opus-4-8", max_tokens=8000,
    tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
    messages=[{"role": "user", "content": prompt}],
)
text = "".join(getattr(b, "text", "") for b in resp.content if getattr(b, "type", "") == "text")
news = json.loads(text[text.index("["): text.rindex("]") + 1])

# soft validation: warn but do not abort the run on minor count drift
req = {"title","source","date","category","importance","description","url"}
news = [x for x in news if req <= set(x.keys())]
n_cards = sum(1 for x in news if x.get("top_development"))
if not (20 <= len(news) <= 40):
    print(f"WARNING: unusual news count {len(news)}", file=sys.stderr)
if n_cards not in (4, 5):
    print(f"WARNING: {n_cards} top-development cards (expected 4-5)", file=sys.stderr)
json.dump(news, open("news_data.json", "w"), indent=2, ensure_ascii=False)
print(f"news: {len(news)} items ({n_cards} cards)")

# ---- STEP 2: ETF PRICES -> finance.html (spec §6.3 regex, anchored on ticker:) ----
def fmt_aum(v):
    if not v:
        return None
    return f"${v/1e9:.2f}B" if v >= 1e9 else f"${v/1e6:.1f}M"

src = open("finance.html").read()
updated = 0
for t in TICKERS:
    try:
        tk = yf.Ticker(t)
        fi = tk.fast_info
        price = round(fi["last_price"], 2)
        prev  = fi["previous_close"]
        change = round(price - prev, 2)
        pct = round(change / prev * 100, 2)
        aum = fmt_aum(tk.get_info().get("totalAssets"))
    except Exception as e:
        print(f"WARNING: quote failed for {t}: {e}; carrying forward", file=sys.stderr)
        continue
    pat = re.compile(
        r"(ticker:\s*'" + re.escape(t) + r"'[\s\S]{0,400}?price:\s*)[-\d.]+"
        r"([\s\S]{0,80}?change:\s*)[-\d.]+"
        r"([\s\S]{0,80}?changePct:\s*)[-\d.]+"
        r"([\s\S]{0,80}?aum:\s*')[^']+(')")
    repl = (lambda m: f"{m.group(1)}{price}{m.group(2)}{change}"
            f"{m.group(3)}{pct}{m.group(4)}{aum or m.group(0)}{m.group(5)}")
    src, k = pat.subn(repl, src, count=1)
    if k == 1:
        updated += 1
    else:
        print(f"WARNING: could not locate {t} block in finance.html", file=sys.stderr)

# bump the two "Jan 2 to <Month> <D>, <YYYY>" date refs (~lines 820, 1459)
src = re.sub(r"Jan 2 to [A-Z][a-z]+ \d{1,2}, \d{4}", f"Jan 2 to {TODAY:%b %-d, %Y}", src)
open("finance.html", "w").write(src)
print(f"finance: {updated}/{len(TICKERS)} ETF prices updated; date refs -> Jan 2 to {TODAY:%b %-d, %Y}")


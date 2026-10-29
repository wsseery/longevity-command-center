#!/usr/bin/env python3
"""
Longevity Command Center — weekly dashboard refresh (NO API KEY REQUIRED).

Step 1: rebuild news_data.json by scraping public RSS feeds (feedparser), then add
any hand-picked items from pinned_news.json (kept every run, outside the scrape window).
No Anthropic API key needed. NON-FATAL: never blocks the Step 2 price refresh.
Step 2: refresh the 11 ETFs in finance.html (price, fund assets, name, expense ratio, 52-week
range, top holdings, turnover, YTD return and daily closes for the charts), the watchlist stocks'
market caps, and the "Jan 2 to <date>" refs (yfinance).

Runs inside a GitHub Action; the workflow commits/pushes any changes.
Output schema per item (consumed by news.html):
title, source, date (YYYY-MM-DD), category, importance, description, url
category in: Clinical Trials | Research | Biotech | Funding | Industry | Protocols
importance in: high | normal
Full reference: /05_Longevity/longevity_command_center_spec.md
"""
import json, os, re, sys, html, datetime

TODAY = datetime.date.today()

# ----------------------------------------------------------------------------
# STEP 1: NEWS -> news_data.json (NON-FATAL — prices still update if this fails)
# ----------------------------------------------------------------------------
# RSS sources. relevance_filter=True means keep only longevity-relevant entries
# (used for broad outlets like ScienceDaily / STAT / GEN).
FEEDS = [
    ("Fight Aging!", "https://www.fightaging.org/feed/", False),
    ("Lifespan.io", "https://www.lifespan.io/feed/", False),
    ("Longevity.Technology", "https://longevity.technology/feed/", False),
    ("ScienceDaily", "https://www.sciencedaily.com/rss/health_medicine/healthy_aging.xml", True),
    ("STAT News", "https://www.statnews.com/feed/", True),
    ("GEN", "https://www.genengnews.com/feed/", True),  # biotech/clinical; endpts.com feed 403s from CI, dropped
]

RELEVANCE = ("aging", "ageing", "longevity", "senescent", "senescence", "senolytic",
             "geroprotector", "gerontolog", "rapamycin", "epigenetic", "reprogramming",
             "lifespan", "healthspan", "thymus", "mitochond", "alzheimer", "telomere",
             " nad", "autophagy", "age-related", "anti-aging", "anti-ageing", "dementia",
             "parkinson", "biological age", "aging clock", "geroscience")

MONEY_RE = re.compile(r"\$\s?[\d.]+\s*(k|m|b|million|billion)\b", re.I)

# Category detection — ordered; first match wins. (pattern, category)
CATEGORY_RULES = [
    (r"\b(raise[sd]?|raising|funding|financing|series\s+[a-e]\b|venture|valuation|"
     r"closes?\s+\$|seed round|grant awarded|invest(s|ment)?|ipo|debut\s+fund)\b", "Funding"),
    (r"\b(phase\s*(1|2|3|i{1,3})|clinical trial|trial results?|placebo|enroll|"
     r"cohort|first-in-human|fda (approv|clear|grant)|topline|readout|"
     r"interim (data|results)|open-label|randomi[sz]ed|patients?\b|dosed|dosing|efficacy)\b", "Clinical Trials"),
    (r"\b(protocol|supplement|regimen|stack|diet|dietary|fasting|caloric|calorie|"
     r"exercise|lifestyle|sleep|nutrition|time-restricted|restriction)\b", "Protocols"),
    (r"\b(acqui(re|res|red|sition)|launch(es|ed)?|partnership|merger|market|"
     r"regulat|policy|standards|conference|summit|clinic\b|industry|ceo|spin(s|-)?out)\b", "Industry"),
    (r"\b(biotech|startup|start-up|company|platform|therapeutic|pipeline|drug (candidate|develop)|"
     r"gene therapy|cell therapy|antibod|molecule|preclinical|spinout)\b", "Biotech"),
]
HIGH_KEYWORDS = ("breakthrough", "first ", "landmark", "major", "significant", "reverses",
                 "reversal", "extends lifespan", "life extension", "restore", "billion",
                 "million", "phase 3", "phase 2", "fda", "approval", "clinical trial", "raises")

MAX_PER_SOURCE = 12
TARGET_MIN, TARGET_MAX = 29, 35
MIN_KEEP = 12

ROUNDUP_RE = re.compile(r"\b(newsletter|weekly roundup|week in review|digest)\b", re.I)

# Hand-picked items, same 8 fields as news_data.json. The rebuild below replaces
# news_data.json wholesale, so an item added there by hand lasts one week; one added
# here stays until it is deleted from this file.
PINNED = "pinned_news.json"
FIELDS = ("title", "source", "date", "category", "importance", "description", "url",
          "top_development")
CATEGORIES = ("Clinical Trials", "Research", "Biotech", "Funding", "Industry", "Protocols")

def _clean(text, limit):
    text = re.sub(r"<[^>]+>", "", text or "")
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        cut = text[:limit].rsplit(" ", 1)[0].rstrip(",.;:—- ")
        text = cut + "…"
    return text

def _categorize(title, blob):
    if MONEY_RE.search(title):
        return "Funding"
    low = blob.lower()
    for pat, cat in CATEGORY_RULES:
        if re.search(pat, low):
            return cat
    return "Research"

def _importance(text, category):
    low = text.lower()
    if category in ("Funding", "Clinical Trials"):
        return "high"
    return "high" if any(k in low for k in HIGH_KEYWORDS) else "normal"

def _entry_date(e):
    for key in ("published_parsed", "updated_parsed"):
        t = e.get(key)
        if t:
            return datetime.date(t.tm_year, t.tm_mon, t.tm_mday)
    return None

def _collect(feedparser, window_days):
    cutoff = TODAY - datetime.timedelta(days=window_days)
    items, seen, seen_urls, per_source = [], set(), set(), {}
    for source, url, needs_filter in FEEDS:
        try:
            parsed = feedparser.parse(url)
        except Exception as e:  # noqa
            print(f"WARNING: feed failed {source}: {e}", file=sys.stderr)
            continue
        for e in parsed.entries:
            d = _entry_date(e)
            if not d or d < cutoff or d > TODAY:
                continue
            title = _clean(e.get("title", ""), 130)
            if not title or ROUNDUP_RE.search(title):
                continue
            summary = _clean(e.get("summary", e.get("description", "")), 280) or title
            blob = f"{title} {summary}"
            if needs_filter and not any(k in blob.lower() for k in RELEVANCE):
                continue
            key = re.sub(r"[^a-z0-9]", "", title.lower())[:60]
            if key in seen:
                continue
            if per_source.get(source, 0) >= MAX_PER_SOURCE:
                continue
            link = e.get("link", "") or ""
            if not link.startswith("http"):
                continue
            url_key = link.split("?")[0].rstrip("/")
            if url_key in seen_urls:
                continue
            cat = _categorize(title, blob)
            items.append({
                "title": title,
                "source": source,
                "date": d.isoformat(),
                "category": cat,
                "importance": _importance(blob, cat),
                "description": summary,
                "url": link,
            })
            seen.add(key)
            seen_urls.add(url_key)
            per_source[source] = per_source.get(source, 0) + 1
    items.sort(key=lambda x: x["date"], reverse=True)
    return items

def _pinned():
    if not os.path.exists(PINNED):
        return []
    try:
        data = json.load(open(PINNED, encoding="utf-8"))
    except Exception as e:  # noqa
        print(f"WARNING: {PINNED} unreadable ({e}); no pinned items this run", file=sys.stderr)
        return []
    keep = []
    for it in data if isinstance(data, list) else []:
        if (isinstance(it, dict) and set(it) == set(FIELDS)
                and it["category"] in CATEGORIES and it["importance"] in ("high", "normal")
                and str(it["url"]).startswith("http")):
            keep.append({k: it[k] for k in FIELDS})
        else:
            print(f"WARNING: skipping malformed item in {PINNED}: {str(it)[:120]}", file=sys.stderr)
    return keep

def refresh_news():
    try:
        import feedparser
    except Exception as e:  # noqa
        print(f"WARNING: feedparser not available ({e}); keeping existing news_data.json", file=sys.stderr)
        return
    items = []
    for window in (10, 14, 21, 30):
        items = _collect(feedparser, window)
        if len(items) >= TARGET_MIN:
            break
    if len(items) < MIN_KEEP:
        print("=" * 62, file=sys.stderr)
        print(f"NEWS NOT REFRESHED - only {len(items)} item(s) scraped (minimum {MIN_KEEP}).", file=sys.stderr)
        print("news_data.json left unchanged rather than replaced with a thin feed.", file=sys.stderr)
        print("The price refresh below still runs. Check the feed WARNINGs above.", file=sys.stderr)
        print("=" * 62, file=sys.stderr)
        return
    items = items[:TARGET_MAX]
    flagged = 0
    for it in items:
        it["top_development"] = bool(flagged < 5 and it["importance"] == "high")
        if it["top_development"]:
            flagged += 1
    # After the TARGET_MAX cut, so a pinned item is never the one trimmed. A pinned item
    # the feeds also returned this week is not added twice; the scraped copy stays.
    scraped = {i["url"].split("?")[0].rstrip("/") for i in items}
    pinned = [p for p in _pinned() if p["url"].split("?")[0].rstrip("/") not in scraped]
    if pinned:
        items = sorted(items + pinned, key=lambda x: x["date"], reverse=True)
        print(f"news: {len(pinned)} pinned item(s) added from {PINNED}")
    n_high = sum(1 for i in items if i["importance"] == "high")
    cats = sorted({i["category"] for i in items})
    if len(items) < TARGET_MIN:
        print(f"WARNING: only {len(items)} news items scraped (<{TARGET_MIN})", file=sys.stderr)
    json.dump(items, open("news_data.json", "w"), indent=2, ensure_ascii=False)
    print(f"news: {len(items)} items, {n_high} high; categories: {', '.join(cats)}")

try:
    refresh_news()
except Exception as e:  # noqa
    print(f"WARNING: news refresh failed ({e}); keeping existing news_data.json", file=sys.stderr)

# ----------------------------------------------------------------------------
# STEP 2: ETF DATA AND STOCK MARKET CAPS -> finance.html (yfinance, no API key)
# ----------------------------------------------------------------------------
def _js(v):
    """A Python value as the JS literal finance.html uses."""
    if v is None:
        return "null"
    if isinstance(v, str):
        return "'" + v.replace("\\", "\\\\").replace("'", "\\'") + "'"
    if isinstance(v, list):
        return "[" + ", ".join(_js(x) for x in v) + "]"
    return repr(v)

def _value_end(s, i):
    """End of the JS literal that starts at s[i]: a 'string', a [...] list or a number."""
    if s[i] == "'":
        j = i + 1
        while s[j] != "'":
            j += 2 if s[j] == "\\" else 1
        return j + 1
    if s[i] == "[":
        depth, quote, j = 0, False, i
        while True:
            c = s[j]
            if quote:
                if c == "\\":
                    j += 1
                elif c == "'":
                    quote = False
            elif c == "'":
                quote = True
            elif c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    return j + 1
            j += 1
    return i + re.match(r"-?[\d.]+", s[i:]).end()

def _set(block, key, js):
    """Set `key: <literal>` at the top level of one ETF block, adding it before url: if absent."""
    m = re.search(r"\n(\s*)" + key + r":\s*", block)
    if not m:
        u = re.search(r"\n(\s*)url:", block)
        return block[:u.start()] + f"\n{u.group(1)}{key}: {js}," + block[u.start():]
    return block[:m.end()] + js + block[_value_end(block, m.end()):]

def _etf_block(src, t):
    """(start, end) of ticker t's object in ETF_DATA, from its opening { to its closing }."""
    m = re.search(r"\{\s*\n\s*ticker:\s*'" + re.escape(t) + r"'", src)
    if not m:
        return None
    end = re.compile(r"\n\s*url:\s*'[^']*'\s*\n\s*\}").search(src, m.end())
    return (m.start(), end.end()) if end else None

def refresh_prices():
    import yfinance as yf
    TICKERS = ["AGNG", "ARKG", "IBB", "XBI", "XLV", "SBIO", "BBH", "IHI", "IDNA", "HTEC", "THNR"]

    def fmt_aum(v):
        if not v:
            return None
        return f"${v/1e9:.2f}B" if v >= 1e9 else f"${v/1e6:.1f}M"

    if not os.path.exists("finance.html"):
        print("WARNING: finance.html not found; skipping price refresh", file=sys.stderr)
        return
    src = open("finance.html").read()

    # Pass 1: fetch. Any field that fails keeps last week's value (it is simply not set).
    fetched, histories = {}, {}
    for t in TICKERS:
        try:
            tk = yf.Ticker(t)
            fi = tk.fast_info
            price = round(fi["last_price"], 2)
            prev = fi["previous_close"]
            if not (price > 0 and prev > 0):
                raise ValueError(f"no price ({price}, previous {prev})")
            change = round(price - prev, 2)
            f = {"price": price, "change": change, "changePct": round(change / prev * 100, 2)}
        except Exception as e:  # noqa
            print(f"WARNING: quote failed for {t}: {e}; carrying forward", file=sys.stderr)
            continue
        try:
            low, high = fi["year_low"], fi["year_high"]
            if low == low and high == high:  # not NaN
                f["low52"], f["high52"] = round(low, 2), round(high, 2)
            info = tk.get_info()
            if info.get("longName"):
                f["name"] = info["longName"]
            if fmt_aum(info.get("totalAssets")):
                f["aum"] = fmt_aum(info["totalAssets"])
            if info.get("netExpenseRatio") is not None:
                f["expense"] = f"{info['netExpenseRatio']:.2f}%"
        except Exception as e:  # noqa
            print(f"WARNING: fund details failed for {t}: {e}; carrying forward", file=sys.stderr)
        try:
            fd = tk.funds_data
            top = fd.top_holdings.head(5)
            if len(top):
                f["topHoldings"] = [(str(r["Name"]), f"{r['Holding Percent'] * 100:.1f}%") for _, r in top.iterrows()]
            turnover = fd.fund_operations.loc["Annual Holdings Turnover", t]
            if turnover == turnover:  # not NaN
                f["turnover"] = f"{turnover * 100:.0f}%"
        except Exception as e:  # noqa
            print(f"WARNING: holdings failed for {t}: {e}; carrying forward", file=sys.stderr)
        try:
            closes = tk.history(start=f"{TODAY.year}-01-01", auto_adjust=False)["Close"].dropna()
            if len(closes) >= 2:
                closes.index = [d.date().isoformat() for d in closes.index]
                histories[t] = closes
                f["ytd"] = f"{(closes.iloc[-1] / closes.iloc[0] - 1) * 100:+.1f}%"
        except Exception as e:  # noqa
            print(f"WARNING: price history failed for {t}: {e}; carrying forward", file=sys.stderr)
        fetched[t] = f

    if not fetched:
        # Every quote failed. Rewriting now would stamp today's date onto last
        # week's prices and commit that as a fresh update.
        print(f"::warning::finance: 0/{len(TICKERS)} ETF prices updated; "
              "finance.html left untouched and the dashboard is stale")
        return

    # One date axis for every chart: the trading days any ETF has this year. An ETF missing a
    # day (a late listing, a halt) carries its previous close; days before its first close stay null.
    dates = sorted({d for h in histories.values() for d in h.index})
    for t, h in histories.items():
        fetched[t]["closes"] = [None if v != v else round(float(v), 2) for v in h.reindex(dates).ffill()]

    # Pass 2: write.
    for t, f in fetched.items():
        span = _etf_block(src, t)
        if not span:
            print(f"WARNING: could not locate {t} block in finance.html", file=sys.stderr)
            continue
        a, b = span
        block = src[a:b]
        indent = re.search(r"\n(\s*)ticker:", block).group(1)
        for key, v in f.items():
            if key == "topHoldings":
                rows = ",\n".join(f"{indent}  {{ name: {_js(n)}, pct: {_js(p)} }}" for n, p in v)
                js = f"[\n{rows}\n{indent}]"
            else:
                js = _js(v)
            block = _set(block, key, js)
        src = src[:a] + block + src[b:]

    if dates:
        line = "  const ETF_DATES = " + _js(dates) + ";\n"
        m = re.search(r"  const ETF_DATES = \[[^\]]*\];\n", src)
        src = src[:m.start()] + line + src[m.end():] if m else src.replace("  const ETF_DATA = [", line + "\n  const ETF_DATA = [", 1)

    # Stocks: every ticker in WATCHLIST_DATA gets mcapB (market cap, $B). A ticker with no
    # quote (delisted, renamed) keeps whatever it had, and the page leaves it out of the sum.
    wl = re.search(r"const WATCHLIST_DATA = \[([\s\S]*?)\n\s*\];", src)
    stocks = re.findall(r"\{ ticker: '([^']+)'", wl.group(1)) if wl else []
    caps_updated = 0
    for t in stocks:
        try:
            info = yf.Ticker(t).get_info()
            cap = info.get("marketCap") if info.get("currency") == "USD" else None
        except Exception as e:  # noqa
            cap = None
            print(f"WARNING: market cap failed for {t}: {e}", file=sys.stderr)
        if not cap:
            print(f"WARNING: no USD market cap for {t}; carrying forward", file=sys.stderr)
            continue
        pat = re.compile(r"(\{ ticker: '" + re.escape(t) + r"'[^\n]*?)(, mcapB: [\d.]+)? \}")
        src, k = pat.subn(lambda m: f"{m.group(1)}, mcapB: {cap / 1e9:.2f} }}", src, count=1)
        caps_updated += k

    if len(fetched) < len(TICKERS):
        print(f"::warning::finance: only {len(fetched)}/{len(TICKERS)} ETF prices updated; "
              "the rest carry forward last week's figures")
    as_of = datetime.date.fromisoformat(dates[-1]) if dates else TODAY  # the last close shown, not run day
    src = re.sub(r"Jan 2 to [A-Z][a-z]+ \d{1,2}, \d{4}", f"Jan 2 to {as_of:%b %-d, %Y}", src)
    open("finance.html", "w").write(src)
    print(f"finance: {len(fetched)}/{len(TICKERS)} ETFs updated ({len(histories)} with price history, "
          f"{len(dates)} trading days); {caps_updated}/{len(stocks)} stock market caps; "
          f"date refs -> Jan 2 to {as_of:%b %-d, %Y}")

try:
    refresh_prices()
except Exception as e:  # noqa
    print(f"WARNING: price refresh failed ({e}); keeping existing finance.html", file=sys.stderr)

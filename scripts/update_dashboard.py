#!/usr/bin/env python3
"""
Longevity Command Center — weekly dashboard refresh (NO API KEY REQUIRED).

Step 1: rebuild news_data.json by scraping public RSS feeds (feedparser).
        No Anthropic API key needed. NON-FATAL: never blocks the Step 2 price refresh.
Step 2: refresh 11 ETF prices in finance.html and bump the "Jan 2 to <date>" refs (yfinance).

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
# STEP 1: NEWS -> news_data.json  (NON-FATAL — prices still update if this fails)
# ----------------------------------------------------------------------------
# RSS sources. relevance_filter=True means keep only longevity-relevant entries
# (used for broad outlets like ScienceDaily / STAT).
FEEDS = [
    ("Fight Aging!",          "https://www.fightaging.org/feed/",                                   False),
    ("Lifespan.io",           "https://www.lifespan.io/feed/",                                      False),
    ("Longevity.Technology",  "https://longevity.technology/feed/",                                 False),
    ("ScienceDaily",          "https://www.sciencedaily.com/rss/health_medicine/healthy_aging.xml", True),
    ("STAT News",             "https://www.statnews.com/feed/",                                     True),
    ("Endpoints News",        "https://endpts.com/feed/",                                           True),
]

RELEVANCE = ("aging", "ageing", "longevity", "senescent", "senescence", "senolytic",
             "geroprotector", "gerontolog", "rapamycin", "epigenetic", "reprogramming",
             "lifespan", "healthspan", "thymus", "mitochond", "alzheimer", "telomere",
             " nad", "autophagy", "age-related", "anti-aging", "anti-ageing", "dementia",
             "parkinson", "biological age", "aging clock", "geroscience")

# Money pattern is checked first and separately: a leading \b would block the "$"
# alternative (since space->"$" is not a word boundary), so keep it standalone.
MONEY_RE = re.compile(r"\$\s?[\d.]+\s*(k|m|b|million|billion)\b", re.I)

# Category detection — ordered; first match wins. (pattern, category)
CATEGORY_RULES = [
    (r"\b(raise[sd]?|raising|funding|financing|series\s+[a-e]\b|venture|valuation|"
     r"closes?\s+\$|seed round|grant awarded|invest(s|ment)?)\b", "Funding"),
    (r"\b(phase\s*(1|2|3|i{1,3})|clinical trial|trial results?|placebo|enroll|"
     r"cohort|first-in-human|fda (approv|clear)|topline|randomi[sz]ed)\b", "Clinical Trials"),
    (r"\b(protocol|supplement|regimen|stack|diet|dietary|fasting|caloric|calorie|"
     r"exercise|lifestyle|sleep|nutrition|time-restricted|restriction)\b", "Protocols"),
    (r"\b(acqui(re|res|red|sition)|launch(es|ed)?|partnership|merger|market|"
     r"regulat|policy|standards|conference|summit|clinic\b|industry|ceo|spin(s|-)?out)\b", "Industry"),
    (r"\b(biotech|startup|start-up|company|platform|therapeutic|pipeline|drug (candidate|develop)|"
     r"gene therapy|preclinical program|spinout)\b", "Biotech"),
]
HIGH_KEYWORDS = ("breakthrough", "first ", "landmark", "major", "significant", "reverses",
                 "reversal", "extends lifespan", "life extension", "restore", "billion",
                 "million", "phase 3", "phase 2", "fda", "approval", "clinical trial", "raises")

MAX_PER_SOURCE = 12
TARGET_MIN, TARGET_MAX = 29, 35


def _clean(text, limit):
    text = re.sub(r"<[^>]+>", "", text or "")          # strip HTML tags
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        cut = text[:limit].rsplit(" ", 1)[0].rstrip(",.;:—- ")
        text = cut + "…"
    return text


def _categorize(title, blob):
    # A dollar figure in the TITLE is a strong funding signal; scanning the
    # description too often mis-tags research stories that cite a grant size.
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
    items, seen, per_source = [], set(), {}
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
            if not title:
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
            per_source[source] = per_source.get(source, 0) + 1
    items.sort(key=lambda x: x["date"], reverse=True)
    return items


def refresh_news():
    try:
        import feedparser
    except Exception as e:  # noqa
        print(f"WARNING: feedparser not available ({e}); keeping existing news_data.json", file=sys.stderr)
        return
    items = []
    for window in (10, 14, 21, 30):          # widen until we have enough
        items = _collect(feedparser, window)
        if len(items) >= TARGET_MIN:
            break
    if not items:
        print("WARNING: scraped 0 news items; keeping existing news_data.json", file=sys.stderr)
        return
    items = items[:TARGET_MAX]
    # cosmetic: flag the freshest few high-importance items (news.html ignores this key,
    # but it preserves the historical schema / spec shape).
    flagged = 0
    for it in items:
        it["top_development"] = bool(flagged < 5 and it["importance"] == "high")
        if it["top_development"]:
            flagged += 1
    n_high = sum(1 for i in items if i["importance"] == "high")
    cats = sorted({i["category"] for i in items})
    if len(items) < TARGET_MIN:
        print(f"WARNING: only {len(items)} news items scraped (<{TARGET_MIN})", file=sys.stderr)
    json.dump(items, open("news_data.json", "w"), indent=2, ensure_ascii=False)
    print(f"news: {len(items)} items, {n_high} high; categories: {', '.join(cats)}")


# STEP 1 is non-fatal: any error is logged but never aborts the ETF refresh below.
try:
    refresh_news()
except Exception as e:  # noqa
    print(f"WARNING: news refresh failed ({e}); keeping existing news_data.json", file=sys.stderr)


# ----------------------------------------------------------------------------
# STEP 2: ETF PRICES -> finance.html  (unchanged; yfinance, no API key)
# ----------------------------------------------------------------------------
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
    updated = 0
    for t in TICKERS:
        try:
            tk = yf.Ticker(t)
            fi = tk.fast_info
            price = round(fi["last_price"], 2)
            prev = fi["previous_close"]
            change = round(price - prev, 2)
            pct = round(change / prev * 100, 2)
            aum = fmt_aum(tk.get_info().get("totalAssets"))
        except Exception as e:  # noqa
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
    src = re.sub(r"Jan 2 to [A-Z][a-z]+ \d{1,2}, \d{4}", f"Jan 2 to {TODAY:%b %-d, %Y}", src)
    open("finance.html", "w").write(src)
    print(f"finance: {updated}/{len(TICKERS)} ETF prices updated; date refs -> Jan 2 to {TODAY:%b %-d, %Y}")


# Non-fatal: a price/yfinance error must not abort the run (or the commit of fresh news).
try:
    refresh_prices()
except Exception as e:  # noqa
    print(f"WARNING: price refresh failed ({e}); keeping existing finance.html", file=sys.stderr)


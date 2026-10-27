"""Shared helpers for the content gate: path classification and HTML inspection.

The rules implemented here are GLOBAL_INSTRUCTIONS.md §8a (merge authority split
by what the PR changes). That file lives on G:\\My Drive\\ and cannot be read
from an Actions runner, so the lists below are a hand-kept mirror of it.
If this file and §8a ever disagree, §8a wins and this file is the bug: change
§8a first, then here.

Adapted from alphagen-website's .github/checks/sitelib.py (2026-10-26). The
differences are this site's layout: pages are flat <name>.html at the root,
posts are blog-<slug>.html, and most pages predate <main> (see split_main).

Pure standard library, so it runs on a bare runner with no install step.
"""

import html
import json
import re

# --- §8a path lists -------------------------------------------------------

# Code: any one of these makes the whole PR a code PR. Checked FIRST.
CODE_PATTERNS = [
    (r"^\.github/", "anything under .github/"),
    (r"\.(js|mjs|cjs|ts|tsx|jsx|py|rb|go|sh|bash|ps1|php|pl)$", "executable source"),
    (r"^assets/css/", "shared stylesheet"),
    (r"^assets/js/", "shared script"),
    (r"\.css$", "stylesheet"),
    (r"(^|/)(CNAME|_config[^/]*|robots\.txt|_redirects|_headers|redirects\.csv)$",
     "build, deploy or redirect configuration"),
    (r"(^|/)(netlify\.toml|wrangler\.toml|vercel\.json)$", "deploy configuration"),
    (r"(^|/)(package(-lock)?\.json|yarn\.lock|pnpm-lock\.yaml|requirements[^/]*\.txt|"
     r"Pipfile(\.lock)?|Gemfile(\.lock)?|go\.(mod|sum))$", "dependency or lockfile"),
    (r"(^|/)clients/", "client material"),
    (r"(^|/)\.(gitattributes|gitignore|env[^/]*)$", "repository configuration"),
    (r"\.svg$", "SVG (can carry script)"),
    # CLAUDE.md no-touch zones: finance.html and news_data.json are written by
    # weekly-update.yml. Every JSON file here is data a page renders.
    (r"^finance\.html$", "machine-written by weekly-update.yml (CLAUDE.md: never hand-edit)"),
    (r"\.json$", "data file"),
    (r"^(tools|scripts)/", "self-hosted tool or script (tools/ pages are generated)"),
    (r"^(site\.webmanifest|favicon\.[a-z]+|icon-\d+\.png|og-image\.png)$",
     "site-wide icon or default OG card"),
]

# Content: a page or index the site serves. Checked SECOND; a path matching
# neither list is code (fail closed).
CONTENT_IMAGE = re.compile(r"^assets/(img/)?[^/]+\.(png|jpe?g|webp|gif|avif)$", re.I)
BLOG_INDEX = "blog.html"
SITEMAP = "sitemap.xml"
BLOG_POST = re.compile(r"^blog-[a-z0-9][a-z0-9-]*\.html$")
ROOT_PAGE = re.compile(r"^[a-z0-9][a-z0-9-]*\.html$")
HOMEPAGE = "index.html"


def code_reason(path):
    for pattern, why in CODE_PATTERNS:
        if re.search(pattern, path, re.I):
            return why
    return None


def page_kind(path):
    """Which content allowlist entry a path matches, or None."""
    if path == SITEMAP:
        return "sitemap"
    if path == BLOG_INDEX:
        return "blog-index"
    if BLOG_POST.match(path):
        return "blog-post"
    if path == HOMEPAGE or ROOT_PAGE.match(path):
        return "page"
    if CONTENT_IMAGE.match(path):
        return "image"
    return None


def is_page(path):
    return page_kind(path) in ("blog-post", "page", "blog-index")


# --- HTML inspection ------------------------------------------------------

MAIN_RE = re.compile(r"<main\b[^>]*>(.*?)</main>", re.S | re.I)
BODY_RE = re.compile(r"<body\b[^>]*>(.*?)</body\s*>", re.S | re.I)
CHROME_RE = re.compile(r"<(header|nav|footer)\b.*?</\1\s*>", re.S | re.I)


def split_main(text):
    """(the page's own copy, everything else).

    The copy is <main> when the page has one. Most pages here predate <main>
    (every post among them); for those it is <body> with its <header>,
    <nav> and <footer> cut out, so <head>, navigation and footer still count
    as outside. No <body> either -> ('', text)."""
    m = MAIN_RE.search(text)
    if m:
        return m.group(1), text[: m.start()] + "<main></main>" + text[m.end():]
    b = BODY_RE.search(text)
    if not b:
        return "", text
    chrome = "".join(c.group(0) for c in CHROME_RE.finditer(b.group(1)))
    inside = CHROME_RE.sub(" ", b.group(1))
    return inside, text[: b.start()] + "<body>" + chrome + "</body>" + text[b.end():]


def footer(text):
    return " ".join(m.group(0) for m in re.finditer(r"<footer\b.*?</footer\s*>", text, re.S | re.I))


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


# Anything that executes, tracks, loads, submits, redirects or carries schema.
# §8a makes analytics, tracking, schema-block and form-embed changes code, so a
# content page may only carry these if each one is a verbatim copy of a block
# the site already serves on main.
ACTIVE_BLOCK_RES = [
    re.compile(r"<script\b[^>]*>.*?</script\s*>", re.S | re.I),
    re.compile(r"<form\b.*?</form\s*>", re.S | re.I),
    re.compile(r"<style\b[^>]*>.*?</style\s*>", re.S | re.I),
    re.compile(r"<noscript\b[^>]*>.*?</noscript\s*>", re.S | re.I),
    re.compile(r"<iframe\b.*?(?:</iframe\s*>|/>)", re.S | re.I),
    re.compile(r"<(?:object|embed|base|portal)\b[^>]*>", re.I),
    re.compile(r"<meta\b[^>]*http-equiv[^>]*>", re.I),
    re.compile(r"<link\b[^>]*\brel=[\"']?(?:stylesheet|preload|modulepreload|prefetch|"
               r"preconnect|dns-prefetch|manifest|import)[^>]*>", re.I),
    # Any tag carrying an inline event handler or a javascript: URL.
    re.compile(r"<[a-z][^>]*\s(?:on[a-z]+\s*=|href\s*=\s*[\"']?\s*javascript:)[^>]*>", re.I),
]


FAQ_JSONLD_RE = re.compile(
    r"^<script\s+type=[\"']application/ld\+json[\"']\s*>(.*)</script\s*>$", re.S | re.I)


def is_faq_jsonld(block):
    """True only for a pure FAQPage JSON-LD block (GLOBAL §8a, FAQ amendment
    2026-10-05). The shape is held tight: FAQPage -> Question(name) ->
    Answer(text), plain strings, no other keys, no URLs, no markup. Anything
    else (BlogPosting included) stays code."""
    m = FAQ_JSONLD_RE.match(block)
    if not m:
        return False
    try:
        data = json.loads(m.group(1))
    except ValueError:
        return False

    def plain(v):
        return isinstance(v, str) and v.strip() and not re.search(r"[<>]|https?:|javascript:", v, re.I)

    if not isinstance(data, dict) or set(data) != {"@context", "@type", "mainEntity"}:
        return False
    if data["@type"] != "FAQPage" or data["@context"] not in ("https://schema.org", "http://schema.org"):
        return False
    qs = data["mainEntity"]
    if not isinstance(qs, list) or not qs:
        return False
    for q in qs:
        if not isinstance(q, dict) or set(q) != {"@type", "name", "acceptedAnswer"}:
            return False
        a = q["acceptedAnswer"]
        if q["@type"] != "Question" or not plain(q["name"]):
            return False
        if not isinstance(a, dict) or set(a) != {"@type", "text"}:
            return False
        if a["@type"] != "Answer" or not plain(a["text"]):
            return False
    return True


def active_blocks(text):
    # Forms are matched whole first, then removed, so the inputs inside a
    # verbatim form are not re-checked one tag at a time.
    found = []
    for rx in ACTIVE_BLOCK_RES:
        for m in rx.finditer(text):
            found.append(norm(m.group(0)))
        if rx.pattern.startswith("<form"):
            text = rx.sub(" ", text)
    return found


QUOTES = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"'})


def visible_text(fragment):
    for tag in ("script", "style", "form", "noscript"):
        fragment = re.sub(rf"<{tag}\b.*?</{tag}\s*>", " ", fragment, flags=re.S | re.I)
    fragment = re.sub(r"<!--.*?-->", " ", fragment, flags=re.S)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return norm(html.unescape(fragment)).translate(QUOTES)


# A figure is any run of digits, with optional $, thousands commas, decimals, %.
NUMBER_RE = re.compile(r"(?<![\w.])\$?\d[\d,]*(?:\.\d+)?%?")


def numbers_in(text):
    out = []
    for tok in NUMBER_RE.findall(text):
        core = tok.replace("$", "").replace(",", "").rstrip("%").rstrip(".")
        if core:
            out.append(core)
    return out


def is_year(core):
    return re.fullmatch(r"(19[9]\d|20\d\d)", core) is not None


# --- CTAs -----------------------------------------------------------------

# A call to action is one marked element: a class token cta, *-cta or cta-*
# (the Crosscheck post's .tool-cta box), a btn / btn-* link or button, or
# data-cta. share-btn is not a CTA: the btn token must start the class name.
CTA_CLASS_RE = re.compile(r"class\s*=\s*[\"'][^\"']*(?<![\w-])(?:[\w-]+-)?cta(?:-[\w-]+)?(?![\w-])", re.I)
BTN_CLASS_RE = re.compile(r"class\s*=\s*[\"'][^\"']*(?<![\w-])btn(?:-[\w-]+)?(?![\w-])", re.I)


def ctas(main_html):
    """Calls to action in the page's copy: forms, CTA boxes, and any link
    or button marked as a button or with data-cta."""
    found = []
    for m in re.finditer(r"<form\b[^>]*>", main_html, re.I):
        found.append("form " + norm(m.group(0))[:80])
    without_forms = re.sub(r"<form\b.*?</form\s*>", " ", main_html, flags=re.S | re.I)
    for m in re.finditer(r"<([a-z][a-z0-9]*)\b([^>]*)>", without_forms, re.I):
        tag, attrs = m.group(1).lower(), m.group(2)
        if ("data-cta" in attrs or CTA_CLASS_RE.search(attrs)
                or (tag in ("a", "button") and BTN_CLASS_RE.search(attrs))):
            found.append(norm(m.group(0))[:80])
    return found


# GLOBAL §6a item 9: a page that takes money never auto-merges, whatever its
# file types, and PrecisionNutrition copy needs its own DRAFT disclaimer block.
# Either one on a changed page makes the PR code.
MONEY_RE = re.compile(r"stripe\.com|paypal\.|square\.link|squareup\.com|gumroad\.com|"
                      r"lemonsqueezy|checkout|founding deposit|precision[\s-]*nutrition", re.I)


def money_reason(text):
    m = MONEY_RE.search(text)
    return (f"takes money or markets PrecisionNutrition (`{m.group(0)}`; GLOBAL §6a item 9)"
            if m else None)


# Longevity Command Center block, verbatim from 00_Global/LEGAL_DISCLAIMERS.md
# (mirrored by hand, 2026-10-26; safety_checks.py carries the same text).
# Compared after whitespace and quote-mark normalisation.
LCC_DISCLAIMER = (
    "Longevity Command Center is educational content only. It is not medical advice, "
    "diagnosis, or treatment. Always consult your physician before starting any supplement, "
    "exercise, or health intervention. Nothing here has been evaluated by the FDA."
)

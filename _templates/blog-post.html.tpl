<!DOCTYPE html>
<!--
  Longevity Command Center blog post template (blog-<slug>.html at the repo root).

  Fill every {{PLACEHOLDER}}, delete these comments, save as blog-<slug>.html.
  Rules that keep a new post a CONTENT PR (GLOBAL §8a; checked by
  .github/checks/classify.py and content_rules.py):
  - No <style> block and no post-specific <script>. Post styles live in
    style.css under .post-page (this template's <main>). The Google tag snippet
    and the font/style.css lines below are site-wide: keep them byte-for-byte.
  - No BlogPosting or any other JSON-LD. The one exception is a pure FAQPage
    block (FAQPage -> Question(name) -> Answer(text), plain text, no links, no
    other keys), which may go just before </head>.
  - Exactly ONE call to action in <main>: the data-cta link in .post-next. No
    btn / btn-* link, no class containing "cta" (e.g. tool-cta) and no form
    anywhere else in <main>. share-btn links are not CTAs.
  - Keep the footer's LCC block verbatim (00_Global/LEGAL_DISCLAIMERS.md).
    Educational only: never claim anything treats, cures, prevents or mitigates
    a condition. Never cite either FL licence. Never mention PrecisionNutrition
    or anything that takes money (that makes it a code PR).
  - Every number in <main> must appear in the PR body's "## Sourced figures"
    table (# | Figure | Source | Link). Only years are exempt: the day in the
    post date and terms like "20-year" count, so list them too.
  - URLs are clean (no .html): canonical, og:url, card href, sitemap <loc>.
  - The nav and footer are copies of the live site's (A nav change touches
    every page, this template included.)
  The same PR may add a card to blog.html (the visible card list only, NOT its
  ItemList JSON-LD), a <url> entry to sitemap.xml and an OG image under
  assets/. These are code, so they go in a SEPARATE PR that Bill merges:
  the netlify.toml 301 from /blog-<slug>.html (until it lands, the .html form
  returns 200 with the clean canonical), the blog.html ItemList entry, and the
  news item in pinned_news.json (never news_data.json).
-->
<html lang="en">
<head>
  <!-- Google tag (gtag.js) - GA4 Longevity Command Center -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-4Z33NTJSR5"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-4Z33NTJSR5');
  </script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{TITLE}}</title>
  <meta name="description" content="{{DESCRIPTION}}">
  <link rel="canonical" href="https://longevitycommandcenter.com/blog-{{SLUG}}">
  <meta name="robots" content="index,follow">
  <meta property="og:site_name" content="Longevity Command Center">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{{OG_TITLE}}">
  <meta property="og:description" content="{{OG_DESCRIPTION}}">
  <meta property="og:url" content="https://longevitycommandcenter.com/blog-{{SLUG}}">
  <meta property="og:image" content="https://longevitycommandcenter.com/assets/og/{{SLUG}}.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{{OG_IMAGE_ALT}}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://longevitycommandcenter.com/assets/og/{{SLUG}}.png">
  <meta name="twitter:title" content="{{OG_TITLE}}">
  <meta name="twitter:description" content="{{OG_DESCRIPTION}}">
  <meta name="author" content="Bill Seery">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="./style.css">
</head>
<body>
  <nav style="position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(10,14,26,0.92);backdrop-filter:blur(12px);border-bottom:1px solid rgba(0,221,255,0.1);padding:10px 24px;display:flex;align-items:center;justify-content:space-between;font-family:'JetBrains Mono',monospace;">
    <div style="display:flex;align-items:center;gap:20px;">
      <span style="font-size:0.85rem;font-weight:700;color:#00ddff;text-shadow:0 0 12px rgba(0,221,255,0.3);letter-spacing:1px;">LONGEVITY COMMAND CENTER</span>
      <div style="display:flex;gap:4px;flex-wrap:wrap;">
        <a href="/" style="font-size:0.7rem;color:#8892a8;text-decoration:none;padding:6px 14px;background:transparent;border:1px solid rgba(0,221,255,0.08);border-radius:4px;letter-spacing:0.5px;text-transform:uppercase;" onmouseover="this.style.color='#00ddff'" onmouseout="this.style.color='#8892a8'">Home</a>
        <a href="/compounds" style="font-size:0.7rem;color:#8892a8;text-decoration:none;padding:6px 14px;background:transparent;border:1px solid rgba(0,221,255,0.08);border-radius:4px;letter-spacing:0.5px;text-transform:uppercase;" onmouseover="this.style.color='#00ddff'" onmouseout="this.style.color='#8892a8'">Compounds</a>
        <a href="/finance" style="font-size:0.7rem;color:#8892a8;text-decoration:none;padding:6px 14px;background:transparent;border:1px solid rgba(0,221,255,0.08);border-radius:4px;letter-spacing:0.5px;text-transform:uppercase;" onmouseover="this.style.color='#00ddff'" onmouseout="this.style.color='#8892a8'">Finance</a>
        <a href="/news" style="font-size:0.7rem;color:#8892a8;text-decoration:none;padding:6px 14px;background:transparent;border:1px solid rgba(0,221,255,0.08);border-radius:4px;letter-spacing:0.5px;text-transform:uppercase;" onmouseover="this.style.color='#00ddff'" onmouseout="this.style.color='#8892a8'">News</a>
        <a href="/blog" style="font-size:0.7rem;color:#e8edf5;text-decoration:none;padding:6px 14px;background:rgba(0,221,255,0.1);border:1px solid rgba(0,221,255,0.25);border-radius:4px;letter-spacing:0.5px;text-transform:uppercase;">Blog</a>
        <a href="/protocols" style="font-size:0.7rem;color:#8892a8;text-decoration:none;padding:6px 14px;background:transparent;border:1px solid rgba(0,221,255,0.08);border-radius:4px;letter-spacing:0.5px;text-transform:uppercase;" onmouseover="this.style.color='#00ddff'" onmouseout="this.style.color='#8892a8'">Protocols</a>
      </div>
    </div>
  </nav>
  <div style="height:52px;"></div>
  <main class="post-page">
  <article class="article-wrap">
    <a class="backlink" href="/blog">&larr; All posts</a>
    <div class="article-meta">
      <span class="article-tag">{{TAG}}</span>
      <span>{{DATE_LONG}}</span>
      <span>By Bill Seery</span>
    </div>
    <h1 class="article-title">{{HEADLINE}}</h1>
    <p class="article-standfirst">{{STANDFIRST}}</p>
    <div class="article-body">
      <p>{{PARAGRAPH}}</p>

      <h2>{{SECTION_HEADING}}</h2>
      <p>{{PARAGRAPH}}</p>
      <!-- Optional: <div class="callout"><strong>Lead-in.</strong> Text.</div>
           Optional table: <div class="tablewrap"><table class="scoretable">…</table></div> -->
    </div>
    <div class="post-next">
      <strong>{{CTA_HEADING}}</strong>
      {{CTA_TEXT}}<br>
      <a href="{{CTA_URL}}" data-cta>{{CTA_LABEL}}</a>
    </div>
    <div class="sources">
      <h3>Sources</h3>
      <ol>
        <li>{{AUTHORS}}. <a href="{{SOURCE_URL}}" target="_blank" rel="noopener noreferrer">&ldquo;{{SOURCE_TITLE}}.&rdquo;</a> <em>{{JOURNAL}}</em> ({{YEAR}}).</li>
      </ol>
    </div>
    <div class="share-row">
      <span>Share:</span>
      <a class="share-btn" href="https://www.linkedin.com/sharing/share-offsite/?url=https://longevitycommandcenter.com/blog-{{SLUG}}%3Futm_source%3Dlinkedin%26utm_medium%3Dsocial%26utm_campaign%3Dblog-{{SLUG}}" target="_blank" rel="noopener noreferrer">LinkedIn</a>
      <a class="share-btn" href="https://twitter.com/intent/tweet?url=https://longevitycommandcenter.com/blog-{{SLUG}}%3Futm_source%3Dx%26utm_medium%3Dsocial%26utm_campaign%3Dblog-{{SLUG}}" target="_blank" rel="noopener noreferrer">X</a>
    </div>
  </article>
  </main>
  <footer class="site-footer">
    <p class="lcc-disclaimer">Longevity Command Center is educational content only. It is not medical advice, diagnosis, or treatment. Always consult your physician before starting any supplement, exercise, or health intervention. Nothing here has been evaluated by the FDA.</p>
    <p>Editorial and educational content on longevity and aging science. For informational purposes only &mdash; not medical, health, or investment advice. Always consult a qualified professional before acting on health information.</p>
    <div class="footer-links">
      <a href="/">Home</a><span class="footer-sep">&middot;</span>
      <a href="/news">News Feed</a><span class="footer-sep">&middot;</span>
      <a href="/blog">Blog</a><span class="footer-sep">&middot;</span>
      <a href="/nutrition">Nutrition</a><span class="footer-sep">&middot;</span>
      <a href="https://longevity.technology" target="_blank" rel="noopener noreferrer">Longevity.Technology</a><span class="footer-sep">&middot;</span>
      <a href="https://lifespan.io" target="_blank" rel="noopener noreferrer">Lifespan.io</a>
    </div>
  </footer>
</body>
</html>

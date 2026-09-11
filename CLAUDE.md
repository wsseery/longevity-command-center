# CLAUDE.md — longevity-command-center

Repo-local facts only. Everything else lives in
`G:\My Drive\Claude\BillSeery\00_Global\GLOBAL_INSTRUCTIONS.md` (ventures, naming, compliance)
and `RUNBOOK_MENU.md` (procedures). **Do not copy those files here — pointers only.**

Venture `05_Longevity`. Live at **https://longevitycommandcenter.com** (Netlify, auto-deploys
on push to `main`). `longevitycommandcenter.netlify.app` is a *different site* — never touch it.

## Compliance — non-negotiable, verify before any content change

- **Educational only, never medical advice.** Nothing on this site may claim to treat, cure,
  prevent or mitigate any condition.
- **Every page carries the LCC block from `00_Global/LEGAL_DISCLAIMERS.md`** at the top of its
  `<footer>`. 10/10 pages were compliant as of 2026-08-25 — keep it that way when adding a page.
- `finance.html` and `index.html` additionally carry the *not investment advice* block, because
  they are the only two pages showing figures. Do not add it site-wide; a securities disclaimer
  on a page about senolytics is noise that makes every disclaimer easier to ignore.
- ⛔ **Never reference Bill's FL licences (insurance G164863, real estate 3333692) anywhere on
  this site.** Neither is a securities or medical licence.
- Never fabricate figures, studies or citations. Every number on the nutrition page is computed
  from `histamine_data.json`, not copied.

## No-touch zones

- **`finance.html` is machine-written** by `.github/workflows/weekly-update.yml` every Tuesday
  09:00 ET. Do not hand-edit it, and always work from a freshly pulled clone — a stale local copy
  will clobber a week of updates.
- `news_data.json` is likewise written by that workflow (public RSS via `feedparser`).
- ⚠️ **Do not add an `ANTHROPIC_API_KEY` secret.** The news path is RSS and needs no key. An
  earlier version silently skipped the news step for three weeks because that secret was assumed
  to exist. A successful run is one whose commit message reads `news refreshed (N items)` and
  which touches `news_data.json`.

## Conventions

- **LF line endings.** `.gitattributes` enforces `text=auto`; it was added 2026-08-29 after CRLF
  churn produced a 19,106-line diff that buried a real 68-line change. If every file shows as
  modified with symmetric insert/delete counts, run `git diff --ignore-all-space` — if it comes
  back empty it is line-ending churn, and the fix is to rewrite to LF, not to commit.
- **A nav change touches 9 pages plus `sitemap.xml`.** Never edit one page's nav alone.
- `og:image` must be an **absolute** URL on the custom domain, or every social card breaks
  silently.
- The Crosscheck Kitchen is self-hosted at `tools/histamine-kitchen/`. Its data is built, not
  hand-written — provenance in `tools/histamine-kitchen/build/usda/`. It was called the Histamine
  Kitchen until 2026-09-11; the rename is **display-name only** — the folder and the live URL
  `/tools/histamine-kitchen/` deliberately stay as they are, so no redirect is needed.
- `tools/histamine-kitchen/index.html` is **generated** from `build/histamine_kitchen_template.html`
  by `build/build_histamine_kitchen.py`. Any edit to the built file must be made in the template
  too, or the next build silently reverts it.

## Open work

Nothing outstanding as of 2026-09-11. Both items that used to sit here had already landed:
the netlify.app 301 is in `netlify.toml`, and the ketosis layer is complete — K data, the K
ceiling and badges in the tool, `nutrition.html` section 04, and both home cards.

One decision from that work is worth not re-litigating: the tool shows a net-carb **band, not
grams per serving**. Only 16 of 278 recipe ingredient rows carry a weight, so a per-serving
figure would have to be invented. The 55 entries marked **per 100 g** (cinnamon, bay leaf and
the like) show their real number but are excluded from the count of 52 foods that break
ketosis, because a threshold measured per 100 g describes the jar, not the spoonful.

## Working agreement

Draft, do not ship. Nothing goes public without Bill's explicit "ship it". Commits and pushes are
Bill's from GitHub Desktop or an approved Claude Code run — never through the Cowork device
bridge, which leaves a `.git/index.lock` GitHub Desktop cannot clear.

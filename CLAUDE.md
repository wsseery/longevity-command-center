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
- The Histamine Kitchen is self-hosted at `tools/histamine-kitchen/`. Its data is built, not
  hand-written — provenance in `tools/histamine-kitchen/build/usda/`.

## Open work

- `feat/netlify-app-redirect` — 301 the netlify.app host to the custom domain. Unmerged; the
  clone is currently parked on this branch.
- Histamine Kitchen ketosis layer: data (K band, `net_carbs_100g`, `k_note`) is in the working
  tree **uncommitted**. Outstanding: the tool UI (K ceiling, K badges, net carbs per serving),
  the `nutrition.html` ketosis section, and the two home cards.

## Working agreement

Draft, do not ship. Nothing goes public without Bill's explicit "ship it". Commits and pushes are
Bill's from GitHub Desktop or an approved Claude Code run — never through the Cowork device
bridge, which leaves a `.git/index.lock` GitHub Desktop cannot clear.

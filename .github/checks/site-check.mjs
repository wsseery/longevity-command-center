// playwright: loads every page a change adds or touches (plus the homepage as a
// smoke test) at desktop width and at 390px, and reports problems the change
// INTRODUCES.
//
//   node site-check.mjs <head-port> <base-port> <path> [<path> ...]
//
// Two local servers: <head-port> serves the site after the change, <base-port>
// the site before it. Every page is checked on both, and only problems found
// after but not before count as failures, so a problem already on the live
// site never fails an unrelated change. Problems already there are counted in
// the summary, not failed on.
//
// Checks: a non-200 page, a console error or uncaught exception from the
// site's own files, a broken internal link, a broken image, a broken external
// link on a changed page, an axe colour-contrast violation, horizontal
// overflow at 390px.
//
// Paths are repo paths (news.html, tools/histamine-kitchen/index.html). The
// browser resolves longevitycommandcenter.com to the local server, so pages run
// under their real hostname.

import { appendFileSync } from 'node:fs';
import { chromium } from 'playwright';
import { AxeBuilder } from '@axe-core/playwright';

const [headPort, basePort, ...paths] = process.argv.slice(2);
const base = 'http://longevitycommandcenter.com';
const toUrl = (p) => (p === 'index.html' ? '/' : p.endsWith('/index.html')
  ? '/' + p.slice(0, -'index.html'.length) : '/' + p);
const pages = [...new Set(['/', ...paths.map(toUrl)])];
const changed = new Set(paths.map(toUrl));

const VIEWPORTS = [
  { name: 'desktop', width: 1280, height: 900 },
  { name: '390px', width: 390, height: 844 },
];
// Hosts that refuse automated requests outright. A 401/403/429/999 from them
// is reported as a note, not a failure; a 404 or a dead host still fails.
// A 5xx from an external host is a note too: finance.html links to Yahoo
// Finance, which answers bots with 503, and finance.html is rewritten every
// week, so treating that as broken would alert every Tuesday.
const BOT_WALL = new Set([401, 403, 429, 999]);
const isBotWall = (status) => BOT_WALL.has(status) || (typeof status === 'number' && status >= 500);
const linkCache = new Map();

// A problem's identity, stable across unrelated edits: list positions and
// pixel counts move whenever a news item is added, so they are not part of it.
const keyOf = (text) => text
  .replace(/:nth-child\(\d+\)/g, ':nth-child(n)')
  .replace(/\d+px/g, 'Npx');

async function checkLink(request, href, external) {
  if (linkCache.has(href)) return linkCache.get(href);
  let result;
  try {
    let res = await request.head(href, { timeout: 20000, maxRedirects: 10 });
    if (res.status() >= 400) res = await request.get(href, { timeout: 20000, maxRedirects: 10 });
    result = res.status();
  } catch (e) {
    result = external ? `unreachable (${e.message.split('\n')[0]})` : 'unreachable';
  }
  linkCache.set(href, result);
  return result;
}

async function checkSite(port) {
  const problems = new Map(); // key -> text
  const notes = [];
  const add = (where, msg) => { const t = `\`${where}\`: ${msg}`; problems.set(keyOf(t), t); };
  const browser = await chromium.launch({
    args: [`--host-resolver-rules=MAP longevitycommandcenter.com 127.0.0.1:${port}, MAP www.longevitycommandcenter.com 127.0.0.1:${port}`],
  });

  for (const path of pages) {
    for (const vp of VIEWPORTS) {
      const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
      const page = await context.newPage();
      const where = `${path} @ ${vp.name}`;
      const errors = [];
      // A console error from the site's own files counts; one from a third
      // party (Google Tag Manager dropping a connection, say) is a note.
      page.on('console', (m) => {
        if (m.type() !== 'error') return;
        const src = m.location().url || '';
        if (src && !src.startsWith(base)) notes.push(`\`${where}\`: third-party console error from ${new URL(src).host}: ${m.text().slice(0, 120)}`);
        else errors.push(m.text());
      });
      page.on('pageerror', (e) => errors.push(`uncaught: ${e.message}`));

      let res;
      try {
        res = await page.goto(base + path, { waitUntil: 'load', timeout: 45000 });
      } catch (e) {
        add(where, `did not load (${e.message.split('\n')[0]})`);
        await context.close();
        continue;
      }
      if (!res || res.status() !== 200) {
        add(where, `returned ${res ? res.status() : 'no response'}`);
        await context.close();
        continue;
      }
      await page.waitForTimeout(1500);

      for (const e of errors) add(where, `console error: ${e.slice(0, 200)}`);

      const badImgs = await page.$$eval('img', (imgs) => imgs
        .filter((i) => i.complete && i.naturalWidth === 0)
        .map((i) => i.getAttribute('src')));
      for (const src of badImgs) add(where, `broken image ${src}`);

      if (vp.width === 390) {
        const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        if (over > 0) add(where, `horizontal overflow of ${over}px at 390px`);
      }

      const axe = await new AxeBuilder({ page }).withRules(['color-contrast']).analyze();
      for (const v of axe.violations) {
        for (const n of v.nodes) add(where, `contrast: ${n.target.join(' ')} — ${n.any[0]?.message ?? v.help}`);
      }

      // Links once per page (desktop pass). Internal links on every tested
      // page; external links only on pages this change touched.
      if (vp.name === 'desktop') {
        const hrefs = await page.$$eval('a[href]', (as) => as.map((a) => a.href));
        for (const href of [...new Set(hrefs)]) {
          if (!/^https?:/.test(href)) continue;
          const url = href.split('#')[0];
          const internal = /^https?:\/\/(www\.)?longevitycommandcenter\.com\//.test(url);
          if (!internal && !changed.has(path)) continue;
          const target = internal ? url.replace(/^https?:\/\/(www\.)?longevitycommandcenter\.com/, `http://127.0.0.1:${port}`) : url;
          const status = await checkLink(page.request, target, !internal);
          if (typeof status === 'number' && status < 400) continue;
          if (!internal && isBotWall(status)) {
            notes.push(`\`${path}\`: ${url} answered ${status} to an automated request — check it by hand`);
          } else {
            add(path, `broken link ${url} (${status})`);
          }
        }
      }
      await context.close();
    }
  }
  await browser.close();
  return { problems, notes };
}

const after = await checkSite(headPort);
const before = await checkSite(basePort);
const introduced = [...after.problems].filter(([k]) => !before.problems.has(k)).map(([, t]) => t);
const preexisting = [...after.problems.keys()].filter((k) => before.problems.has(k)).length;
const fixed = [...before.problems.keys()].filter((k) => !after.problems.has(k)).length;
const notes = [...new Set(after.notes)];

const lines = [`### playwright: ${introduced.length ? '**failed — this change introduced problems**' : '**passed**'}`, '',
  `Pages: ${pages.map((p) => '`' + p + '`').join(', ')} at desktop and 390px.`,
  `Problems already on the site before this change (not counted): ${preexisting}. Fixed by this change: ${fixed}.`, ''];
lines.push(...introduced.map((f) => `- ${f}`));
if (notes.length) lines.push('', '**Notes (not failures)**', ...notes.map((n) => `- ${n}`));
const text = lines.join('\n');
console.log(text);
if (process.env.GITHUB_STEP_SUMMARY) appendFileSync(process.env.GITHUB_STEP_SUMMARY, text + '\n');
process.exit(introduced.length ? 1 : 0);

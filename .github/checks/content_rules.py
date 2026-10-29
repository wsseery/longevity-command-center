"""content-rules: the third required check behind content auto-merge.

  content_rules.py <base-sha>

GLOBAL_INSTRUCTIONS.md §8a, on what this PR adds or changes:
  - every new page: exactly one call to action in its copy, and the
    Longevity Command Center block from 00_Global/LEGAL_DISCLAIMERS.md
    verbatim (the licences that must never appear are compliance-grep's job);
  - every new or changed page: no figure that is not in the PR body's
    "Sourced figures" table.

Compares the PR's checkout (HEAD) against <base-sha> and looks only at what the
PR changes, so a pre-existing line elsewhere on the site never blocks an
unrelated PR. Exits non-zero on any finding, with every finding listed.

The PR body (for the sourced-figures table) comes from $PR_BODY. Ported from
alphagen-website's content_checks.py `rules` mode; compliance-grep stays in
safety_checks.py.
"""

import os
import re
import subprocess
import sys

import sitelib as S


def run(args):
    return subprocess.run(args, check=True, capture_output=True,
                          encoding="utf-8", errors="replace").stdout


def changed(base):
    out = run(["git", "diff", "--name-status", "--no-renames", base, "HEAD"])
    rows = []
    for line in out.splitlines():
        status, path = line.split("\t", 1)
        if status[0] != "D":
            rows.append((status[0], path))
    return rows


def base_text(base, path):
    try:
        return run(["git", "show", f"{base}:{path}"])
    except subprocess.CalledProcessError:
        return None


def head_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        return None


def sourced_figures(body):
    """Figures listed in the PR body's 'Sourced figures' table."""
    lines = (body or "").splitlines()
    start = next((i for i, l in enumerate(lines)
                  if re.match(r"\s*(#+|\*\*)\s*(\d+\.\s*)?sourced figures", l, re.I)), None)
    if start is None:
        return set(), False
    table = []
    for l in lines[start + 1:]:
        if l.strip().startswith("|"):
            table.append([c.strip() for c in l.strip().strip("|").split("|")])
        elif table:
            break
    if not table:
        return set(), False
    header = [c.lower() for c in table[0]]
    # Figure AND Source: a citation's own numbers live in the Source column.
    # Link and Used-in columns stay out.
    cols = ([i for i, h in enumerate(header) if "figure" in h or "source" in h]
            or range(1, len(header)))
    figs = set()
    for row in table[2:]:  # skip header and the |---| row
        for i in cols:
            if i < len(row):
                figs.update(S.numbers_in(row[i]))
    return figs, True


def site_facts(base):
    """Numbers the site already shows in its shared footer: fair to repeat,
    not new figures. Footer only, so nothing in the nav or <head> excuses a
    number in a post."""
    home = base_text(base, "index.html") or ""
    return set(S.numbers_in(S.visible_text(S.footer(home))))


def rules(base, body):
    findings = []
    allowed, have_table = sourced_figures(body)
    facts = site_facts(base)

    for status, path in changed(base):
        kind = S.page_kind(path)
        if kind not in ("blog-post", "page", "blog-index"):
            continue
        head = head_text(path) or ""
        main = S.split_main(head)[0]
        new = status == "A"

        if new:
            found = S.ctas(main)
            if len(found) != 1:
                listed = "; ".join(found) or "none"
                findings.append(f"`{path}`: {len(found)} calls to action in the page copy, "
                                f"need exactly 1 ({listed})")
            if S.norm(S.LCC_DISCLAIMER) not in S.visible_text(head):
                findings.append(f"`{path}`: the Longevity Command Center disclaimer block "
                                "(LEGAL_DISCLAIMERS.md) is missing or not verbatim")

        # Indexes list posts by date; their numbers are not claims.
        if kind == "blog-index":
            continue
        before = set() if new else set(S.numbers_in(
            S.visible_text(S.split_main(base_text(base, path) or "")[0])))
        unsourced = sorted({n for n in S.numbers_in(S.visible_text(main))
                            if n not in before and n not in allowed
                            and n not in facts and not S.is_year(n)})
        if unsourced:
            where = ("" if have_table else
                     " (the PR body has no 'Sourced figures' table)")
            findings.append(f"`{path}`: figures not in this PR's sourced-figures table"
                            f"{where}: {', '.join(unsourced)}")
    return findings


def main():
    findings = rules(sys.argv[1], os.environ.get("PR_BODY", ""))
    lines = ["### content-rules: " + ("**failed**" if findings else "**passed**"), ""]
    lines += [f"- {f}" for f in findings] or [
        "Every new page has one CTA and the disclaimer; every new figure is sourced."]
    text = "\n".join(lines)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(text + "\n")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()

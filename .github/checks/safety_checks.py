"""compliance-grep: what a change ADDS to this public site.

  safety_checks.py <base-sha>

Compares HEAD against <base-sha> and looks only at what the change adds or
removes, so a problem already on the site never fails an unrelated change.
Exits non-zero on any finding, with every finding listed.

Rules, from this repo's CLAUDE.md and the LCC blocks in
00_Global/LEGAL_DISCLAIMERS.md (mirrored by hand, 2026-10-05):
  - Never reference Bill's FL licences (G164863, 3333692) anywhere.
  - Never mix ventures; no other venture's analytics tag.
  - Educational only: no claim that anything treats, cures, prevents or
    mitigates a condition.
  - Every page carries the LCC disclaimer block; finance.html and index.html
    also carry the not-investment-advice block.
"""

import html
import os
import re
import subprocess
import sys

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def run(args):
    return subprocess.run(args, check=True, capture_output=True,
                          encoding="utf-8", errors="replace").stdout


def resolve(base):
    """A first push (before = 000...) has no parent to compare with; compare
    against the empty tree, so everything counts as added."""
    try:
        run(["git", "rev-parse", "--verify", "--quiet", base + "^{tree}"])
        return base
    except subprocess.CalledProcessError:
        return EMPTY_TREE


def changed(base):
    out = run(["git", "diff", "--name-status", "--no-renames", base, "HEAD"])
    return [(line[0], line.split("\t", 1)[1]) for line in out.splitlines()
            if not line.startswith("D")]


def text_of(ref, path):
    try:
        if ref is None:
            with open(path, encoding="utf-8") as f:
                return f.read()
        return run(["git", "show", f"{ref}:{path}"])
    except (subprocess.CalledProcessError, FileNotFoundError, UnicodeDecodeError):
        return None


def visible(page):
    page = re.sub(r"<(script|style)\b.*?</\1\s*>", " ", page, flags=re.S | re.I)
    page = re.sub(r"<!--.*?-->", " ", page, flags=re.S)
    page = re.sub(r"<[^>]+>", " ", page)
    return re.sub(r"\s+", " ", html.unescape(page)).strip()


TEXT_EXT = re.compile(r"\.(html?|xml|txt|csv|json|md|js|css|svg|py)$", re.I)

FAIL_TERMS = {
    "G164863": "Bill's insurance licence (CLAUDE.md: never on this site)",
    "3333692": "Bill's real-estate licence (CLAUDE.md: never on this site)",
    "alphagen": "AlphaGen (never mix ventures)",
    "savingsre": "SavingsRE (never mix ventures)",
    "dialridge": "DialRidge (never mix ventures)",
    "G-RG0E11KB0Q": "AlphaGen's GA4 tag",
    "GTM-K4HVBNM": "SavingsRE's tag manager",
}

# Claim forms only. Base forms are everyday English on this site ("treat the
# L score as a hypothesis", "cured ham"), and matched nothing but false
# positives on the 2026-10-05 site; these forms state that something works.
CLAIM = re.compile(r"\b(cures?|treats|prevents|mitigates|revers(?:es|ing) (?:aging|ageing))\b", re.I)

LCC = ("Longevity Command Center is educational content only. It is not medical advice, "
       "diagnosis, or treatment. Always consult your physician before starting any supplement, "
       "exercise, or health intervention. Nothing here has been evaluated by the FDA.")
INVEST = ("The financial information on this page is provided for general informational and "
          "educational purposes only and is not investment advice.")
INVEST_PAGES = {"finance.html", "index.html"}

# Written by weekly-update.yml from third-party feeds. A headline saying a drug
# "prevents" something is the source's claim, quoted; it is noted, not failed.
MACHINE_WRITTEN = {"news_data.json", "finance.html"}

SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")


def count(rx, text):
    return len(rx.findall(text or ""))


def main():
    base = resolve(sys.argv[1])
    failures, notes = [], []
    for status, path in changed(base):
        if path.startswith(".github/") or path == "CLAUDE.md" or not TEXT_EXT.search(path):
            continue
        after = text_of(None, path)
        if after is None:
            continue
        before = text_of(base, path) or ""
        is_page = path.endswith(".html") and "/build/" not in path

        for term, why in FAIL_TERMS.items():
            rx = re.compile(re.escape(term), re.I)
            added = count(rx, after) - count(rx, before)
            if added > 0:
                failures.append(f"`{path}`: adds `{term}` ({added}x): {why}")

        if count(SSN, after) > count(SSN, before):
            failures.append(f"`{path}`: adds something shaped like an SSN (###-##-####)")

        # Claims: compare the readable text, with the disclaimer itself removed
        # (it says "not ... treatment", which is the opposite of a claim).
        read_after = (visible(after) if is_page else after).replace(LCC, "")
        read_before = (visible(before) if is_page else before).replace(LCC, "")
        words_before = [m.group(0).lower() for m in CLAIM.finditer(read_before)]
        for word in sorted({m.group(0).lower() for m in CLAIM.finditer(read_after)}):
            hits = [m for m in CLAIM.finditer(read_after) if m.group(0).lower() == word]
            added = len(hits) - words_before.count(word)
            if added <= 0:
                continue
            # Which occurrence is new is unknowable from counts; show the last.
            m = hits[-1]
            snippet = read_after[max(0, m.start() - 70): m.end() + 50].strip()
            line = f"`{path}`: adds \"{word}\" ({added}x), e.g. \"...{snippet}...\""
            if path in MACHINE_WRITTEN:
                notes.append(line + " (quoted from a news feed)")
            else:
                failures.append(line + ": reads as a medical claim (educational only: never "
                                "treats, cures, prevents or mitigates)")

        if is_page:
            had, has = LCC in visible(before), LCC in visible(after)
            if not has and (had or status == "A"):
                failures.append(f"`{path}`: the LCC disclaimer block is "
                                f"{'missing from this new page' if status == 'A' else 'removed'}")
            elif not has:
                notes.append(f"`{path}`: has no LCC disclaimer block (already missing before "
                             "this change)")
            if path in INVEST_PAGES and INVEST in visible(before) and INVEST not in visible(after):
                failures.append(f"`{path}`: the not-investment-advice block is removed")

    lines = ["### compliance-grep: " + ("**failed**" if failures else "**passed**"), ""]
    lines += [f"- {f}" for f in failures] or ["Nothing banned added, no new medical claim, "
                                             "disclaimers intact."]
    if notes:
        lines += ["", "**Notes (not failures)**"] + [f"- {n}" for n in notes]
    text = "\n".join(lines)
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(text + "\n")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

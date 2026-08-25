#!/usr/bin/env python3
# PURPOSE: Build the Histamine Kitchen single-file web app from its template + the two
#          JSON datasets. The built file is what the site serves.
# TRIGGER: Run by hand after editing data/histamine_data.json or data/recipes.json:
#              python tools/histamine-kitchen/build/build_histamine_kitchen.py
#          Then review the diff and commit. Git is the version history - there are no
#          dated copies in the repo (Drive keeps dated snapshots under /09_Wellness/).
# OUTPUT:  tools/histamine-kitchen/index.html
#          Validation runs first; a failed check aborts the build and writes nothing.

import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]   # tools/histamine-kitchen/
TEMPLATE = ROOT / "build" / "histamine_kitchen_template.html"
FOODS    = ROOT / "data" / "histamine_data.json"
RECIPES  = ROOT / "data" / "recipes.json"
OUTPUT   = ROOT / "index.html"

CATEGORIES = None   # populated from the data; set to a frozen list to enforce a fixed vocabulary
BOOLS_FOOD = ("keto", "uncertain", "liberator", "dao", "other", "l_mitigable")


def fail(msg, errs):
    errs.append(msg)


def validate(foods, recipes):
    errs = []
    names = {}
    for i, f in enumerate(foods):
        w = f"foods[{i}] {f.get('name','<no name>')!r}"
        if not f.get("name"):
            fail(f"{w}: missing name", errs); continue
        if f["name"] in names:
            fail(f"{w}: duplicate name", errs)
        names[f["name"]] = f
        for k in ("h", "l"):
            v = f.get(k)
            if not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= 3:
                fail(f"{w}: {k} must be an int 0-3, got {v!r}", errs)
        for k in BOOLS_FOOD:
            if k in f and not isinstance(f[k], bool):
                fail(f"{w}: {k} must be a boolean, got {f[k]!r}", errs)
        if f.get("l_mitigable") and not (f.get("l_prep") or "").strip():
            fail(f"{w}: l_mitigable is true but l_prep is empty", errs)
        if not f.get("category"):
            fail(f"{w}: missing category", errs)
        if not isinstance(f.get("aliases", []), list):
            fail(f"{w}: aliases must be a list", errs)

    if CATEGORIES:
        for f in foods:
            if f.get("category") not in CATEGORIES:
                fail(f"foods {f['name']!r}: category {f.get('category')!r} not on the allowed list", errs)

    ids = set()
    for i, r in enumerate(recipes):
        w = f"recipes[{i}] {r.get('name','<no name>')!r}"
        rid = r.get("id")
        if not rid:
            fail(f"{w}: missing id", errs)
        elif rid in ids:
            fail(f"{w}: duplicate id {rid!r}", errs)
        ids.add(rid)
        meals = r.get("meal")
        if not isinstance(meals, list) or not meals:
            fail(f"{w}: meal must be a non-empty list of slots", errs)
        for ing in r.get("ingredients", []):
            item = ing.get("item")
            if item not in names:
                fail(f"{w}: ingredient {item!r} does not resolve to a food name", errs)
            elif ing.get("lprep") and not names[item].get("l_mitigable"):
                fail(f"{w}: ingredient {item!r} has lprep:true but the food is not l_mitigable", errs)
    return errs, names


def eff_l(food, lprep):
    return max(0, food["l"] - 2) if (lprep and food.get("l_mitigable")) else food["l"]


def coverage(foods, recipes, names):
    """Runbook step 3 — every (H ceiling x L ceiling x keto) combo needs ~3 recipes per meal slot."""
    rows = []
    slots = sorted({m for r in recipes for m in r["meal"]})
    for hc in (0, 1):
        for lc in (0, 1, 2):
            for keto in (True, False):
                for slot in slots:
                    n = 0
                    for r in recipes:
                        if slot not in r["meal"]:
                            continue
                        if keto and not r.get("keto"):
                            continue
                        H = max((names[i["item"]]["h"] for i in r["ingredients"]), default=0)
                        L = max((eff_l(names[i["item"]], i.get("lprep")) for i in r["ingredients"]), default=0)
                        if H <= hc and L <= lc:
                            n += 1
                    if n < 3:
                        rows.append((hc, lc, keto, slot, n))
    return rows


def main():
    ap = argparse.ArgumentParser(description="Build tools/histamine-kitchen/index.html")
    ap.add_argument("--out", default=None, help="override the output path")
    ap.add_argument("--skip-coverage", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="validate and report only; write nothing")
    a = ap.parse_args()

    foods = json.loads(FOODS.read_text(encoding="utf-8"))
    recipes = json.loads(RECIPES.read_text(encoding="utf-8"))
    print(f"loaded {len(foods)} foods, {len(recipes)} recipes")

    errs, names = validate(foods, recipes)
    if errs:
        print(f"\nVALIDATION FAILED — {len(errs)} problem(s):", file=sys.stderr)
        for e in errs[:50]:
            print("  -", e, file=sys.stderr)
        sys.exit(1)
    print("validation passed")

    if not a.skip_coverage:
        thin = coverage(foods, recipes, names)
        if thin:
            print(f"coverage warning — {len(thin)} thin slot combination(s) (<3 recipes):")
            for hc, lc, keto, slot, n in thin[:20]:
                print(f"  H<={hc} L<={lc} keto={keto} {slot}: {n}")
        else:
            print("coverage passed — every combination has >=3 recipes per slot")

    tpl = TEMPLATE.read_text(encoding="utf-8")
    dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = tpl.replace("__FOODS__", dump(foods)).replace("__RECIPES__", dump(recipes))
    if "__FOODS__" in html or "__RECIPES__" in html:
        sys.exit("placeholder still present after substitution")

    if a.check:
        print("check only - nothing written")
        return

    out = pathlib.Path(a.out) if a.out else OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT.parents[1]) if out.is_relative_to(ROOT.parents[1]) else out}  ({len(html):,} bytes)")


if __name__ == "__main__":
    main()

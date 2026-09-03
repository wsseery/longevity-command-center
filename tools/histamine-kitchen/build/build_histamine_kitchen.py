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
BOOLS_FOOD = ("keto", "uncertain", "liberator", "dao", "other", "l_mitigable", "k_trace")

# The ketosis layer, added 2026-09-02. `k` is a 0-3 band derived from net carbs per 100 g:
#   0 = under 3 g   1 = 3-8 g   2 = 8-20 g   3 = over 20 g
# `net_carbs_100g` is the number the band came from - carbohydrate by difference, less fibre,
# less sugar alcohols, sourced from USDA FoodData Central SR Legacy. `k_note` states which
# USDA row was used, or on what basis the value was derived where USDA has no entry.
# Four entries are deliberately k = null: they are preparation states or categories
# ("Leftovers", "Restaurant / canteen meals", "Smoked products", "Canned or semi-finished
# products"), not foods, so no carb figure describes them.


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
        # --- ketosis layer ---
        if "k" not in f:
            fail(f"{w}: missing k (ketosis band)", errs)
        elif f["k"] is not None:
            v = f["k"]
            if not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= 3:
                fail(f"{w}: k must be an int 0-3 or null, got {v!r}", errs)
        net_ok = True
        if "net_carbs_100g" not in f:
            fail(f"{w}: missing net_carbs_100g", errs); net_ok = False
        elif f["net_carbs_100g"] is not None:
            v = f["net_carbs_100g"]
            if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
                fail(f"{w}: net_carbs_100g must be a non-negative number or null, got {v!r}", errs)
                net_ok = False
        if "k_trace" not in f:
            fail(f"{w}: missing k_trace", errs)
        if not isinstance(f.get("k_note", ""), str):
            fail(f"{w}: k_note must be a string", errs)
        elif f.get("k") is not None and not (f.get("k_note") or "").strip():
            fail(f"{w}: has a k value but no k_note - every figure must state its source", errs)
        # k and net_carbs_100g must agree; a hand edit to one without the other is a real bug
        if net_ok and f.get("k") is not None and f.get("net_carbs_100g") is not None:
            n = f["net_carbs_100g"]
            band = 0 if n < 3 else 1 if n < 8 else 2 if n <= 20 else 3
            if band != f["k"]:
                fail(f"{w}: k={f['k']} does not match net_carbs_100g={n} (expected k={band})", errs)
        # the keto boolean is now DERIVED: keto == (k <= 1). Kept for backward compatibility.
        if f.get("k") is not None and "keto" in f and f["keto"] != (f["k"] <= 1):
            fail(f"{w}: keto={f['keto']} disagrees with k={f['k']} (keto must equal k <= 1)", errs)

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


def rec_k(r, names):
    """Highest net-carb band among ingredients eaten in quantity. Trace foods (spices, condiments)
    are excluded - they are scored per 100 g, and a pinch of cinnamon is not what makes a dish
    high-carb. This mirrors recK() in the template exactly; if one changes, change both."""
    vals = [names[i["item"]]["k"] for i in r["ingredients"]
            if names[i["item"]]["k"] is not None and not names[i["item"]].get("k_trace")]
    return max(vals) if vals else 0


def coverage(foods, recipes, names):
    """Every (H x L x K ceiling x keto) combo needs recipes per meal slot.

    The K axis was added 2026-09-03. Two thresholds are checked separately, because they mean
    different things: the DEFAULT settings a normal user lands on must be comfortably filled,
    while the STRICTEST corner only has to be usable at all."""
    rows = []
    slots = sorted({m for r in recipes for m in r["meal"]})

    def count(hc, lc, kc, keto, slot):
        n = 0
        for r in recipes:
            if slot not in r["meal"]:
                continue
            if keto and not r.get("keto"):
                continue
            H = max((names[i["item"]]["h"] for i in r["ingredients"]), default=0)
            L = max((eff_l(names[i["item"]], i.get("lprep")) for i in r["ingredients"]), default=0)
            if H <= hc and L <= lc and rec_k(r, names) <= kc:
                n += 1
        return n

    for hc in (0, 1):
        for lc in (0, 1, 2):
            for kc in (0, 1, 2):
                for keto in (True, False):
                    for slot in slots:
                        n = count(hc, lc, kc, keto, slot)
                        if n < 3:
                            rows.append((hc, lc, kc, keto, slot, n))
    return rows


def headline_coverage(recipes, names):
    """The two thresholds that actually matter, reported in full whether they pass or fail."""
    slots = sorted({m for r in recipes for m in r["meal"]})

    def count(hc, lc, kc, slot):
        n = 0
        for r in recipes:
            if slot not in r["meal"] or not r.get("keto"):
                continue
            H = max((names[i["item"]]["h"] for i in r["ingredients"]), default=0)
            L = max((eff_l(names[i["item"]], i.get("lprep")) for i in r["ingredients"]), default=0)
            if H <= hc and L <= lc and rec_k(r, names) <= kc:
                n += 1
        return n

    out = []
    for label, (hc, lc, kc), need in (("DEFAULT   H<=1 L<=1 K<=1 keto", (1, 1, 1), 5),
                                      ("STRICTEST H0   L0   K0   keto", (0, 0, 0), 2)):
        counts = {s: count(hc, lc, kc, s) for s in slots}
        out.append((label, need, counts, all(v >= need for v in counts.values())))
    return out


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
        print("\ncoverage — the two thresholds that matter:")
        for label, need, counts, ok in headline_coverage(recipes, names):
            marks = "  ".join(f"{s}:{n}{'' if n >= need else ' SHORT'}" for s, n in counts.items())
            print(f"  {label}  need >={need}/slot  {'PASS' if ok else 'FAIL'}")
            print(f"    {marks}")
        thin = coverage(foods, recipes, names)
        if thin:
            print(f"\ncoverage warning — {len(thin)} thin combination(s) across the full H x L x K grid (<3 recipes)")
            for hc, lc, kc, keto, slot, n in thin[:12]:
                print(f"  H<={hc} L<={lc} K<={kc} keto={keto} {slot}: {n}")
            if len(thin) > 12:
                print(f"  ... and {len(thin)-12} more")
        else:
            print("\nfull grid passed — every combination has >=3 recipes per slot")

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

# Histamine Kitchen

A dual-scale food reference. Every food carries two **independent** 0–3 scores:
**H** (histamine, from the SIGHI Food Compatibility List) and **L** (lectin, from Plant
Paradox lists cross-checked against measured lectin-content literature). 440 foods, 46 recipes.

Served at `/tools/histamine-kitchen/`, linked from `nutrition.html`.
Self-contained single file — no build step at request time, no network except web fonts.

## Layout

```
tools/histamine-kitchen/
  index.html                         ← the built app. Do NOT hand-edit; it is generated.
  data/histamine_data.json           ← 440 foods. Source of truth.
  data/recipes.json                  ← 46 recipes. Source of truth.
  build/histamine_kitchen_template.html   ← the app shell, with __FOODS__ / __RECIPES__ placeholders
  build/build_histamine_kitchen.py        ← validates, then injects the data into the template
```

## Changing the data

```bash
# 1. edit data/histamine_data.json or data/recipes.json
# 2. validate without writing anything
python tools/histamine-kitchen/build/build_histamine_kitchen.py --check
# 3. rebuild index.html
python tools/histamine-kitchen/build/build_histamine_kitchen.py
# 4. review the diff and commit
```

The build **aborts** rather than producing a broken app if: a recipe ingredient does not
resolve to a food `name`; `h` or `l` is not an integer 0–3; a flag is not a boolean;
`l_prep` is empty where `l_mitigable` is true; a food name or recipe id is duplicated; or a
food has no category. It also warns (without aborting) when any
H-ceiling × L-ceiling × keto combination has fewer than three recipes in a meal slot, which
is the condition that makes the menu generator repeat itself.

Verified 2026-08-24: building from this data reproduces the shipped v02 byte for byte.

## Data schema

```
name, aliases[], category, keto, uncertain,
h (0-3), liberator, dao, other, note,      ← histamine layer
l (0-3), l_mitigable, l_prep, l_note       ← lectin layer
```

Recipes: every `ingredients[].item` must match a food `name` exactly. An ingredient may
carry `"lprep": true`, meaning the recipe already specifies the lectin-reducing preparation;
the engine then scores it at `max(0, l - 2)`, but only where the food is `l_mitigable`.
Recipe H = max `h` across ingredients. Recipe L = max **effective** `l`.
`meal` is a **list** of slots, not a string.

## Rules that are not negotiable

- **Never flatten H and L into one number.** Different mechanisms, and 143 of the 440 foods
  disagree — 45 histamine-clear but lectin-heavy, 98 histamine-flagged but lectin-clean.
- **The two scales are not equally well evidenced.** SIGHI is a long-standing clinical
  reference; the lectin literature is thinner and contested. Every surface that shows L says
  so — the app footer, `nutrition.html`, and the runbook.
- **Never describe a food as "safe."** Give both scores and the mechanism.
- Educational only. Not medical advice, diagnosis, or treatment.

## Provenance

Authoring notes, the runbook and dated snapshots of each shipped build live outside this repo
in `/BillSeery/09_Wellness/` on Drive. The data files **here** are the source of truth — the
copies there are archived snapshots and should not be edited.

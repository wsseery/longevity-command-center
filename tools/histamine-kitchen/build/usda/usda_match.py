#!/usr/bin/env python3
# PURPOSE: Match Histamine Kitchen food names to USDA SR Legacy rows and compute net carbs
#          per 100 g (carbohydrate by difference - fibre - sugar alcohols).
# TRIGGER: python match2.py   -> usda_mapping.csv / .json for human review.
# OUTPUT:  One reviewable row per food. Nothing enters the dataset from here directly.
#
# KEY RULE: a USDA description reads "HeadNoun, qualifier, qualifier". Matching on whole-string
# token overlap put "Butter (sweet cream)" on "Nuts, almond butter" and "Honey" on "Nuts, almonds,
# honey roasted". So a candidate only qualifies if the QUERY intersects the head segment - the
# text before the first comma. That single constraint removes the whole class of error.
import csv, json, re, collections

D = '/home/claude/usda/FoodData_Central_sr_legacy_food_csv_2018-04/'
KEEP = {'1005':'carb', '1079':'fiber', '1086':'sugalc'}

desc = {r['fdc_id']: r['description'] for r in csv.DictReader(open(D+'food.csv'))}
vals = collections.defaultdict(dict)
for r in csv.DictReader(open(D+'food_nutrient.csv')):
    k = KEEP.get(r['nutrient_id'])
    if k:
        try: vals[r['fdc_id']][k] = float(r['amount'])
        except ValueError: pass

STOP = {'raw','fresh','all','commercial','varieties','types','and','or','with','without',
        'the','of','general','mixed','species','included','includes','style','added','a'}
SING = lambda t: t[:-3]+'y' if t.endswith('ies') else (t[:-1] if len(t) > 3 and t.endswith('s') and not t.endswith('ss') else t)
def norm(s):
    s = s.lower().replace('&', ' and ')
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()
def toks(s):
    return {SING(t) for t in norm(s).split()} - STOP

BAD = ['dehydrated','powder','juice','canned','concentrate','sauce','baby food','infant',
       'fast food','restaurant','school','usda commodity','puree','sweetened','candied',
       'pickled','breaded','freeze dried','flour','syrup','extract','paste','soup','salad',
       'sandwich','pizza','mcdonald','burger king','wendy','taco bell','kfc','subway',
       'reduced fat','low fat','fat free','light','diet','enriched','fortified','instant',
       'prepared','mix','filling','topping','spread','beverage','drink','supplement',
       'formula','dessert','snack','bar','cereal','cracker','dried','honey roasted',
       'roasted','salted','oil','frozen','smoked','cured','fried','battered','glazed']
GOOD = ['raw', 'whole', 'plain', 'regular']

rows = []
for fid, d in desc.items():
    v = vals.get(fid, {})
    if 'carb' not in v: continue
    net = v['carb'] - v.get('fiber', 0.0) - v.get('sugalc', 0.0)
    n = norm(d)
    head = n.split(',')[0].strip() if ',' in d else n
    rows.append({'fdc': fid, 'desc': d, 'norm': n,
                 'head': head, 'headtok': {SING(t) for t in head.split()} - STOP,
                 'toks': toks(d),
                 'carb': v['carb'], 'fiber': v.get('fiber'), 'sugalc': v.get('sugalc'),
                 'net': round(max(net, 0.0), 2)})

inv = collections.defaultdict(list)
for i, r in enumerate(rows):
    for t in r['headtok']: inv[t].append(i)      # index on the HEAD segment only

def rank(qt, qtext, r):
    # hard gate: the query must touch the head noun
    hit = qt & r['headtok']
    if not hit: return None
    s = 3.0 * len(hit) / len(r['headtok'])          # how much of the head we explain
    s += 1.5 * len(qt & r['toks']) / len(qt)        # how much of the query is covered
    s -= 0.05 * max(0, len(r['toks']) - len(qt))    # prefer concise
    d = r['norm']
    for b in BAD:
        if b in d and b not in qtext: s -= 1.6
    for g in GOOD:
        if g in d and g not in qtext: s += 0.45
    if r['head'] == qtext: s += 2.0                 # exact head match
    return s

def best(names):
    out = None
    for nm in names:
        qtext, qt = norm(nm), toks(nm)
        if not qt: continue
        seen = set()
        for t in qt: seen.update(inv.get(t, ()))
        for i in seen:
            sc = rank(qt, qtext, rows[i])
            if sc is not None and (out is None or sc > out[0]):
                out = (sc, rows[i], nm)
    return out

FOODS = json.load(open('/mnt/user-data/uploads/Dev/longevity-command-center/tools/histamine-kitchen/data/histamine_data.json'))
res = []
for f in FOODS:
    b = best([f['name']] + list(f.get('aliases') or []))
    if b is None:
        res.append({'name': f['name'], 'category': f['category'], 'band': 'NO-MATCH',
                    'score': None, 'usda': None, 'fdc': None, 'net': None,
                    'carb': None, 'fiber': None, 'sugalc': None, 'via': None})
        continue
    sc, r, via = b
    band = 'high' if sc >= 4.4 else 'medium' if sc >= 3.4 else 'low'
    res.append({'name': f['name'], 'category': f['category'], 'band': band, 'score': round(sc,2),
                'usda': r['desc'], 'fdc': r['fdc'], 'net': r['net'],
                'carb': r['carb'], 'fiber': r['fiber'], 'sugalc': r['sugalc'], 'via': via})

json.dump(res, open('usda_mapping.json','w'), indent=1)
with open('usda_mapping.csv','w',newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=['name','category','band','score','net','usda','fdc','carb','fiber','sugalc','via'])
    w.writeheader()
    for r in res: w.writerow({k: r.get(k) for k in w.fieldnames})
print('bands:', dict(collections.Counter(r['band'] for r in res)), 'of', len(res))

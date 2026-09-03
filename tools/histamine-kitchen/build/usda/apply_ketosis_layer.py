#!/usr/bin/env python3
# PURPOSE: Build the final name -> net-carb mapping (auto match + hand overrides), assign the
#          K scale, and write the ketosis layer into histamine_data.json.
# TRIGGER: python apply_k.py            -> report only, writes nothing
#          python apply_k.py --write    -> writes histamine_data.k.json
# OUTPUT:  k (0-3), net_carbs_100g (number), k_note (string) on every food.
#          The `keto` boolean is REDEFINED as k <= 1; every disagreement with the old hand flag
#          is reported, never silently overwritten.
import csv, json, collections, argparse, sys

D='/home/claude/usda/FoodData_Central_sr_legacy_food_csv_2018-04/'
KEEP={'1005':'carb','1079':'fiber','1086':'sugalc'}
desc={r['fdc_id']:r['description'] for r in csv.DictReader(open(D+'food.csv'))}
vals=collections.defaultdict(dict)
for r in csv.DictReader(open(D+'food_nutrient.csv')):
    k=KEEP.get(r['nutrient_id'])
    if k:
        try: vals[r['fdc_id']][k]=float(r['amount'])
        except ValueError: pass
def netof(fid):
    v=vals.get(fid,{})
    if 'carb' not in v: return None
    return round(max(v['carb']-v.get('fiber',0.0)-v.get('sugalc',0.0),0.0),2)

ns={}; exec(open('overrides.py').read(), ns)
OV=ns['OVERRIDES']; ACCEPT=ns['ACCEPT_AUTO']; MISLEAD=ns['PER_100G_MISLEADING']
AUTO={r['name']: r for r in json.load(open('usda_mapping.json'))}
FOODS=json.load(open('/mnt/user-data/uploads/Dev/longevity-command-center/tools/histamine-kitchen/data/histamine_data.json'))

def kband(n):
    if n is None: return None
    if n < 3:  return 0
    if n < 8:  return 1
    if n <= 20: return 2
    return 3
KTXT={0:"under 3 g net carbs per 100 g",1:"3-8 g net carbs per 100 g",
      2:"8-20 g net carbs per 100 g",3:"over 20 g net carbs per 100 g"}

out=[]; unresolved=[]; disagree=[]; srccount=collections.Counter()
for f in FOODS:
    nm=f['name']; ov=OV.get(nm)
    net=None; note=''
    if ov and 'fdc' in ov:
        fid=ov['fdc']; net=netof(fid)
        note=f"USDA FoodData Central SR Legacy: {desc[fid]} ({KTXT[kband(net)]})."
        srccount['usda-pinned']+=1
    elif ov and 'net' in ov:
        net=ov['net']
        note=(f"No direct USDA entry. {ov['src']}." if net is not None else f"{ov['src']}.")
        srccount['derived']+=1
    else:
        a=AUTO.get(nm)
        if a and a['net'] is not None and (a['band'] in ('high','medium') or nm in ACCEPT):
            net=a['net']; note=f"USDA FoodData Central SR Legacy: {a['usda']} ({KTXT[kband(net)]})."
            srccount['usda-auto']+=1
        else:
            unresolved.append((nm,f['category'],a['band'] if a else 'none',a['usda'] if a else None))
            srccount['UNRESOLVED']+=1
    if nm in MISLEAD and note:
        note += (" Per 100 g, which is the jar rather than the meal - a normal pinch or"
                 " spoonful contributes a fraction of a gram of net carbs.")
    g=dict(f)
    g['k']=kband(net) if net is not None else None
    g['net_carbs_100g']=net
    g['k_note']=note
    if net is not None:
        newketo = g['k']<=1
        if bool(f.get('keto')) != newketo:
            disagree.append((nm,f['category'],f.get('keto'),newketo,net,g['k']))
        g['keto']=newketo
    out.append(g)

print("=== SOURCES ==="); [print(f"  {k:14s} {v}") for k,v in srccount.most_common()]
print(f"\n=== K DISTRIBUTION ===")
kc=collections.Counter(g['k'] for g in out)
for k in [0,1,2,3,None]:
    if kc.get(k): print(f"  K{k if k is not None else '-'}: {kc[k]:4d}   {KTXT.get(k,'no value')}")
print(f"\n=== keto BOOLEAN DISAGREEMENTS: {len(disagree)} ===")
for nm,cat,old,new,net,k in sorted(disagree,key=lambda x:-x[4])[:200]:
    print(f"  {nm[:32]:34s}|{cat[:13]:14s}| old keto={str(old):5s} -> new={str(new):5s} | net={net:7.2f} K{k}")
print(f"\n=== UNRESOLVED: {len(unresolved)} ===")
for u in unresolved: print("   ",u)
if '--write' in sys.argv:
    json.dump(out, open('histamine_data.k.json','w'), ensure_ascii=False, indent=1)
    json.dump({'disagree':disagree,'unresolved':unresolved}, open('k_report.json','w'), indent=1)
    print("\nWROTE histamine_data.k.json")

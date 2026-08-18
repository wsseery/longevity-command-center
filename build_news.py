import json

FA = "https://www.fightaging.org/archives/2026/08/"
LI = "https://lifespan.io/news/"
LT = "https://longevity.technology/unlocked/longevity-technology-unlocked-news-roundup-week-33-2026/"

items = []

# ---- 5 AI Analysis top-development cards (date = yesterday, 2026-08-17) ----
cards = [
 ("Aging-clock field pushes toward reliable biological-age measurement as brain-specific clocks emerge",
  "Research",
  "Multiple reviews this week map progress toward trustworthy biological-age measurement, including brain-specific aging clocks and a broader push for reliability and accuracy. Measurement quality directly gates rejuvenation trials that use clocks as endpoints."),
 ("Senescent-cell targeting matures: senolytics move into chronic lung disease as senomorphic pipeline advances",
  "Biotech",
  "Work targeting senescent cells to treat age-related chronic pulmonary disease, alongside continued senomorphic development, signals a maturing anti-senescence toolkit that goes beyond simple senolytic clearance."),
 ("Anti-inflammatory approach to Alzheimer's advances as PD-L1 antibody therapy posts trial results",
  "Clinical Trials",
  "Trial results for a PD-L1 antibody therapy aimed at reducing neuroinflammation add to evidence that dampening chronic inflammation is a viable lever against Alzheimer's progression."),
 ("Longevity medicine professionalizes: clinic standards MOU, supplement-integrity enforcement, and a new consumer platform",
  "Industry",
  "A clinic-standards MOU between Longevity Clinics World and the Healthy Longevity Medicine Society, a $5.3M ingredient-integrity judgment won by Timeline, and David Sinclair's new Lifespan consumer platform together mark a field moving toward standards and accountability."),
 ("Immune and mitochondrial rejuvenation advance as delivery methods and telomere-response targets improve",
  "Biotech",
  "Improved mitochondrial delivery via PEG lipids and cell-penetrating peptides, plus interference in the short-telomere response to restore immune function in old mice, point to tractable routes for reversing immune and mitochondrial aging."),
]
for title, cat, desc in cards:
    items.append({
        "title": title, "source": "AI Analysis", "date": "2026-08-17",
        "category": cat, "importance": "high", "description": desc,
        "url": LI if cat in ("Industry","Clinical Trials") else FA, "top_development": True
    })

# ---- ~26 articles ----
A = [
 # Research (Fight Aging, week Aug 10-14)
 ("Interfering in the short-telomere response improves immune system function in old mice","Fight Aging!","2026-08-10","Research","high",
  "Blocking the cellular response to short telomeres restored aspects of immune function in aged mice, suggesting a route to counter immune aging without directly lengthening telomeres.",
  FA+"interfering-in-the-response-to-short-telomeres-improves-immune-system-function-in-old-mice/"),
 ("Summarizing the state of hyperfunction theories of aging","Fight Aging!","2026-08-10","Research","normal",
  "A review of hyperfunction models, which frame aging as the continued, inappropriate running of developmental growth programs rather than as accumulated molecular damage.",
  FA+"summarizing-the-state-of-hyperfunction-theories-of-aging/"),
 ("Is it reasonable to say that obesity accelerates aging?","Fight Aging!","2026-08-11","Research","normal",
  "An examination of the evidence that excess visceral fat drives chronic inflammation and metabolic dysfunction, plausibly accelerating several mechanisms of aging.",
  FA+"is-it-reasonable-to-say-that-obesity-accelerates-aging/"),
 ("Why do myasthenia gravis patients live five years longer than the general population?","Fight Aging!","2026-08-11","Research","normal",
  "Data showing a longevity advantage in myasthenia gravis patients prompts hypotheses about immune modulation and treatment effects that may bear on aging.",
  FA+"why-do-myesthenia-gravis-patients-live-five-years-longer-than-the-general-population/"),
 ("Altered bile acid metabolism is related to gut microbiome aging","Fight Aging!","2026-08-11","Research","normal",
  "Age-related shifts in gut bacterial populations change bile acid metabolism, a signaling axis that influences metabolism and inflammation throughout the body.",
  FA+"altered-bile-acid-metabolism-is-related-to-gut-microbiome-aging/"),
 ("A review of approaches to rejuvenate aging hematopoietic stem cells","Fight Aging!","2026-08-12","Research","normal",
  "Hematopoietic stem cell aging skews blood and immune cell production; a review surveys strategies aimed at restoring youthful function to this stem cell population.",
  FA+"a-review-of-approaches-to-rejuvenate-aging-hematopoietic-stem-cells/"),
 ("PEG lipids and cell-penetrating peptides improve delivery and uptake of mitochondria","Fight Aging!","2026-08-12","Research","high",
  "Combining PEG lipids with cell-penetrating peptides improved the delivery and cellular uptake of transplanted mitochondria, a step toward practical mitochondrial replacement therapies.",
  FA+"peg-lipids-and-cell-penetrating-peptides-improve-delivery-and-uptake-of-mitochondria/"),
 ("Towards reliability and accuracy in the measurement of biological age","Fight Aging!","2026-08-13","Research","high",
  "A discussion of why current biological age measures remain noisy and what is needed to make them reliable enough to serve as endpoints in rejuvenation trials.",
  FA+"towards-reliability-and-accuracy-in-the-measurement-of-biological-age/"),
 ("Iron metabolism and ferroptosis in atherosclerosis","Fight Aging!","2026-08-13","Research","normal",
  "A review of how dysregulated iron handling and ferroptosis, an iron-dependent form of cell death, contribute to the progression of atherosclerotic cardiovascular disease.",
  FA+"iron-metabolism-and-ferroptosis-in-atherosclerosis/"),
 ("Reviewing the state of aging clocks for the brain","Fight Aging!","2026-08-13","Research","normal",
  "An overview of brain-specific aging clocks and the challenges of measuring biological age in neural tissue relative to blood-based epigenetic clocks.",
  FA+"reviewing-the-state-of-aging-clocks-for-the-brain/"),
 ("How tauopathy promotes mitochondrial dysfunction, and prospects for sabotaging that mechanism","Fight Aging!","2026-08-14","Research","normal",
  "Research links tau pathology to impaired mitochondrial function in neurons and explores interventions that might interrupt this damaging feedback loop.",
  FA+"how-tauopathy-promotes-mitochondrial-dysfunction-and-prospects-for-sabotaging-that-mechanism/"),
 ("Thymus hormone thymulin shows potential to reduce inflammation in an age-dependent manner","Lifespan.io","2026-08-12","Research","normal",
  "A study identified the thymus-derived hormone thymulin as a molecule that can suppress inflammatory signaling, with effects that vary with age.",
  LI),
 ("Researchers explain how protein AGGF1 exerts significant effects on blood pressure","Lifespan.io","2026-08-10","Research","normal",
  "Findings published in Aging Cell clarify the mechanism by which the protein AGGF1 influences blood pressure regulation, relevant to vascular aging.",
  LI),

 # Clinical Trials
 ("Trial results for a PD-L1 antibody therapy to reduce inflammation in Alzheimer's disease","Fight Aging!","2026-08-10","Clinical Trials","high",
  "Reported trial results for a PD-L1 antibody therapy targeting neuroinflammation add to the case for anti-inflammatory strategies against Alzheimer's disease.",
  FA+"trial-results-for-a-pd-l1-antibody-therapy-to-reduce-inflammation-in-alzheimers-disease/"),
 ("David Sinclair featured in National Geographic cover story on his longevity human clinical trial","Lifespan.io","2026-08-07","Clinical Trials","normal",
  "National Geographic's cover story profiles David Sinclair and the human clinical trial central to his longevity research program.",
  LI),

 # Biotech
 ("Targeting senescent cells to treat age-related chronic pulmonary disease","Fight Aging!","2026-08-14","Biotech","normal",
  "Preclinical work applies senolytic strategies to age-related chronic lung disease, extending anti-senescence approaches into pulmonary indications.",
  FA+"targeting-senescent-cells-to-treat-age-related-chronic-pulmonary-disease/"),
 ("Viome acquires Circulate Health, adding therapeutic plasma exchange to its diagnostics platform","Longevity.Technology","2026-08-14","Biotech","normal",
  "Viome's acquisition of Circulate Health brings therapeutic plasma exchange and a network of more than 200 partner clinics into a platform built around diagnostics, nutrition, and coaching.",
  LT),
 ("Insilico Medicine advances its Virtual Aging Cell platform to model biological change across scales","Longevity.Technology","2026-08-13","Biotech","normal",
  "Insilico Medicine is developing a Virtual Aging Cell platform that models biological change across six interconnected scales, treating biological age as a core variable rather than an output.",
  LT),

 # Funding
 ("New $7.5M NIH-funded USC center to investigate sex differences in aging","Longevity.Technology","2026-08-13","Funding","normal",
  "A $7.5 million NIH-funded center at USC will study sex differences in aging after decades of male-biased research, with potential to reshape biomarkers and clinical trial design.",
  LT),
 ("Longevity startup NewLimit raises $435M ahead of its first clinical trial","STAT News","2026-06-02","Funding","normal",
  "Epigenetic-reprogramming company NewLimit raised $435M to advance toward its first human trial, one of the year's largest longevity financings and a marker of capital concentrating in reprogramming.",
  "https://www.statnews.com/2026/06/02/longevity-startup-newlimit-announces-435-million-clinical-trial-financing/"),

 # Industry
 ("Longevity Clinics World and Healthy Longevity Medicine Society sign standards-focused MOU","Longevity.Technology","2026-08-14","Industry","normal",
  "The two bodies signed an MOU on evidence-based medicine, shared terminology, education, and quality standardization, part of the longevity clinic sector's move toward formal standards and accreditation.",
  LT),
 ("Timeline wins $5.3M judgment against sellers falsely marketing products as containing urolithin A","Longevity.Technology","2026-08-13","Industry","normal",
  "Swiss longevity company Timeline won a $5.3 million judgment against sellers falsely claiming their products contained urolithin A, reinforcing ingredient-integrity standards in the supplement market.",
  LT),
 ("David Sinclair launches Lifespan Group and its consumer platform Lifespan.com","Lifespan.io","2026-08-07","Industry","normal",
  "David Sinclair unveiled Lifespan Group LLC and its flagship consumer platform Lifespan.com, expanding science-media and product efforts in the longevity space.",
  LI),

 # Protocols
 ("Structured exercise drives measurable mechanisms of neuroprotection","Fight Aging!","2026-08-14","Protocols","normal",
  "A review of the biological mechanisms by which regular exercise protects the aging brain, from improved vascular function to reduced neuroinflammation.",
  FA+"mechanisms-of-neuroprotection-arising-from-exercise/"),
 ("Restricting dietary valine extends lifespan in male mice and improves healthspan in both sexes","Lifespan.io","2026-08-13","Protocols","normal",
  "A study found that lowering dietary intake of the amino acid valine extended median and maximum lifespan in male mice while improving healthspan measures in both sexes.",
  LI),
 ("Major review concludes reduced protein intake can slow aging","Lifespan.io","2026-08-11","Protocols","normal",
  "A review of animal and human evidence concludes that reducing protein intake can improve metabolism, alter nutrient-sensing pathways, and limit cellular damage associated with aging.",
  LI),
]

for title, source, date, cat, imp, desc, url in A:
    assert len(title) <= 130, (len(title), title)
    items.append({
        "title": title, "source": source, "date": date, "category": cat,
        "importance": imp, "description": desc, "url": url, "top_development": False
    })

# validation
cats = {"Clinical Trials","Research","Biotech","Funding","Industry","Protocols"}
seen = set(i["category"] for i in items)
assert cats.issubset(seen), cats - seen
assert 29 <= len(items) <= 35, len(items)
assert sum(1 for i in items if i["top_development"]) == 5
for i in items:
    assert i["importance"] in ("high","normal"), i
    assert i["category"] in cats, i
    assert len(i["title"]) <= 130

out = "/sessions/ecstatic-affectionate-dijkstra/mnt/outputs/news_data.json"
with open(out,"w") as f:
    json.dump(items, f, indent=2, ensure_ascii=False)

from collections import Counter
print("TOTAL:", len(items))
print("cards:", sum(1 for i in items if i["top_development"]))
print("by category:", dict(Counter(i["category"] for i in items)))
print("date range:", min(i["date"] for i in items), "->", max(i["date"] for i in items))
print("OK, wrote", out)

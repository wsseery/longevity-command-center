// ===== DATA =====
const compounds = [
  // === ORIGINAL ITP-TESTED COMPOUNDS (32) ===
  { name: "Rapamycin + Acarbose", category: "Combination Therapy", bestMale: 34, bestFemale: 28, itpResult: "positive", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Largest ITP effect ever. 34% male, 28% female median lifespan extension. Started at 9 months. Not yet tested in humans as combination." },
  { name: "Rapamycin (Sirolimus)", category: "mTOR Inhibitor", bestMale: 23, bestFemale: 26, itpResult: "positive", humanPhase: "Phase 2", activeTrials: 4, totalEnrollment: 1200, notes: "Gold standard. Consistent across multiple ITP cohorts and dose levels. PEARL trial completed. RTB101 Phase 3 failed." },
  { name: "Acarbose", category: "Glucose Metabolism", bestMale: 22, bestFemale: 5, itpResult: "positive", humanPhase: "Phase 1", activeTrials: 1, totalEnrollment: 50, notes: "Strong male effect. FDA-approved diabetes drug. Reduces postprandial glucose." },
  { name: "Metformin + Rapamycin", category: "Combination Therapy", bestMale: 23, bestFemale: 23, itpResult: "positive", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "23% both sexes. Uncertain if additive beyond rapamycin alone." },
  { name: "17-alpha-Estradiol", category: "Hormonal", bestMale: 19, bestFemale: 0, itpResult: "positive_males", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Males only. Non-feminizing. Works even started late in life." },
  { name: "Metformin", category: "Glucose Metabolism", bestMale: 7, bestFemale: 0, itpResult: "null", humanPhase: "Phase 3", activeTrials: 3, totalEnrollment: 3500, notes: "ITP null result — +7% male trend was not statistically significant (p=0.35). TAME trial is a landmark — FDA approved aging as composite endpoint. Awaiting full funding ($5M of $45-70M raised)." },
  { name: "GLP-1 Agonists (Semaglutide)", category: "Metabolic", bestMale: null, bestFemale: null, itpResult: "not_tested", humanPhase: "Phase 3", activeTrials: 10, totalEnrollment: 40000, notes: "Not ITP tested. SELECT: 20% CV risk reduction. EVOKE: Phase 3 Alzheimer's. Proposed as 'first longevity drug'." },
  { name: "Canagliflozin", category: "SGLT2 Inhibitor", bestMale: 14, bestFemale: 0, itpResult: "positive_males", humanPhase: "Phase 1", activeTrials: 2, totalEnrollment: 80, notes: "Males only +14%. Senolytic effects. Telomere lengthening in humans." },
  { name: "16-alpha-Hydroxyestradiol", category: "Hormonal", bestMale: 15, bestFemale: -7, itpResult: "positive_males", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Male benefit, female harm. Estriol metabolite." },
  { name: "Captopril", category: "ACE Inhibitor", bestMale: 14, bestFemale: 5, itpResult: "positive", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Both sexes benefit. ACE inhibitor — safety well established in humans but no aging trial." },
  { name: "NDGA", category: "Antioxidant", bestMale: 12, bestFemale: 0, itpResult: "positive_males", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Males only, consistent 8-12% across doses." },
  { name: "Astaxanthin", category: "Antioxidant", bestMale: 12, bestFemale: 0, itpResult: "positive_males", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Males +12%. Natural carotenoid. Follow-up studies in progress." },
  { name: "Glycine", category: "Amino Acid", bestMale: 6, bestFemale: 4, itpResult: "positive", humanPhase: "Phase 2", activeTrials: 2, totalEnrollment: 150, notes: "Both sexes. Cheap. GlyNAC Phase 2 improved 7/9 hallmarks of aging." },
  { name: "Meclizine", category: "mTORC1 Inhibitor", bestMale: 8, bestFemale: 0, itpResult: "positive_males", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "OTC anti-nausea drug. Males +8%. Follow-up testing." },
  { name: "Halofuginone", category: "ISR Activator", bestMale: 9, bestFemale: 0, itpResult: "positive_males", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Males +9%. Anti-fibrotic plant alkaloid. Late-life efficacy." },
  { name: "Mitoglitazone", category: "Mitochondrial", bestMale: 9, bestFemale: 0, itpResult: "positive_males", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Mitochondrial pyruvate carrier inhibitor. Males +9%." },
  { name: "Epicatechin", category: "Flavonoid", bestMale: 5, bestFemale: 0, itpResult: "positive_males", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Found in dark chocolate. Males +5% median, +6% max." },
  { name: "Protandim", category: "Nrf2 Activator", bestMale: 7, bestFemale: 0, itpResult: "positive_males", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Botanical blend. Weak positive. Only 1 of 3 sites." },
  { name: "Aspirin", category: "Anti-inflammatory", bestMale: 8, bestFemale: 0, itpResult: "null", humanPhase: "Phase 3", activeTrials: 0, totalEnrollment: 19114, notes: "ITP: initial positive not replicated. ASPREE Phase 3: NEGATIVE in 19,114 humans. Not recommended." },
  { name: "Dasatinib + Quercetin", category: "Senolytic", bestMale: null, bestFemale: null, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 6, totalEnrollment: 400, notes: "Pioneer senolytic. Most human data. IPF, CKD, cognitive trials." },
  { name: "Fisetin", category: "Senolytic", bestMale: -4, bestFemale: -6, itpResult: "null", humanPhase: "Phase 1", activeTrials: 5, totalEnrollment: 200, notes: "ITP NEGATIVE — did not extend lifespan. Human trials ongoing for senolytic effects." },
  { name: "NAD+ Precursors (NMN/NR)", category: "NAD+ Pathway", bestMale: 0, bestFemale: 0, itpResult: "null", humanPhase: "Phase 2", activeTrials: 8, totalEnrollment: 1500, notes: "NR null in ITP. 25+ human trials. Modest effects. Reliably raises NAD+ levels." },
  { name: "Spermidine", category: "Autophagy", bestMale: null, bestFemale: null, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 3, totalEnrollment: 200, notes: "Not ITP tested. Phase 2 improved memory. Autophagy inducer." },
  { name: "Resveratrol", category: "Sirtuin Pathway", bestMale: 0, bestFemale: 0, itpResult: "null", humanPhase: "Phase 2", activeTrials: 20, totalEnrollment: 5000, notes: "ITP null (3x tested). 150+ human trials, mostly neutral. GSK invested $1B — program failed." },
  { name: "Alpha-Ketoglutarate", category: "Epigenetic", bestMale: 3, bestFemale: 1, itpResult: "null", humanPhase: "Phase 2", activeTrials: 2, totalEnrollment: 200, notes: "ITP null. ABLE trial ongoing. 8-year bio age reduction in observational study." },
  { name: "Urolithin A", category: "Mitophagy", bestMale: null, bestFemale: null, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 3, totalEnrollment: 250, notes: "Not ITP tested. Improved muscle endurance. Mitophagy inducer." },
  { name: "Nicotinamide Riboside", category: "NAD+ Pathway", bestMale: 0, bestFemale: 0, itpResult: "null", humanPhase: "Phase 2", activeTrials: 5, totalEnrollment: 500, notes: "Null in ITP. Multiple human trials show NAD+ increase but modest clinical effects." },
  { name: "Curcumin", category: "Anti-inflammatory", bestMale: 0, bestFemale: 0, itpResult: "null", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Popular supplement. No ITP benefit." },
  { name: "Green Tea Extract", category: "Antioxidant", bestMale: 0, bestFemale: 0, itpResult: "null", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "No ITP benefit." },
  { name: "Fish Oil", category: "Omega-3", bestMale: 0, bestFemale: 0, itpResult: "null", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "ITP null. High dose caused harm at one site." },
  { name: "Simvastatin", category: "Statin", bestMale: 0, bestFemale: 0, itpResult: "null", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "No ITP benefit at any dose." },
  { name: "Enalapril", category: "ACE Inhibitor", bestMale: 0, bestFemale: 0, itpResult: "null", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "ACE inhibitor. No ITP benefit (unlike captopril)." },

  // === NEW: PEER-REVIEWED COMPOUNDS (20) ===
  // Tier 1: Mammalian lifespan replicated
  { name: "Selegiline (Deprenyl)", category: "MAO-B Inhibitor", bestMale: 34, bestFemale: 34, itpResult: "not_tested", humanPhase: "FDA Approved", activeTrials: 1, totalEnrollment: 100, notes: "Most replicated mammalian longevity drug outside ITP. 2025 meta-analysis: 22 studies, 4 species (rats, mice, hamsters, dogs), 6 countries, SMD=0.68 (p=0.0002). +34% remaining lifespan in aged rats. FDA-approved for Parkinson's and depression. Bell-shaped dose-response — low doses most effective." },
  { name: "Klotho Protein", category: "Longevity Factor", bestMale: 30, bestFemale: 26, itpResult: "not_tested", humanPhase: "Phase 1", activeTrials: 2, totalEnrollment: 150, notes: "Landmark Science 2005: overexpression extends mouse lifespan 20-30% across 2 transgenic lines. Klotho deficiency causes progeroid syndrome. 2025 AAV gene therapy: +15-20%. Single injection improved cognition in aged rhesus monkeys (Nature Aging 2023). Human epidemiology: higher serum Klotho = lower all-cause mortality. KLOTHO-VS allele confers cognitive advantage. Delivery challenges limit translation." },

  // Tier 2: Mammalian lifespan extension (single study or multi-species invertebrate)
  { name: "Taurine", category: "Amino Acid", bestMale: 10, bestFemale: 12, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 3, totalEnrollment: 300, notes: "Science 2023 landmark: +10-12% median lifespan in mice, +10-23% in C. elegans, healthspan improvements in rhesus monkeys. 34 research organizations, 2 independent labs. Taurine declines ~80% with age in humans. Reduces senescence, DNA damage, inflammaging. Widely available, safe supplement." },
  { name: "Trametinib (MEK Inhibitor)", category: "MAPK Pathway", bestMale: 10, bestFemale: 7, itpResult: "not_tested", humanPhase: "FDA Approved", activeTrials: 0, totalEnrollment: 0, notes: "Nature Aging 2025 (Partridge lab): +7-10% alone in mice. Combination with rapamycin: +27-35% — additive via distinct pathway (RAS/MAPK). FDA-approved for melanoma. Most promising candidate for combination longevity strategies. Extends Drosophila lifespan in multiple studies." },
  { name: "Berberine", category: "AMPK Activator", bestMale: 16, bestFemale: 16, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 4, totalEnrollment: 800, notes: "'Nature's metformin' — activates AMPK via complex I inhibition. Aging Cell 2020: +16.49% mean lifespan in naturally aged mice, 72% senescent cell reduction. +27% in C. elegans. Multiple human RCTs show comparable glucose-lowering to metformin. Poor oral bioavailability — phytosome formulations improving." },
  { name: "Methylene Blue", category: "Mitochondrial", bestMale: null, bestFemale: 6, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 0, totalEnrollment: 0, notes: "Oldest FDA-approved drug (~1891). +6% lifespan in female mice (Scientific Reports 2017). Alternative mitochondrial electron carrier — bypasses Complex I/III. +30% Complex IV activity. Reverses aging in human fibroblasts. Multiple Phase 2 Alzheimer's trials (tau aggregation). Hormetic — beneficial at low doses only." },
  { name: "Melatonin", category: "Circadian / Antioxidant", bestMale: 18, bestFemale: 18, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 0, totalEnrollment: 0, notes: "DrugAge aggregate: ~18% rodent lifespan extension across multiple studies. +13.5% median, +33.2% max in Drosophila. Upregulates SIRT1/SIRT3, stimulates autophagy, protects mitochondria. Results inconsistent across strains — may reflect anti-tumor effects. OTC in US, prescription (Circadin) in EU." },

  // Advanced human trials (no/limited rodent lifespan data but strong human evidence)
  { name: "Low-Dose Colchicine", category: "Anti-inflammatory", bestMale: null, bestFemale: null, itpResult: "not_tested", humanPhase: "FDA Approved", activeTrials: 2, totalEnrollment: 21800, notes: "Strongest human evidence on this list. FDA approved 2023 (LODOCO 0.5mg/day) for CV prevention. LoDoCo2 (n=5,522): 31% MACE reduction. COLCOT (n=4,745): 23% MACE reduction. Meta-analysis of 6 RCTs (n=21,800): 25% reduction. First anti-inflammatory approved for CV prevention. Targets NLRP3 inflammasome / inflammaging." },
  { name: "SS-31 (Elamipretide)", category: "Mitochondrial Peptide", bestMale: null, bestFemale: null, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 3, totalEnrollment: 400, notes: "Mitochondria-targeted tetrapeptide. Binds cardiolipin, restores cristae structure. Reverses age-related cardiac diastolic dysfunction and skeletal muscle decline in mice (eLife 2020). FDA Breakthrough Therapy designation for HFpEF. Most clinically advanced mitochondria-targeting aging intervention. Requires subcutaneous injection." },

  // Senolytics & novel mechanisms
  { name: "Procyanidin C1 (PCC1)", category: "Senolytic", bestMale: 10, bestFemale: 10, itpResult: "not_tested", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Nature Metabolism 2021: +10% median survival in aged mice. Dual senolytic (clears senescent cells via BCL-2 inhibition) AND senomorphic (suppresses SASP). Natural compound from grape seed extract. Replicated by independent lab (npj Aging 2025). Oral delivery advantage over synthetic senolytics." },
  { name: "Navitoclax (ABT-263)", category: "Senolytic", bestMale: 17, bestFemale: 17, itpResult: "not_tested", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "+16.7% median lifespan in obese Titan mice (GeroScience 2024). BCL-2/BCL-xL inhibitor. Rejuvenates hematopoietic stem cells, improves cognition in aged mice. Limitation: thrombocytopenia from BCL-xL inhibition limits chronic dosing. Disease model only — no WT mouse lifespan data. Platelet-sparing analogs in development." },
  { name: "FOXO4-DRI Peptide", category: "Senolytic Peptide", bestMale: null, bestFemale: null, itpResult: "not_tested", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Cell 2017 (Baar et al.): Disrupts FOXO4-p53 interaction selectively in senescent cells. Restored fitness, fur density, renal function in fast-aging mice. Improves vascular function in naturally aged mice (2026). No direct lifespan extension data in normal mice — healthspan only. Peptide delivery and cost challenges." },
  { name: "CD38 Inhibitor 78c", category: "NAD+ Metabolism", bestMale: 17, bestFemale: null, itpResult: "not_tested", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Aging Cell 2022: +17% median, +14% max lifespan in aged male mice. CD38 is the primary driver of age-related NAD+ decline — 78c addresses root cause rather than supplementing precursors (NMN/NR). Improved exercise capacity and metabolic function. Natural CD38 inhibitor apigenin has supportive data. May synergize with NMN/NR." },

  // Epigenetic reprogramming & gene therapy
  { name: "Partial Reprogramming (OSK)", category: "Epigenetic Reprogramming", bestMale: 109, bestFemale: 109, itpResult: "not_tested", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Most transformative concept. Browder et al. 2022/2024: OSK AAV delivery in 124-week-old mice extended median REMAINING lifespan by 109%. Ocampo 2016 (Cell): extends progeroid mouse lifespan. Lu 2020 (Nature): reverses vision loss. Risk: teratoma formation. Requires gene therapy — not a pill. Altos Labs, Retro Biosciences pursuing. Human trials 5-10+ years away." },

  // Telomerase / pineal
  { name: "TA-65 (Cycloastragenol)", category: "Telomerase Activator", bestMale: 15, bestFemale: 15, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 1, totalEnrollment: 750, notes: "Astragalus-derived telomerase activator. Aging Cell 2011: elongates short telomeres in mice, improves healthspan without cancer increase. Human meta-analysis (8 RCTs, n=750): statistically significant telomere lengthening, but no functional improvement in aging biomarkers. Commercially available. Long-term cancer safety monitoring needed." },

  // Invertebrate-validated compounds with strong mechanisms
  { name: "Low-Dose Lithium", category: "GSK-3β Inhibitor", bestMale: null, bestFemale: null, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 2, totalEnrollment: 200, notes: "+46% lifespan in C. elegans (J Biol Chem 2008). Extends Drosophila lifespan. FAILS in mice — negative rodent data is a significant limitation. However, human epidemiology: regions with higher lithium in water show lower suicide, dementia rates (multiple population studies). FDA-approved for bipolar. Narrow therapeutic window." },
  { name: "Sulforaphane", category: "NRF2 Activator", bestMale: null, bestFemale: null, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 5, totalEnrollment: 600, notes: "+18-50% lifespan in C. elegans (dose-dependent, multiple independent studies). From broccoli sprouts (50-100x more than mature broccoli). Activates NRF2 → ARE genes, HDAC inhibitor. No mammalian lifespan data. Extensive human Phase 2 data on inflammation and NRF2 biomarkers. Safe, widely available." },
  { name: "Trehalose", category: "Autophagy Inducer", bestMale: null, bestFemale: null, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 2, totalEnrollment: 150, notes: "+20-30% lifespan in C. elegans via mTOR-independent autophagy. Natural disaccharide. PNAS 2018: 3 independent genetic approaches confirm mechanism. Inhibits GLUT transporters → activates TFEB and lysosomal biogenesis. No mammalian lifespan data. Human trials for NASH and neurodegeneration." },
  { name: "Pterostilbene", category: "Stilbene / SIRT1", bestMale: null, bestFemale: null, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 2, totalEnrollment: 200, notes: "Methylated resveratrol analog with ~4x better bioavailability (~80% vs ~20%). +12-20% lifespan in Drosophila (2022). Improves oocyte quality in aged mice. Activates SIRT1/AMPK, crosses BBB better than resveratrol. No mammalian lifespan data. Human studies: improved lipids, BP, inflammation. Found in blueberries." },
  { name: "Alpha-Lipoic Acid", category: "Mitochondrial / ISC", bestMale: null, bestFemale: null, itpResult: "not_tested", humanPhase: "Phase 2", activeTrials: 0, totalEnrollment: 0, notes: "EMBO Reports 2020: extends Drosophila lifespan when started mid-life by reversing intestinal stem cell (ISC) dysfunction via endocytosis-autophagy mechanism. Novel ISC rejuvenation pathway. No mammalian lifespan data. FDA-approved in EU for diabetic neuropathy. Nrf2 activation, metal chelation, regenerates other antioxidants." },

  // Additional: Epitalon
  { name: "Epitalon (AEDG Peptide)", category: "Pineal Peptide", bestMale: null, bestFemale: 12, itpResult: "not_tested", humanPhase: "Preclinical", activeTrials: 0, totalEnrollment: 0, notes: "Synthetic tetrapeptide from pineal gland. Anisimov et al. (2001-2010): +12.3% maximum lifespan in SHR mice. Activates telomerase, modulates melatonin/epigenetic regulation. Primarily from one Russian research group — limited independent replication. Mean lifespan extension not consistently demonstrated. Widely sold as injectable peptide supplement." },
];

// ===== SCORING =====
const MAX_LIFESPAN = 109; // Updated for Partial Reprogramming OSK
const MAX_TRIALS = 20;

function phaseScore(phase) {
  switch(phase) {
    case 'FDA Approved': return 120;
    case 'Phase 3': return 100;
    case 'Phase 2': return 60;
    case 'Phase 1': return 30;
    case 'Preclinical': return 10;
    default: return 0;
  }
}

function computeComposite(c) {
  const bestEffect = Math.max(c.bestMale || 0, c.bestFemale || 0);
  const lifespanNorm = (bestEffect / MAX_LIFESPAN) * 100;
  const pScore = phaseScore(c.humanPhase);
  const trialsNorm = Math.min((c.activeTrials / MAX_TRIALS) * 100, 100);
  return (lifespanNorm * 0.4) + (pScore * 0.4) + (trialsNorm * 0.2);
}

// Compute scores
compounds.forEach(c => {
  c.compositeScore = computeComposite(c);
});

// Sort by composite score descending initially
let currentSort = { key: 'compositeScore', dir: 'desc' };
let currentFilter = 'all';
let currentSearch = '';
let expandedRow = null;

function sortCompounds(arr) {
  const { key, dir } = currentSort;
  return [...arr].sort((a, b) => {
    let va = a[key];
    let vb = b[key];
    // Handle nulls
    if (va === null || va === undefined) va = -999;
    if (vb === null || vb === undefined) vb = -999;
    // String sort
    if (typeof va === 'string') {
      if (key === 'humanPhase') {
        va = phaseScore(va);
        vb = phaseScore(vb);
      } else {
        return dir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
      }
    }
    return dir === 'asc' ? va - vb : vb - va;
  });
}

function filterCompounds(arr) {
  return arr.filter(c => {
    // Search
    if (currentSearch && !c.name.toLowerCase().includes(currentSearch.toLowerCase()) && !c.category.toLowerCase().includes(currentSearch.toLowerCase()) && !c.notes.toLowerCase().includes(currentSearch.toLowerCase())) return false;
    // Filter
    switch(currentFilter) {
      case 'itp_positive':
        return c.itpResult === 'positive' || c.itpResult === 'positive_males';
      case 'human_trials':
        return c.activeTrials > 0;
      case 'both':
        return (c.itpResult === 'positive' || c.itpResult === 'positive_males') && c.activeTrials > 0;
      case 'no_effect':
        return c.itpResult === 'null';
      case 'peer_reviewed':
        return c.itpResult === 'not_tested' && (c.bestMale > 0 || c.bestFemale > 0 || c.activeTrials > 0);
      default: return true;
    }
  });
}

// ===== CATEGORY MAPPING =====
function categoryClass(cat) {
  const map = {
    'mTOR Inhibitor': 'cat-mtor',
    'Glucose Metabolism': 'cat-glucose',
    'Combination Therapy': 'cat-combo',
    'Hormonal': 'cat-hormonal',
    'Metabolic': 'cat-metabolic',
    'SGLT2 Inhibitor': 'cat-sglt2',
    'ACE Inhibitor': 'cat-ace',
    'Antioxidant': 'cat-antioxidant',
    'Amino Acid': 'cat-amino',
    'Senolytic': 'cat-senolytic',
    'NAD+ Pathway': 'cat-nad',
    'Autophagy': 'cat-autophagy',
    'Sirtuin Pathway': 'cat-sirtuin',
    'Epigenetic': 'cat-epigenetic',
    'Mitophagy': 'cat-mitophagy',
    'Mitochondrial': 'cat-mitochondrial',
    'Flavonoid': 'cat-flavonoid',
    'Nrf2 Activator': 'cat-nrf2',
    'Anti-inflammatory': 'cat-anti-inflammatory',
    'Omega-3': 'cat-omega',
    'Statin': 'cat-statin',
    'ISR Activator': 'cat-isr',
    'mTORC1 Inhibitor': 'cat-mtor',
    // New categories
    'MAO-B Inhibitor': 'cat-maob',
    'Longevity Factor': 'cat-longevity',
    'MAPK Pathway': 'cat-mapk',
    'AMPK Activator': 'cat-ampk',
    'Circadian / Antioxidant': 'cat-circadian',
    'Mitochondrial Peptide': 'cat-mitochondrial',
    'Senolytic Peptide': 'cat-senolytic',
    'NAD+ Metabolism': 'cat-nad',
    'Epigenetic Reprogramming': 'cat-reprogramming',
    'Telomerase Activator': 'cat-telomerase',
    'GSK-3β Inhibitor': 'cat-gsk3',
    'NRF2 Activator': 'cat-nrf2',
    'Autophagy Inducer': 'cat-autophagy',
    'Stilbene / SIRT1': 'cat-sirtuin',
    'Mitochondrial / ISC': 'cat-mitochondrial',
    'Pineal Peptide': 'cat-pineal',
  };
  return map[cat] || 'cat-default';
}

function itpDisplay(result) {
  switch(result) {
    case 'positive': return { icon: '✓', cls: 'positive', label: 'Both sexes' };
    case 'positive_males': return { icon: '♂', cls: 'males', label: 'Males only' };
    case 'null': return { icon: '✗', cls: 'null-result', label: 'No effect' };
    case 'harmful': return { icon: '⚠', cls: 'harmful', label: 'Harmful' };
    case 'not_tested': return { icon: '🔬', cls: 'in-progress', label: 'Not ITP tested' };
    default: return { icon: '?', cls: 'null-result', label: 'Unknown' };
  }
}

function phaseClass(phase) {
  switch(phase) {
    case 'FDA Approved': return 'phase-fda';
    case 'Phase 3': return 'phase-3';
    case 'Phase 2': return 'phase-2';
    case 'Phase 1': return 'phase-1';
    case 'Preclinical': return 'preclinical';
    default: return 'none';
  }
}

function deltaHTML(val) {
  if (val === null || val === undefined) {
    return `<div class="delta-cell"><span class="delta-val na-val">N/A</span></div>`;
  }
  const absVal = Math.abs(val);
  const barWidth = Math.min((absVal / 40) * 100, 100); // Cap at 40% for bar display
  let barCls, valCls;
  if (val > 0) { barCls = 'positive-bar'; valCls = 'positive-val'; }
  else if (val < 0) { barCls = 'negative-bar'; valCls = 'negative-val'; }
  else { barCls = 'zero-bar'; valCls = 'zero-val'; }
  const sign = val > 0 ? '+' : '';
  return `<div class="delta-cell">
    <div class="delta-bar-wrap"><div class="delta-bar ${barCls}" style="width:0%" data-width="${barWidth}"></div></div>
    <span class="delta-val ${valCls}">${sign}${val}%</span>
  </div>`;
}

// ===== RENDER TABLE =====
const tbody = document.getElementById('tableBody');

function renderTable() {
  const sorted = sortCompounds(compounds);
  // Assign ranks from full sorted list
  sorted.forEach((c, i) => c.rank = i + 1);
  const filtered = filterCompounds(sorted);

  tbody.innerHTML = '';
  expandedRow = null;

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;padding:40px;color:var(--text-dim);">No compounds match your filters.</td></tr>`;
    return;
  }

  filtered.forEach((c, idx) => {
    const itp = itpDisplay(c.itpResult);
    const maxScore = compounds.reduce((m, x) => Math.max(m, x.compositeScore), 0);
    const scorePct = maxScore > 0 ? (c.compositeScore / maxScore) * 100 : 0;

    const tr = document.createElement('tr');
    tr.className = c.rank === 1 ? 'rank-1' : '';
    if (c.itpResult === 'not_tested' && (c.bestMale > 0 || c.bestFemale > 0 || c.activeTrials > 0)) {
      tr.classList.add('peer-reviewed');
    }
    tr.dataset.compound = c.name;

    let rankCls = '';
    if (c.rank === 1) rankCls = 'top-1';
    else if (c.rank === 2) rankCls = 'top-2';
    else if (c.rank === 3) rankCls = 'top-3';

    tr.innerHTML = `
      <td style="text-align:center"><span class="rank-num ${rankCls}">${c.rank}</span></td>
      <td><span class="compound-name">${c.name}</span></td>
      <td><span class="category-badge ${categoryClass(c.category)}">${c.category}</span></td>
      <td><span class="itp-icon ${itp.cls}">${itp.icon}</span><span class="itp-label">${itp.label}</span></td>
      <td>${deltaHTML(c.bestMale)}</td>
      <td>${deltaHTML(c.bestFemale)}</td>
      <td><span class="phase-badge ${phaseClass(c.humanPhase)}">${c.humanPhase}</span></td>
      <td><span class="trials-count">${c.activeTrials}</span></td>
      <td><div class="score-cell">
        <div class="score-bar-wrap"><div class="score-bar" style="width:0%" data-width="${scorePct}"></div></div>
        <span class="score-val">${c.compositeScore.toFixed(0)}</span>
      </div></td>
    `;

    tr.addEventListener('click', () => toggleDetail(c, tr));
    tbody.appendChild(tr);

    // Animate bars after a small delay
    requestAnimationFrame(() => {
      setTimeout(() => {
        tr.querySelectorAll('.delta-bar').forEach(bar => {
          bar.style.width = bar.dataset.width + '%';
        });
        tr.querySelectorAll('.score-bar').forEach(bar => {
          bar.style.width = bar.dataset.width + '%';
        });
      }, idx * 30);
    });
  });
}

function toggleDetail(compound, tr) {
  // Close existing
  const existing = document.querySelector('.detail-row');
  if (existing) {
    const wasForSame = existing.previousElementSibling === tr;
    existing.remove();
    expandedRow = null;
    if (wasForSame) return;
  }

  const detailTr = document.createElement('tr');
  detailTr.className = 'detail-row';

  const bestEffect = Math.max(compound.bestMale || 0, compound.bestFemale || 0);
  const enrollment = compound.totalEnrollment > 0 ? compound.totalEnrollment.toLocaleString() : 'N/A';

  let takeaway = '';
  if (compound.humanPhase === 'FDA Approved') {
    takeaway = 'FDA-approved drug being explored for aging indications — highest regulatory readiness.';
  } else if (compound.itpResult === 'positive' && compound.activeTrials > 0) {
    takeaway = 'Strong preclinical evidence AND active human trials — high translational potential.';
  } else if (compound.itpResult === 'positive' || compound.itpResult === 'positive_males') {
    if (compound.activeTrials === 0) {
      takeaway = 'Positive mouse data but no active human aging trials — translational gap.';
    } else {
      takeaway = 'Mouse lifespan benefit confirmed; human trials underway.';
    }
  } else if (compound.itpResult === 'null' && compound.activeTrials > 0) {
    takeaway = 'No mouse lifespan extension, but pursued in human trials for other aging-related endpoints.';
  } else if (compound.itpResult === 'not_tested' && bestEffect > 0 && compound.activeTrials > 0) {
    takeaway = 'Peer-reviewed lifespan data outside ITP with active human trials — promising pipeline candidate.';
  } else if (compound.itpResult === 'not_tested' && bestEffect > 0) {
    takeaway = 'Peer-reviewed lifespan extension data but no ITP validation or human aging trials yet.';
  } else if (compound.itpResult === 'not_tested' && compound.activeTrials > 0) {
    takeaway = 'Not yet tested in the ITP; advancing in human trials based on other preclinical evidence.';
  } else {
    takeaway = 'No significant lifespan extension in mice; not currently in human aging trials.';
  }

  // Determine source badge
  let sourceBadge = '';
  if (compound.itpResult !== 'not_tested') {
    sourceBadge = '<span class="source-badge itp-source">ITP Data</span>';
  } else {
    sourceBadge = '<span class="source-badge peer-source">Peer-Reviewed</span>';
  }

  detailTr.innerHTML = `<td colspan="9"><div class="detail-panel">
    <div class="detail-header-row"><h4>${compound.name}</h4>${sourceBadge}</div>
    <div class="detail-notes">${compound.notes}</div>
    <div class="detail-meta">
      <div class="detail-meta-item">
        <span class="detail-meta-label">Best Lifespan Effect</span>
        <span class="detail-meta-value">${bestEffect > 0 ? '+' + bestEffect + '%' : 'None detected'}</span>
      </div>
      <div class="detail-meta-item">
        <span class="detail-meta-label">Human Phase</span>
        <span class="detail-meta-value">${compound.humanPhase}</span>
      </div>
      <div class="detail-meta-item">
        <span class="detail-meta-label">Total Enrollment</span>
        <span class="detail-meta-value">${enrollment}</span>
      </div>
      <div class="detail-meta-item">
        <span class="detail-meta-label">Active Trials</span>
        <span class="detail-meta-value">${compound.activeTrials}</span>
      </div>
      <div class="detail-meta-item">
        <span class="detail-meta-label">Category</span>
        <span class="detail-meta-value">${compound.category}</span>
      </div>
    </div>
    <div style="margin-top:16px;padding-top:12px;border-top:1px solid rgba(0,221,255,0.1);">
      <span class="detail-meta-label">Key Takeaway</span>
      <span class="detail-meta-value" style="color:var(--amber);">${takeaway}</span>
    </div>
  </div></td>`;

  tr.after(detailTr);
  expandedRow = detailTr;
}

// ===== SORTING =====
document.querySelectorAll('thead th[data-sort]').forEach(th => {
  th.addEventListener('click', () => {
    const key = th.dataset.sort;
    if (key === 'rank') return; // rank is auto
    // Toggle direction
    if (currentSort.key === key) {
      currentSort.dir = currentSort.dir === 'desc' ? 'asc' : 'desc';
    } else {
      currentSort.key = key;
      currentSort.dir = 'desc';
    }
    // Update visual
    document.querySelectorAll('thead th').forEach(h => h.classList.remove('sorted-asc', 'sorted-desc'));
    th.classList.add(currentSort.dir === 'asc' ? 'sorted-asc' : 'sorted-desc');
    renderTable();
  });
});

// ===== FILTERS =====
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    renderTable();
  });
});

// ===== SEARCH =====
document.getElementById('searchInput').addEventListener('input', (e) => {
  currentSearch = e.target.value;
  renderTable();
});

// ===== STATS COUNTER ANIMATION =====
function animateCounters() {
  const cells = document.querySelectorAll('.stat-cell');
  cells.forEach((cell, i) => {
    setTimeout(() => {
      cell.classList.add('visible');
      const valEl = cell.querySelector('.stat-value');
      const target = parseInt(valEl.dataset.count);
      const duration = 1200;
      const start = performance.now();
      function tick(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        // easeOutExpo
        const ease = 1 - Math.pow(2, -10 * progress);
        valEl.textContent = Math.round(target * ease);
        if (progress < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }, i * 100);
  });
}

// ===== SCROLL ANIMATIONS =====
function setupScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.legend-card, .chart-card').forEach(el => {
    el.classList.add('animate-on-scroll');
    observer.observe(el);
  });
}

// ===== CHARTS =====
function initCharts() {
  // Chart.js defaults for dark theme
  Chart.defaults.color = '#8892a8';
  Chart.defaults.borderColor = 'rgba(0, 221, 255, 0.08)';
  Chart.defaults.font.family = "'JetBrains Mono', monospace";
  Chart.defaults.font.size = 11;

  // 1. Horizontal bar chart — Top 15 by lifespan (excluding outlier OSK)
  const top15 = [...compounds]
    .filter(c => c.name !== 'Partial Reprogramming (OSK)') // Exclude outlier for chart readability
    .map(c => ({ ...c, bestEffect: Math.max(c.bestMale || 0, c.bestFemale || 0) }))
    .sort((a, b) => b.bestEffect - a.bestEffect)
    .slice(0, 15);

  new Chart(document.getElementById('barChart'), {
    type: 'bar',
    data: {
      labels: top15.map(c => c.name.length > 22 ? c.name.substring(0, 20) + '…' : c.name),
      datasets: [
        {
          label: 'Male Δ%',
          data: top15.map(c => c.bestMale || 0),
          backgroundColor: 'rgba(0, 221, 255, 0.7)',
          borderColor: 'rgba(0, 221, 255, 1)',
          borderWidth: 1,
          borderRadius: 3,
        },
        {
          label: 'Female Δ%',
          data: top15.map(c => c.bestFemale || 0),
          backgroundColor: 'rgba(255, 176, 32, 0.7)',
          borderColor: 'rgba(255, 176, 32, 1)',
          borderWidth: 1,
          borderRadius: 3,
        }
      ]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { padding: 20, usePointStyle: true, pointStyle: 'rectRounded' }
        },
        tooltip: {
          backgroundColor: '#141a2e',
          borderColor: 'rgba(0,221,255,0.3)',
          borderWidth: 1,
          titleFont: { family: "'Outfit', sans-serif", weight: 600 },
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.x > 0 ? '+' : ''}${ctx.parsed.x}%`
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(0,221,255,0.05)' },
          ticks: { callback: v => v + '%' },
          title: { display: true, text: 'Median Lifespan Change %', color: '#556080' }
        },
        y: {
          grid: { display: false },
          ticks: {
            font: { size: 10 },
            color: '#e8edf5'
          }
        }
      }
    }
  });

  // 2. Bubble chart — Translational pipeline
  const phaseMap = { 'FDA Approved': 5, 'Phase 3': 4, 'Phase 2': 3, 'Phase 1': 2, 'Preclinical': 1, 'None': 0 };
  const bubbleData = compounds
    .filter(c => c.name !== 'Partial Reprogramming (OSK)') // Exclude outlier
    .map(c => ({
      x: Math.max(c.bestMale || 0, c.bestFemale || 0),
      y: phaseMap[c.humanPhase] || 0,
      r: Math.max(Math.sqrt(c.activeTrials || 0) * 5, 4),
      name: c.name,
      trials: c.activeTrials,
      isNew: c.itpResult === 'not_tested' && (c.bestMale > 0 || c.bestFemale > 0 || c.activeTrials > 0)
    }));

  // Color by quadrant + new compound distinction
  const bubbleColors = bubbleData.map(d => {
    if (d.x > 10 && d.y >= 3) return 'rgba(0, 255, 136, 0.6)';  // high mouse + high human
    if (d.x > 10 && d.y < 3) return d.isNew ? 'rgba(182, 120, 255, 0.6)' : 'rgba(0, 221, 255, 0.5)';   // high mouse, low human (purple for new)
    if (d.x <= 10 && d.y >= 3) return 'rgba(255, 176, 32, 0.5)'; // low mouse, high human
    return 'rgba(140, 150, 170, 0.3)';                             // low both
  });

  new Chart(document.getElementById('bubbleChart'), {
    type: 'bubble',
    data: {
      datasets: [{
        data: bubbleData,
        backgroundColor: bubbleColors,
        borderColor: bubbleColors.map(c => c.replace(/[\d.]+\)$/, '0.9)')),
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#141a2e',
          borderColor: 'rgba(0,221,255,0.3)',
          borderWidth: 1,
          titleFont: { family: "'Outfit', sans-serif", weight: 600 },
          callbacks: {
            title: items => items.length ? bubbleData[items[0].dataIndex].name : '',
            label: item => {
              const d = bubbleData[item.dataIndex];
              return [
                `Mouse effect: +${d.x}%`,
                `Active trials: ${d.trials}`,
              ];
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(0,221,255,0.05)' },
          title: { display: true, text: 'Best Mouse Lifespan Δ%', color: '#556080' },
          ticks: { callback: v => v + '%' },
          min: -8,
          max: 40
        },
        y: {
          grid: { color: 'rgba(0,221,255,0.05)' },
          title: { display: true, text: 'Human Trial Phase', color: '#556080' },
          ticks: {
            stepSize: 1,
            callback: v => {
              const labels = { 0: 'None', 1: 'Preclinical', 2: 'Phase 1', 3: 'Phase 2', 4: 'Phase 3', 5: 'FDA Approved' };
              return labels[v] || '';
            }
          },
          min: -0.5,
          max: 5.5
        }
      }
    }
  });
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
  // Set initial sort header visual
  const defaultTh = document.querySelector('th[data-sort="compositeScore"]');
  if (defaultTh) defaultTh.classList.add('sorted-desc');

  renderTable();
  animateCounters();
  setupScrollAnimations();
  initCharts();
});

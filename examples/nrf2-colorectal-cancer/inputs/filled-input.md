# Input as submitted

The Input section of `prompts/pathway-map-prompt.en.md`, filled in for this run.

## Required

- **Central factor:** NRF2 / NFE2L2
- **Disease / tissue / cell type:** Colorectal cancer
- **Target phenotype, or the relationship to be established:**
  - chemoresistance
  - migration / invasion / EMT
  - proliferation and metabolic reprogramming
  - ferroptosis resistance and stemness
  - anoikis resistance
- **Species:** Human. Mouse models and other systems permitted as candidate pathway only.

## Optional

- **Cell lines / subtypes / mutations to prioritise:** not specified
- **Stimuli / culture conditions to prioritise:** not specified
- **Factors or pathways to include:** not specified
- **Factors or pathways to exclude:** the cytoplasmic-NRF2 / PSMD4 branch (decided during Step 4 review — see below)
- **Specified papers:** none
- **Publication years / number of papers:** not specified
- **Level of detail:** standard
- **Mode:** confirm
- **Anything else:** baseline map, no drug-intervention layer

## Decisions taken at the Step 4 checkpoint

Confirm mode stopped after pathway selection and put three questions to the requester. The answers:

1. **Anoikis resistance** — keep as a candidate pathway (broken line), not moved to held-back information, despite the only evidence being C3 (fibrosarcoma / lung adenocarcinoma).
2. **Stemness** — same: keep as candidate.
3. **Cytoplasmic vs nuclear NRF2** — *exclude*. One retrieved paper (PMID 29899863) uses an NLS-mutant to argue that cytoplasmic NRF2 matters more than nuclear NRF2 for 5-FU and oxaliplatin resistance, acting through PSMD4 and an NF-κB/AKT/β-catenin/ZEB1 cascade. Including it would have required splitting NRF2 into cytosolic and nuclear nodes and would have added a branch that cuts against the conventional "nuclear import = activation" reading, plus 3-4 nodes. Excluded from this baseline map; recorded in the Papers and Review sheets rather than dropped.

## Assumptions recorded on the Summary sheet

- **A1** — Cell lines, subtypes and mutations were not specified; whatever each source used was recorded as-is in RawExtraction.
- **A2** — No stimulus or culture condition was prioritised; perturbations are recorded per observation.
- **A3** — All evidence came from PubMed abstracts. No figure panel was opened. Every row is marked `confirm = abstract`.
- **A4** — mRNA nodes are gene-product-level functional summaries, not a claim that transcription is the dominant mechanism.
- **A5** — The cytosol/nucleus split of NRF2 and the cNRF2-PSMD4 branch were excluded at the requester's instruction.

Five phenotypes exceed what a standard-detail map holds comfortably. The approach taken was to keep the shared upstream segment as a single trunk and branch to each phenotype through a representative effector axis (SLC7A11/GPX4, TXNRD1, HMOX1, ABCB1), rather than to develop each phenotype's downstream network in full.

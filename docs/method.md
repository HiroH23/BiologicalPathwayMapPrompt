# Method notes

Design rationale behind the template. This document explains *why* the rules are what they are; the rules themselves live in `prompts/`.

## 1. Two gradings, not one confidence score

Every relation carries two independent values.

**Evidence level (E)** describes how directly the relation was demonstrated.

| | Meaning | Typical experiment |
|---|---|---|
| E1 | Direct | purified protein / in vitro reaction, direct binding, ChIP + reporter mutation |
| E2 | Perturbation-dependent | knockdown, knockout, inhibitor, overexpression changes the downstream readout |
| E3 | Indirect | perturbation effect shown, but a mediator may intervene |
| E4 | Association only | correlation, co-expression, co-localisation |

**Context fit (C)** describes how well the experimental system matches the map's target.

| | Meaning |
|---|---|
| C1 | species, disease, cell/tissue and condition all match |
| C2 | species matches; cell, disease or condition partly differs |
| C3 | different species, or an unrelated cell line |
| C4 | cell-free, computational prediction, or database annotation only |

These are orthogonal. A co-immunoprecipitation in HEK293 is E1/C3. A rescue experiment in the exact patient-derived line of interest is E2/C1. A single score cannot represent both, and which weakness matters depends on what the map is for — so the template keeps them apart and records both.

A relation enters the **main pathway** only if it is C1-C2 *and* carries at least one piece of E1-E3 evidence. Everything else is either a **candidate pathway** (drawn, broken) or **held-back information** (not drawn, reason recorded).

## 2. The visual grammar

Three independent visual channels, none of which is colour:

| Channel | Encodes |
|---|---|
| Arrowhead / connector shape | type of action (conversion, catalysis, stimulation, inhibition, transcriptional regulation) |
| Line style (solid / broken) | pathway layer (main / candidate) |
| Position and compartment boxes | subcellular localisation |

Colour may mirror the biological type for scanning convenience, but no meaning depends on it. This keeps the figure readable in greyscale and for colour-vision-deficient readers, and it means a reader can tell "this arrow rests on an association in a different cell type" from the line itself rather than from a table.

The legend is required to cover only the symbols actually used, which stops it becoming a generic key that readers skip.

## 3. mRNA nodes as gene-product-level summaries

Papers routinely report both transcript and protein for a factor. Drawing both nodes for every factor doubles the map without adding mechanism.

The template collapses them onto the mRNA node **only when both move in the same direction**, and requires that the figure annotate such a node as a gene-product-level functional summary. Two consequences follow:

- Collapsing is not evidence that transcription is the dominant mechanism. Protein nodes are retained separately wherever modification, localisation or enzymatic action is part of the explanation.
- Where transcript and protein move in *opposite* directions, that is a finding, not noise. The template forbids collapsing and requires the discrepancy to be recorded.

A `gene → mRNA → protein` chain is never added automatically. Each such edge must correspond to a source that actually reasons across both levels.

## 4. State splitting

Phosphorylation, localisation and activity can each be represented as a state split. Mechanically expanding every combination produces a map that is technically richer and practically unreadable.

The criterion is: **does the difference change the downstream action?** If a note on the phosphorylated node already conveys the activity state, no separate "active" node is added.

Three inferences are explicitly forbidden because models make them by default:

- Phosphorylation is not activation unless shown.
- "Inhibits nuclear import" is not "promotes nuclear export".
- A candidate found by search is not thereby the mediator in the original experiment.

## 5. Enzymes versus scaffolds

Factors that assist a conversion attach to an **Anchor** on the conversion edge, not to the product node. This keeps "A becomes B" visually distinct from "C helps A become B".

The template requires distinguishing enzymes, transport cofactors, scaffold factors and allosteric regulators. In the worked example this produced a concrete correction: the first draft attached both SENP3 and CHTOP to the same Anchor, but the source describes CHTOP as *recruiting the SENP3-containing complex*. The final map draws CHTOP → SENP3 as its own complex-assembly edge, with only SENP3 as catalysis on the Anchor.

## 6. Isoform uncertainty

Where a source names a pathway rather than an isoform ("canonical PI3K/AKT/GSK3β signalling"), the template requires notation that preserves the uncertainty — `AKT1 and/or AKT2 and/or AKT3` — rather than silently picking one. Where an Xref is needed for a node like that, it points at one isoform as a documented placeholder, and the workbook says so.

## 7. Gaps and conflicts

**Gaps.** Where no adequate evidence exists, the template requires `Mediator unresolved` on the figure. A plausible candidate is not a substitute for evidence.

**Negative searches.** If differently worded queries all return nothing, that is recorded as "no hits in the retrieved set" — which is not the same claim as "the field holds no evidence". The distinction matters because a model cannot tell the two apart from search results alone.

**Conflicts.** Where findings about the same relation disagree, both are recorded, the edge or node is annotated "conflicting evidence", and the Review sheet records which was adopted and why. The worked example contains one: one paper shows NRF2 perturbation bidirectionally changes migration, another finds NRF2 barely induced by oxaliplatin and attributes EMT to a different axis. The former was adopted, because it perturbs NRF2 itself rather than testing a drug stimulus.

**Retractions.** Retracted papers and papers under an expression of concern are excluded, with the exclusion recorded rather than silently dropped.

**Cross-paper chains.** Where relations from different papers are joined into a pathway, the `cross-paper chain` column is flagged, making explicit that the chain as a whole was not demonstrated under one set of conditions.

## 8. Why validation is scripted

Visual self-assessment is unreliable. The template specifies mechanical checks instead, and the worked example demonstrates why: the first draft passed a reading-level review but the scripted checks found eight edges passing through unrelated node rectangles, and XSD validation found two encoding bugs (double float suffixes producing `179.0.0`, and schema-disallowed attributes on `<State>` elements).

The checks that matter most, in rough order of how often they catch something:

1. **Edge-through-node, per segment.** A line crossing a node box reads as a connection that is not there. This requires checking every segment of routed polylines, not just endpoints.
2. **XSD validation** against the official GPML2013a schema. Hand-written GPML looks fine and fails to load.
3. **Evidence-to-style consistency.** No E4 or C3/C4 relation may be drawn solid. This is the check that catches the map quietly overstating its own evidence.
4. **Bidirectional ID correspondence** between workbook and GPML. One-directional checks miss rows added to only one artifact.
5. GraphId uniqueness, reference resolution, vocabulary, node overlap, orphan nodes.

**Format-validated and rendering-confirmed are different claims.** The template requires keeping them distinct in the delivery report. A GPML that validates against the XSD may still lay out differently in PathVisio.

## 9. What the template does not do

It does not verify biology. It records what the retrieved papers state, applies a documented grading, and makes the reasoning auditable — which is a different thing from being right.

Grading is performed by a language model and is not reproducible run to run. E and C values should be read as the model's documented reasoning about each source, to be checked, not as measurements.

Evidence quality is bounded by what the model could actually read. An abstract-only run is a starting point for manual verification, and the template requires it to be labelled as one.

# Validation log

Run date: 2026-10-29. Script: [`build/validate.py`](build/validate.py).

## Status

**Format-validated. Not rendering-confirmed.**

The GPML passes format validation against the official GPML2013a XSD:

```
$ xmllint --noout --schema GPML2013a.xsd NRF2_CRC_baseline.gpml
NRF2_CRC_baseline.gpml validates
```

The file has **not** been opened in PathVisio itself. The included SVG and PNG are rendered from the same structural definition (`build/model.py`) by a separate renderer, so details may differ from how PathVisio lays the file out.

The schema used is `GPML2013a.xsd` from the PathVisio repository (`modules/org.pathvisio.core/resources/GPML2013a.xsd`).

## Final run

```
  [1] XML well-formed. Root=Pathway, namespace=http://pathvisio.org/GPML/2013a
  [2] XSD validation against GPML2013a.xsd: PASS
  [3] GraphId uniqueness: PASS (83 unique ids)
  [4] GraphRef / Anchor / GroupRef resolution: PASS
  [5] arrowhead vocabulary: PASS -> ['mim-catalysis', 'mim-conversion', 'mim-inhibition',
      'mim-stimulation', 'mim-transcription-translation']
  [6] DataNode Type vocabulary: PASS -> ['Pathway', 'Protein', 'Rna']
  [7] node-node overlap: PASS (none)
  [8] edge-through-node check: PASS (no edge passes through an unrelated node box)
  [9a] Entities <-> DataNode IDs: PASS (28 nodes, both directions)
  [9b] Reactions <-> Interaction IDs: PASS (34 reactions, both directions)
  [9c] every PaperID cited by a reaction exists in Papers: PASS (11 used)
  [9d] every PaperID cited by an observation exists in Papers: PASS
  [10] evidence-to-style consistency: PASS. No E4/C3/C4 relation is drawn solid;
       candidates drawn broken = ['R018', 'R024', 'R027', 'R031', 'R032', 'R033']
  [11] orphan node check: PASS (every node participates in >=1 edge)
  [12] relations from a non-target system (C3): ['R031', 'R032'] - all drawn broken and
       carry a 'Mediator unresolved' note on the arm

NO PROBLEMS FOUND by the checks above.
```

## What failed before it passed

Worth recording, because these are the reason the checks exist.

### Eight edges passed through unrelated node rectangles

The first draft laid every edge out as a straight line between node centres. The coordinate check found eight that crossed a node box they had nothing to do with:

```
R009 (GSK3B -> NRF2)                    crosses NRF2 (SUMOylated)
R014 (HNRNPC -> SLC7A11)                crosses SLC7A11 mRNA
R020 (GDF15 mRNA -> GDF15)              crosses UCKL1
R029 (NRF2 -> Proliferation / Warburg)  crosses TXNRD1 mRNA
R030 (NRF2 -> Migration & invasion)     crosses ABCB1 mRNA
R032 (HMOX1 mRNA -> Anoikis resistance) crosses Chemoresistance
R033 (NRF2 -> Stemness / CSC growth)    crosses TXNRD1 mRNA, Proliferation / Warburg
```

A line through a node box reads as a connection that is not there, so this is a correctness problem rather than a cosmetic one. Fixed in two ways: nodes were repositioned to open routing corridors in the gaps between columns, and eight edges were given intermediate Points so they route around obstructions as polylines. Two further crossings appeared during that rework (`R027` through `ATF4`, then `R031` through `TXNRD1 mRNA`) and were fixed the same way.

The check runs per *segment*, which matters once edges are polylines — checking only endpoints would have passed all of these.

### Two encoding bugs found by the XSD

Neither was visible to a reading-level review.

**Double float suffix.** Coordinates were formatted as `f"{value}.0"`, which is correct for an integer but produces `179.0.0` for a value already formatted as a float — not valid `xs:float`. Affected most Point coordinates and several Shape and Graphics attributes. Fixed with a single formatter applied to every coordinate emission.

**Disallowed attributes on `<State>`.** The `<Graphics>` child of a `<State>` element had `FontSize` and `Valign`, which GPML2013a does not permit there.

### A self-inflicted false positive

The first version of the GraphId-uniqueness check collected Anchors twice — once via a generic tree walk, once via an Anchor-specific pass — and reported `an_R006` as a duplicate. The GPML was correct; the check was wrong. Recorded here because a validator bug that reports a problem is cheap, and a validator bug that reports success is not.

## Checks and their limits

| Check | Limit |
|---|---|
| XSD validation | Confirms the file is schema-valid. Does not confirm PathVisio renders it as intended. |
| Edge-through-node | Treats nodes as rectangles with a 3 px pad. Does not model arrowhead geometry or label overflow outside the box. |
| Node overlap | Coordinate-based. Does not check whether text fits inside its box at render time. |
| Evidence-to-style | Verifies that no E4 or C3/C4 relation is drawn solid. Cannot verify that the E/C grading is itself correct. |
| ID correspondence | Bidirectional between workbook and GPML. Does not verify that row *content* matches the figure's meaning. |

The gradings themselves are not machine-checkable. They were applied by a language model from abstracts and should be read as documented reasoning to be verified, not as measurements.

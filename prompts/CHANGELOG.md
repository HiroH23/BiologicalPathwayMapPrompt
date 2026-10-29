# Changelog

## v1.1 — 2026-10-29

Revisions made after the first full run (the NRF2 / colorectal cancer example),
which surfaced gaps in v1.0.

**Added**
- Explicit definitions for evidence level (E1–E4), context fit (C1–C4) and pathway
  layer. v1.0 asked for "direct / indirect / association only" and "fit to the target
  condition" without defining them, so the judgement drifted between runs.
- Mandatory literature-handling rules: confirm that bibliographic records exist, do not
  infer figure numbers, record confirmation status, exclude retracted publications.
- Handling of conflicting findings: record both, annotate the figure, record which was
  adopted and why.
- Priority order for conflicting instructions (accuracy > traceability > readability >
  coverage).
- Node-count targets for each level of detail.
- `confirm` / `autonomous` mode, so pathway selection can be reviewed before drawing.
- Gene naming rules (human vs mouse) and the condition for collapsing mRNA and protein
  onto one node (same direction of change only).
- E3 ligase / deubiquitinase to the list of missing-mechanism categories.
- "No hits in the retrieved set" as a recordable outcome, distinct from "no evidence
  exists in the field".
- ID prefix conventions (OBS, R, S, N, P) so the workbook and GPML can be cross-checked
  mechanically.
- Scripted validation in place of visual self-assessment, including per-segment
  edge-through-node checking.

**Added to the GPML section**
- Xref requirement per DataNode, with the species-appropriate database.
- `<State>` elements for modification marks, rather than text in the label.
- `Group Style="Complex"` for complexes.
- Compartments drawn as Shapes.
- Coordinates are `xs:float`; do not append a second `.0`.
- Do not put schema-disallowed attributes (FontSize, Valign) on `<State>` Graphics.
- Intermediate Points for routing lines around obstructions, with no GraphRef or
  ArrowHead on an intermediate Point.

The last three were added because the first run produced exactly those errors, and the
XSD caught them.

## v1.0

Initial template: six-step procedure, Excel + GPML output, PathVisio-native
requirement, visual rules, reader's-view revision pass.

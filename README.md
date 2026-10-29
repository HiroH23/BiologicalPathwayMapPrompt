# Evidence-Tracked Pathway Map Prompt

A prompt template that asks a general-purpose LLM to build a biological pathway map from the literature, and to leave behind the evidence trail that produced it.

The output is two files that stay in sync:

- a **GPML** file (GPML2013a) that opens and edits natively in [PathVisio](https://pathvisio.github.io/), and
- an **Excel workbook** in which every node and every edge is traceable back to a specific observation in a specific paper.

Node and edge GraphIds in the GPML match row IDs in the workbook, in both directions.

## Why this exists

Asking a model for "a pathway diagram of X" usually produces one of two failure modes: a picture pasted into a file that cannot be edited, or a plausible-looking network in which it is impossible to tell which arrows rest on a direct biochemical experiment, which rest on a knockdown, and which rest on a correlation in a different cell type.

This template addresses that by making three things explicit and mandatory:

1. **Two independent gradings per relation.** Directness (E1-E4) and context fit (C1-C4) are recorded separately. A direct binding experiment in the wrong cell type and an indirect effect in exactly the right model are different kinds of weakness, and collapsing them into one "confidence" score hides that.
2. **A visual grammar tied to evidence.** Arrowhead shape encodes the type of action. Line style encodes the pathway layer. Anything resting on association only, or on a different experimental system, is drawn broken, and the figure says so in its legend.
3. **Gaps stay visible.** Where no adequate evidence was found, the template requires "Mediator unresolved" rather than a plausible filler. Searches that returned nothing are recorded as searches that returned nothing, which is distinct from a claim that the field holds no evidence.

## Repository layout

```
prompts/
  pathway-map-prompt.ja.md     Japanese template (the original)
  pathway-map-prompt.en.md     English template
  CHANGELOG.md
docs/
  method.md                    The grading scheme and design rationale
  index.html                   Single-page overview with the worked example
examples/
  nrf2-colorectal-cancer/      Worked example: NRF2 in colorectal cancer
```

## Using it

Copy the template, fill in the Input section, and give it to a model that can search the literature and write files. The required fields are the central factor, the disease/tissue/cell type, the target phenotype, and the species. Everything else has a documented default.

Two options are worth setting deliberately:

- **Level of detail** caps the node count (overview ~10-20, standard ~20-40, detailed ~40-70). Without a cap, maps drift toward unreadable density.
- **Mode.** `confirm` stops after pathway selection and presents the proposed main and candidate pathways before drawing. `autonomous` runs to completion. Confirm mode is worth the extra round trip when the phenotype list is broad, because that is where the evidence usually turns out to be thinner than expected.

The template assumes the model has a literature search tool and can write files. With weaker tooling it will still produce the structure, but the delivery report is required to state what could not be done rather than claim it was done.

## Worked example

[`examples/nrf2-colorectal-cancer/`](examples/nrf2-colorectal-cancer/) contains a complete run: NRF2 (NFE2L2) in human colorectal cancer, across five requested phenotypes. 28 nodes, 34 reactions, 12 papers.

![NRF2 colorectal cancer baseline map](examples/nrf2-colorectal-cancer/outputs/NRF2_CRC_baseline_preview.png)

The example is included partly because it did **not** come out clean, and the failures are the informative part. Two of the five requested phenotypes turned out to have no supporting evidence in colorectal cancer at all and are drawn as broken candidate arms with "Mediator unresolved" on them. One retrieved paper was retracted and is recorded as excluded. One relation has directly conflicting evidence in the literature, and the workbook records both findings and which was adopted. See [`examples/nrf2-colorectal-cancer/README.md`](examples/nrf2-colorectal-cancer/README.md).

A caveat that applies to the whole example: every piece of evidence in it was read from PubMed abstracts. No figure panel was opened. The workbook marks all 12 papers `confirm = abstract`, `figure = not checked`. That is a real limitation, not a formality — the E1 relations in particular should be verified against the original figures before the map is used for anything load-bearing.

## Validation

The example ships with the validation script that produced it. It checks:

- format validation against the official GPML2013a XSD
- GraphId uniqueness
- GraphRef / Anchor / GroupRef reference resolution
- ArrowHead and DataNode Type vocabulary
- node-node overlap, from coordinates
- whether any segment of any edge passes through an unrelated node's rectangle
- ID correspondence between the workbook and the GPML, in both directions
- that no E4 or C3/C4 relation is drawn solid

Running it on the first draft of the example found eight edges passing through unrelated nodes, and the XSD check found two genuine encoding bugs. Both are the reason the checks are in the template.

**Format-validated is not the same as rendering-confirmed.** The example GPML passes `xmllint --noout --schema GPML2013a.xsd`, and the included SVG/PNG are rendered from the same structural definition — but by a separate renderer, not by PathVisio. Details may differ from how PathVisio draws it.

## Scope and limits

- The template produces a **baseline map**: no drug-intervention layer. Overlaying compounds is a separate pass.
- It does not verify biology. It records what the retrieved papers state, with the grading that was applied, and makes the reasoning auditable. Whether the resulting model is correct is a question for the reader.
- Evidence quality is bounded by what the model could actually read. Abstract-only runs are explicitly marked as such and should be treated as a starting point for manual verification.
- Grading is applied by a language model and is not reproducible run to run. Treat E/C values as the model's documented reasoning, not as measurements.

## License

**A repository-wide reuse license has not been selected.** See [licensing notes](docs/licensing.md) before publishing or describing this package as open source. Set authorship and choose an appropriate license as the repository owner.


The worked example cites published literature by PMID and DOI; those papers remain under their own copyright. Nothing in the example reproduces source text.

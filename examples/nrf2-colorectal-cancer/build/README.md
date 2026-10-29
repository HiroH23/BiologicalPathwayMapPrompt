# Build scripts

Everything in `../outputs/` is generated from two source files, which is what keeps the
GPML, the workbook and the preview consistent with one another.

| File | Contents |
|---|---|
| `model.py` | Figure structure: nodes, reactions, routing waypoints, compartments, canvas |
| `evidence.py` | Observation records (`OBS*`) and the candidate-mechanism search log (`S*`) |
| `build_gpml.py` | Writes the GPML2013a file |
| `build_xlsx.py` | Writes the 7-sheet evidence workbook |
| `build_svg.py` | Writes the preview SVG (imports geometry helpers from `build_gpml.py`) |
| `validate.py` | Runs every check listed in `../VALIDATION.md` |

## Rebuilding

```bash
python3 build_gpml.py
python3 build_xlsx.py
python3 build_svg.py
python3 validate.py
xmllint --noout --schema GPML2013a.xsd NRF2_CRC_baseline.gpml
```

Outputs land in the current directory; move them to `../outputs/` when you are done.

Requires `openpyxl` and `lxml`. `cairosvg` is needed only for the PNG:

```bash
python3 -c "import cairosvg; cairosvg.svg2png(url='NRF2_CRC_baseline_preview.svg', write_to='NRF2_CRC_baseline_preview.png', output_width=1800)"
```

`validate.py` uses `GPML2013a.xsd` from the working directory and fetches it if absent
(from the PathVisio repository, `modules/org.pathvisio.core/resources/GPML2013a.xsd`).
The schema is gitignored rather than vendored.

## Editing the map

Change `model.py`, not the generated files. Node positions are explicit coordinates;
`via=[(x, y), ...]` on a reaction routes that edge as a polyline around obstructions.
After any change, rerun `validate.py` — the edge-through-node check is the one that
catches layout regressions, and it checks every segment of a routed edge.

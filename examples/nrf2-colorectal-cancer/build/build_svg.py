"""Preview SVG rendered from the same structure as the GPML."""
from xml.sax.saxutils import escape
from model import (N, R, COMPARTMENTS, CANVAS_W, CANVAS_H,
                   NODE_W, NODE_H, PHENO_W, PHENO_H)
from build_gpml import edge_points, size

NODES = {n["id"]: n for n in N}

TYPE_STROKE = {"Protein": "#1f4e79", "Rna": "#7a4b00",
               "Pathway": "#2e5e2e", "GeneProduct": "#1f4e79",
               "Metabolite": "#555555"}

o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
  f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="Helvetica, Arial, sans-serif">')
a('<rect width="100%" height="100%" fill="#ffffff"/>')

# arrowhead / connector markers
a('<defs>')
a('<marker id="conversion" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
  'markerHeight="7" orient="auto-start-reverse">'
  '<path d="M0,1 L9,5 L0,9 z" fill="#333"/></marker>')
a('<marker id="stimulation" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
  'markerHeight="7" orient="auto-start-reverse">'
  '<path d="M0,1 L9,5 L0,9 z" fill="none" stroke="#333" stroke-width="1.3"/></marker>')
a('<marker id="transcription" viewBox="0 0 12 10" refX="11" refY="5" markerWidth="8" '
  'markerHeight="8" orient="auto-start-reverse">'
  '<path d="M0,1 L10,5 L0,9 z" fill="#333"/>'
  '<path d="M10,0 L10,10" stroke="#333" stroke-width="1.2"/></marker>')
a('<marker id="inhibition" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" '
  'markerHeight="8" orient="auto-start-reverse">'
  '<path d="M7,0 L7,10" stroke="#333" stroke-width="2"/></marker>')
a('<marker id="catalysis" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="9" '
  'markerHeight="9" orient="auto-start-reverse">'
  '<circle cx="6" cy="6" r="4.5" fill="none" stroke="#333" stroke-width="1.3"/></marker>')
a('</defs>')

MARKER = {"mim-conversion": "conversion", "mim-stimulation": "stimulation",
          "mim-inhibition": "inhibition", "mim-catalysis": "catalysis",
          "mim-transcription-translation": "transcription"}

# compartments
for c in COMPARTMENTS:
    a(f'<rect x="{c["x1"]}" y="{c["y1"]}" width="{c["x2"]-c["x1"]}" '
      f'height="{c["y2"]-c["y1"]}" rx="14" fill="none" stroke="#9e9e9e" '
      'stroke-width="2"/>')
    a(f'<text x="{c["x1"]+10}" y="{c["y1"]+16}" font-size="10" fill="#6b6b6b" '
      f'font-style="italic">{escape(c["label"])}</text>')


def draw_edge(path, arrow, dashed):
    """path = [(x,y), ...]; only the final segment carries the arrowhead."""
    dash = ' stroke-dasharray="6,4"' if dashed else ''
    pts = " ".join(f"{x},{y}" for x, y in path[:-1])
    if len(path) > 2:
        a(f'<polyline points="{pts}" fill="none" stroke="#333" '
          f'stroke-width="1.2"{dash}/>')
    (xa, ya), (xb, yb) = path[-2], path[-1]
    a(f'<line x1="{xa}" y1="{ya}" x2="{xb}" y2="{yb}" stroke="#333" '
      f'stroke-width="1.2"{dash} marker-end="url(#{MARKER[arrow]})"/>')


for r in R:
    src, dst = NODES[r["src"]], NODES[r["dst"]]
    x1, y1, _, _, x2, y2, _, _ = edge_points(src, dst, r["via"])
    draw_edge([(x1, y1)] + [tuple(p) for p in r["via"]] + [(x2, y2)],
              r["arrow"], r["layer"] == "candidate")
    if r["helper"]:
        ax, ay = (src["x"] + dst["x"]) / 2, (src["y"] + dst["y"]) / 2
        a(f'<circle cx="{ax}" cy="{ay}" r="2.5" fill="#333"/>')
        for spec in r["helper"].split(","):
            nid, arrow = spec.split(":")
            hn = NODES[nid]
            hw, _ = size(hn)
            hx = hn["x"] - hw / 2 if hn["x"] > ax else hn["x"] + hw / 2
            draw_edge([(hx, hn["y"]), (ax, ay)], arrow, False)

# nodes
for n in N:
    w, h = size(n)
    x, y = n["x"] - w / 2, n["y"] - h / 2
    rx = 10 if n["comp"] == "phenotype" else 2
    dash = ' stroke-dasharray="5,3"' if n["layer"] == "candidate" else ''
    stroke = TYPE_STROKE.get(n["type"], "#333")
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="#ffffff" '
      f'stroke="{stroke}" stroke-width="1.5"{dash}/>')
    label = n["label"]
    if len(label) > 26:
        words, lines, cur = label.split(" "), [], ""
        for wd in words:
            if len(cur + " " + wd) > 26 and cur:
                lines.append(cur); cur = wd
            else:
                cur = (cur + " " + wd).strip()
        lines.append(cur)
    else:
        lines = [label]
    fs = 9 if len(lines) > 1 else 10
    y0 = n["y"] - (len(lines) - 1) * fs / 2 + fs / 3
    for i, ln in enumerate(lines):
        a(f'<text x="{n["x"]}" y="{y0 + i*fs}" font-size="{fs}" text-anchor="middle" '
          f'fill="#111">{escape(ln)}</text>')
    if n["state"]:
        sx, sy = n["x"] + w / 2, n["y"] - h / 2
        a(f'<circle cx="{sx}" cy="{sy}" r="8" fill="#ffffff" stroke="{stroke}" '
          'stroke-width="1.2"/>')
        a(f'<text x="{sx}" y="{sy+3}" font-size="9" text-anchor="middle" '
          f'fill="#111">{n["state"]}</text>')

# unresolved-mediator notes
a('<text x="352" y="960" font-size="8.5" text-anchor="start" fill="#8a4a00">'
  'Mediator unresolved (anoikis arm: no CRC evidence)</text>')
a('<text x="960" y="960" font-size="8.5" text-anchor="end" fill="#8a4a00">'
  'Mediator unresolved (stemness arm)</text>')

# legend
LX, LY = 60, 1090
a(f'<rect x="{LX-10}" y="{LY-18}" width="1170" height="200" rx="10" fill="none" '
  'stroke="#cccccc"/>')
a(f'<text x="{LX}" y="{LY}" font-size="11" font-weight="bold" fill="#111">LEGEND</text>')
legend_lines = [
    "Arrowhead = type of action.   Filled triangle: conversion.   Open triangle: stimulation.   "
    "Bar: inhibition.   Open circle: catalysis.   Triangle with bar: transcriptional regulation.",
    "Solid line / solid box = main pathway (context fit C1-C2, evidence E1-E3).   "
    "Broken line / broken box = candidate pathway (other system, or association only).",
    "Boxes = subcellular compartment. The nucleus is drawn twice; both regions are the same compartment.",
    "Rna nodes are gene-product-level functional summaries. mRNA-to-protein edges are not measured translation steps.",
    "'S' mark on NRF2 = SUMO conjugation, removed by SENP3 (reaction R006). Helper factors attach to the midpoint of the reaction they assist.",
    "Node outline colour only mirrors the biological type label; no meaning depends on colour alone.",
]
for i, t in enumerate(legend_lines, 1):
    a(f'<text x="{LX}" y="{LY + 20*i}" font-size="9.5" fill="#333">{escape(t)}</text>')
a(f'<text x="{LX}" y="{LY + 20*(len(legend_lines)+1) + 4}" font-size="9.5" '
  'fill="#333">Reading order: start at the top (MYC, FOXO3, GDF15), follow down to NRF2 in the '
  'middle, then to the target genes and the phenotype row at the bottom.</text>')

# node type key
keys = [("Protein", "#1f4e79"), ("Rna", "#7a4b00"), ("Phenotype (Pathway)", "#2e5e2e")]
for i, (lbl, col) in enumerate(keys):
    kx = LX + 10 + i * 220
    ky = LY + 20*(len(legend_lines)+2) + 10
    a(f'<rect x="{kx}" y="{ky-10}" width="16" height="13" rx="2" fill="#fff" '
      f'stroke="{col}" stroke-width="1.5"/>')
    a(f'<text x="{kx+22}" y="{ky}" font-size="9.5" fill="#333">{escape(lbl)}</text>')

a('<text x="630" y="28" font-size="14" font-weight="bold" text-anchor="middle" '
  'fill="#111">NRF2 signalling in colorectal cancer malignant progression '
  '(baseline map, Homo sapiens)</text>')
a('</svg>')

with open("NRF2_CRC_baseline_preview.svg", "w", encoding="utf-8") as f:
    f.write("\n".join(o) + "\n")
print("wrote NRF2_CRC_baseline_preview.svg")

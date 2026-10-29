"""Generate GPML2013a from model.py."""
from xml.sax.saxutils import escape
from model import (N, R, PAPERS, COMPARTMENTS, CANVAS_W, CANVAS_H,
                   NODE_W, NODE_H, PHENO_W, PHENO_H)

NODES = {n["id"]: n for n in N}


def f(v):
    """GPML wants plain xs:float text; never append a second '.0'."""
    return f"{float(v):.1f}"

def size(n):
    return (PHENO_W, PHENO_H) if n["comp"] == "phenotype" else (NODE_W, NODE_H)

def _side(n, tx, ty):
    """Edge-midpoint of node n on the side facing point (tx, ty)."""
    w, h = size(n)
    dx, dy = tx - n["x"], ty - n["y"]
    if abs(dx) * h >= abs(dy) * w:
        return (n["x"] + w / 2, n["y"], 1.0, 0.0) if dx > 0 else \
               (n["x"] - w / 2, n["y"], -1.0, 0.0)
    return (n["x"], n["y"] + h / 2, 0.0, 1.0) if dy > 0 else \
           (n["x"], n["y"] - h / 2, 0.0, -1.0)


def edge_points(src, dst, via=None):
    """Pick anchor sides so lines leave the bottom / enter the top when flowing down.

    With waypoints, the exit side faces the first waypoint and the entry side
    faces the last one, so a routed line does not double back over its own node.
    """
    via = via or []
    sw, sh = size(src); dw, dh = size(dst)
    if via:
        fx, fy = via[0]
        lx, ly = via[-1]
        sx, sy, srx, sry = _side(src, fx, fy)
        dxp, dyp, drx, dry = _side(dst, lx, ly)
        return (sx, sy, srx, sry, dxp, dyp, drx, dry)
    sx, sy, srx, sry = _side(src, dst["x"], dst["y"])
    dxp, dyp, drx, dry = _side(dst, src["x"], src["y"])
    return (sx, sy, srx, sry, dxp, dyp, drx, dry)


out = []
a = out.append
a('<?xml version="1.0" encoding="UTF-8"?>')
a('<Pathway xmlns="http://pathvisio.org/GPML/2013a" '
  'Name="NRF2 signalling in colorectal cancer malignant progression (baseline map)" '
  'Data-Source="Literature-derived, PubMed" Version="20261029" '
  'Organism="Homo sapiens">')
a('  <Comment Source="WikiPathways-description">Baseline, evidence-tracked map of NRF2 '
  '(NFE2L2) regulation and its downstream effectors in human colorectal cancer. '
  'Solid edges = main pathway (species/disease/cell match C1-C2 and evidence level E1-E3). '
  'Broken edges = candidate pathway (other systems, or association only). '
  'mRNA nodes are gene-product-level functional summaries, not claims that transcription '
  'is the dominant mechanism. No drug intervention layer is included. '
  'Node and edge GraphIds correspond to the Entities and Reactions sheets of the companion '
  'Excel file.</Comment>')
a(f'  <Graphics BoardWidth="{f(CANVAS_W)}" BoardHeight="{f(CANVAS_H)}" />')

# ---- DataNodes
for n in N:
    w, h = size(n)
    style = ' LineStyle="Broken"' if n["layer"] == "candidate" else ''
    fill = ' FillColor="ffffff"'
    if n["comp"] == "phenotype":
        shape = ' ShapeType="RoundedRectangle"'
    else:
        shape = ''
    a(f'  <DataNode TextLabel="{escape(n["label"])}" GraphId="{n["id"]}" Type="{n["type"]}">')
    if n["note"]:
        a(f'    <Comment>{escape(n["note"])}</Comment>')
    a(f'    <Graphics CenterX="{f(n["x"])}" CenterY="{f(n["y"])}" Width="{f(w)}" '
      f'Height="{f(h)}" ZOrder="32768" FontSize="10" Valign="Middle"{shape}{fill}{style} />')
    a(f'    <Xref Database="{escape(n["xdb"])}" ID="{escape(n["xid"])}" />')
    a('  </DataNode>')

# ---- States (modification marks)
si = 0
for n in N:
    if n["state"]:
        si += 1
        a(f'  <State GraphRef="{n["id"]}" TextLabel="{n["state"]}" GraphId="st{si:03d}" '
          f'StateType="ProteinModification">')
        a('    <Comment>SUMO conjugation. Removed by SENP3 (see R006).</Comment>')
        a('    <Graphics RelX="1.0" RelY="-1.0" Width="16.0" Height="16.0" '
          'ShapeType="Oval" FillColor="ffffff" />')
        a('    <Xref Database="" ID="" />')
        a('  </State>')

# ---- Interactions
for r in R:
    src, dst = NODES[r["src"]], NODES[r["dst"]]
    x1, y1, rx1, ry1, x2, y2, rx2, ry2 = edge_points(src, dst, r["via"])
    style = ' LineStyle="Broken"' if r["layer"] == "candidate" else ''
    need_anchor = bool(r["helper"])
    a(f'  <Interaction GraphId="{r["id"]}">')
    a(f'    <Comment>{escape(r["kind"])} | evidence {r["E"]} | context fit {r["C"]} | '
      f'papers {r["papers"]}' + (' | cross-paper chain' if r["cross"] else '') +
      (f' | {escape(r["note"])}' if r["note"] else '') + '</Comment>')
    a(f'    <Graphics ZOrder="12288" LineThickness="1.0"{style}>')
    a(f'      <Point X="{f(x1)}" Y="{f(y1)}" GraphRef="{r["src"]}" RelX="{f(rx1)}" RelY="{f(ry1)}" />')
    for (vx, vy) in r["via"]:
        a(f'      <Point X="{f(vx)}" Y="{f(vy)}" />')
    a(f'      <Point X="{f(x2)}" Y="{f(y2)}" GraphRef="{r["dst"]}" RelX="{f(rx2)}" RelY="{f(ry2)}" '
      f'ArrowHead="{r["arrow"]}" />')
    if need_anchor:
        a(f'      <Anchor Position="0.5" GraphId="an_{r["id"]}" Shape="None" />')
    a('    </Graphics>')
    a('    <Xref Database="" ID="" />')
    a('  </Interaction>')

# ---- helper (catalysis / recruitment) edges onto anchors
hi = 0
for r in R:
    if not r["helper"]:
        continue
    for spec in r["helper"].split(","):
        nid, arrow = spec.split(":")
        hi += 1
        hn = NODES[nid]
        hw, hh = size(hn)
        src_n, dst_n = NODES[r["src"]], NODES[r["dst"]]
        ax = (src_n["x"] + dst_n["x"]) / 2
        ay = (src_n["y"] + dst_n["y"]) / 2
        # leave the helper from the side facing the anchor
        if hn["x"] > ax:
            hx, hrx = hn["x"] - hw / 2, -1.0
        else:
            hx, hrx = hn["x"] + hw / 2, 1.0
        a(f'  <Interaction GraphId="H{hi:03d}">')
        label = "catalysis" if arrow == "mim-catalysis" else "recruitment / scaffold"
        a(f'    <Comment>{label} onto {r["id"]} | source {hn["label"]} | '
          f'see Reactions sheet row {r["id"]}</Comment>')
        a('    <Graphics ZOrder="12288" LineThickness="1.0">')
        a(f'      <Point X="{f(hx)}" Y="{f(hn["y"])}" GraphRef="{nid}" '
          f'RelX="{f(hrx)}" RelY="0.0" />')
        a(f'      <Point X="{f(ax)}" Y="{f(ay)}" GraphRef="an_{r["id"]}" RelX="0.0" '
          f'RelY="0.0" ArrowHead="{arrow}" />')
        a('    </Graphics>')
        a('    <Xref Database="" ID="" />')
        a('  </Interaction>')

# ---- Labels (legend)
LEG_X, LEG_Y = 300, 1100
legend = [
    ("LEGEND", 0, True),
    ("Arrowhead = type of action:  conversion / catalysis / stimulation / inhibition / transcriptional regulation", 20, False),
    ("Solid line = main pathway (context fit C1-C2, evidence E1-E3).   Broken line = candidate pathway (other system, or association only).", 38, False),
    ("Boxes = subcellular compartment. The nucleus is drawn twice; both regions are the same compartment.", 56, False),
    ("Rna nodes are gene-product-level summaries. mRNA-to-protein edges are not measured translation steps.", 74, False),
    ("'S' state mark on NRF2 = SUMO conjugation, removed by SENP3.   Colour carries no meaning in this map.", 92, False),
]
for i, (txt, dy, bold) in enumerate(legend, 1):
    fw = ' FontWeight="Bold"' if bold else ''
    a(f'  <Label TextLabel="{escape(txt)}" GraphId="LG{i:03d}">')
    a(f'    <Graphics CenterX="{f(LEG_X + 320)}" CenterY="{f(LEG_Y + dy)}" Width="1140.0" '
      f'Height="18.0" ZOrder="28672" FontSize="9" Valign="Middle" Align="Left"{fw} />')
    a('  </Label>')

a('  <Label TextLabel="Mediator unresolved (anoikis arm: no CRC evidence)" GraphId="LG100">')
a('    <Graphics CenterX="520.0" CenterY="960.0" Width="330.0" Height="16.0" '
  'ZOrder="28672" FontSize="8" Valign="Middle" />')
a('  </Label>')
a('  <Label TextLabel="Mediator unresolved (stemness arm)" GraphId="LG101">')
a('    <Graphics CenterX="840.0" CenterY="960.0" Width="250.0" Height="16.0" '
  'ZOrder="28672" FontSize="8" Valign="Middle" />')
a('  </Label>')

for c in COMPARTMENTS:
    cx = (c["x1"] + c["x2"]) / 2
    a(f'  <Label TextLabel="{escape(c["label"])}" GraphId="LB{c["id"]}">')
    a(f'    <Graphics CenterX="{f(c["x1"] + 150)}" CenterY="{f(c["y1"] + 12)}" '
      f'Width="290.0" Height="16.0" ZOrder="28672" FontSize="9" Valign="Middle" '
      'Align="Left" FontStyle="Italic" />')
    a('  </Label>')

# ---- Shapes (compartments)
for c in COMPARTMENTS:
    cx = (c["x1"] + c["x2"]) / 2
    cy = (c["y1"] + c["y2"]) / 2
    w = c["x2"] - c["x1"]
    h = c["y2"] - c["y1"]
    a(f'  <Shape GraphId="{c["id"]}">')
    a(f'    <Graphics CenterX="{f(cx)}" CenterY="{f(cy)}" Width="{f(w)}" Height="{f(h)}" '
      'ZOrder="16384" FontSize="10" Valign="Middle" ShapeType="RoundedRectangle" '
      'LineThickness="2.0" Color="999999" Rotation="0.0" />')
    a('  </Shape>')

a('  <InfoBox CenterX="0.0" CenterY="0.0" />')

# ---- Biopax references
a('  <Biopax>')
for p in PAPERS:
    if p["type"] == "Retracted":
        continue
    a('    <bp:PublicationXref xmlns:bp="http://www.biopax.org/release/biopax-level3.owl#" '
      'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
      f'rdf:id="{p["id"]}">')
    a(f'      <bp:ID rdf:datatype="http://www.w3.org/2001/XMLSchema#string">{p["pmid"]}</bp:ID>')
    a('      <bp:DB rdf:datatype="http://www.w3.org/2001/XMLSchema#string">PubMed</bp:DB>')
    a(f'      <bp:TITLE rdf:datatype="http://www.w3.org/2001/XMLSchema#string">{escape(p["title"])}</bp:TITLE>')
    a(f'      <bp:SOURCE rdf:datatype="http://www.w3.org/2001/XMLSchema#string">{escape(p["journal"])}</bp:SOURCE>')
    a(f'      <bp:YEAR rdf:datatype="http://www.w3.org/2001/XMLSchema#string">{p["year"]}</bp:YEAR>')
    a(f'      <bp:AUTHORS rdf:datatype="http://www.w3.org/2001/XMLSchema#string">{escape(p["first"])}</bp:AUTHORS>')
    a('    </bp:PublicationXref>')
a('  </Biopax>')
a('</Pathway>')

with open("NRF2_CRC_baseline.gpml", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

print(f"nodes={len(N)} interactions={len(R)} helper_edges={hi} states={si}")
print("wrote NRF2_CRC_baseline.gpml")

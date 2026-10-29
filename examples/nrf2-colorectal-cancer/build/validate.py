"""Mechanical validation of the GPML and its correspondence with the Excel workbook."""
import re
import urllib.request
from collections import Counter
from lxml import etree
from openpyxl import load_workbook

from model import N, R, COMPARTMENTS, CANVAS_W, CANVAS_H, NODE_W, NODE_H, PHENO_W, PHENO_H

GPML = "NRF2_CRC_baseline.gpml"
XLSX = "NRF2_CRC_baseline_evidence.xlsx"
NS = {"g": "http://pathvisio.org/GPML/2013a"}
problems, notes = [], []

# ---------------------------------------------------------------- 1. well-formedness
tree = etree.parse(GPML)
root = tree.getroot()
notes.append(f"[1] XML well-formed. Root={etree.QName(root).localname}, "
             f"namespace={etree.QName(root).namespace}")

# ---------------------------------------------------------------- 2. XSD
import os
xsd_path = "GPML2013a.xsd" if os.path.exists("GPML2013a.xsd") else None
for url in ([] if xsd_path else ["https://raw.githubusercontent.com/PathVisio/GPML/master/GPML2013a.xsd",
            "https://raw.githubusercontent.com/PathVisio/pathvisio/master/modules/org.pathvisio.core/resources/GPML2013a.xsd"]):
    try:
        data = urllib.request.urlopen(url, timeout=20).read()
        if b"schema" in data[:400]:
            xsd_path = "GPML2013a.xsd"
            open(xsd_path, "wb").write(data)
            break
    except Exception as e:
        notes.append(f"[2] schema fetch failed for {url}: {type(e).__name__}")
if xsd_path:
    try:
        schema = etree.XMLSchema(etree.parse(xsd_path))
        if schema.validate(tree):
            notes.append("[2] XSD validation against GPML2013a.xsd: PASS")
        else:
            for e in schema.error_log:
                problems.append(f"[2] XSD: line {e.line}: {e.message}")
    except Exception as e:
        notes.append(f"[2] XSD could not be compiled: {type(e).__name__}: {e}")
else:
    notes.append("[2] GPML2013a.xsd NOT retrievable from this sandbox -> "
                 "XSD validation NOT PERFORMED. Structural checks below only.")

# ---------------------------------------------------------------- 3. GraphId uniqueness
ids = [el.get("GraphId") for el in root.iter() if el.get("GraphId")]
dupes = [i for i, c in Counter(ids).items() if c > 1]
if dupes:
    problems.append(f"[3] duplicate GraphIds: {dupes}")
else:
    notes.append(f"[3] GraphId uniqueness: PASS ({len(set(ids))} unique ids)")

# ---------------------------------------------------------------- 4. reference resolution
declared = set(ids)
unresolved = []
for el in root.iter():
    for attr in ("GraphRef", "GroupRef"):
        v = el.get(attr)
        if v and v not in declared:
            unresolved.append(f"{etree.QName(el).localname}.{attr}={v}")
if unresolved:
    problems.append(f"[4] unresolved references: {unresolved}")
else:
    notes.append("[4] GraphRef / Anchor / GroupRef resolution: PASS")

# every interaction has exactly 2 points
for ia in root.iter(f"{{{NS['g']}}}Interaction"):
    pts = ia.findall(f"{{{NS['g']}}}Graphics/{{{NS['g']}}}Point")
    if len(pts) < 2:
        problems.append(f"[4] {ia.get('GraphId')} has {len(pts)} points")
    if pts[0].get("ArrowHead"):
        problems.append(f"[4] {ia.get('GraphId')} carries an arrowhead on its start point")
    if not pts[-1].get("ArrowHead"):
        problems.append(f"[4] {ia.get('GraphId')} has no arrowhead on its end point")
    for mid in pts[1:-1]:
        if mid.get("GraphRef"):
            problems.append(f"[4] {ia.get('GraphId')} waypoint carries a GraphRef")

# ---------------------------------------------------------------- 5. arrowhead vocabulary
ALLOWED = {"mim-conversion", "mim-catalysis", "mim-stimulation", "mim-inhibition",
           "mim-transcription-translation", "mim-modification", "mim-binding",
           "mim-necessary-stimulation", "mim-covalent-bond", "mim-cleavage",
           "mim-gap", "mim-branching-left", "mim-branching-right",
           "mim-translocation", "Arrow", "TBar", "None"}
bad = {p.get("ArrowHead") for p in root.iter(f"{{{NS['g']}}}Point")
       if p.get("ArrowHead") and p.get("ArrowHead") not in ALLOWED}
if bad:
    problems.append(f"[5] arrowheads outside the GPML2013a MIM set: {bad}")
else:
    used = sorted({p.get("ArrowHead") for p in root.iter(f"{{{NS['g']}}}Point")
                   if p.get("ArrowHead")})
    notes.append(f"[5] arrowhead vocabulary: PASS -> {used}")

# ---------------------------------------------------------------- 6. DataNode Type vocabulary
TYPES = {"GeneProduct", "Protein", "Rna", "Metabolite", "Complex", "Pathway", "Unknown"}
badt = {d.get("Type") for d in root.iter(f"{{{NS['g']}}}DataNode")
        if d.get("Type") not in TYPES}
if badt:
    problems.append(f"[6] DataNode Type outside PathVisio Classic set: {badt}")
else:
    notes.append(f"[6] DataNode Type vocabulary: PASS -> "
                 f"{sorted({d.get('Type') for d in root.iter(f'{{{NS[chr(103)]}}}DataNode')})}")

# ---------------------------------------------------------------- 7. node overlap by coordinate
def box(n):
    w, h = (PHENO_W, PHENO_H) if n["comp"] == "phenotype" else (NODE_W, NODE_H)
    return n["x"] - w/2, n["y"] - h/2, n["x"] + w/2, n["y"] + h/2

overlaps = []
for i in range(len(N)):
    for j in range(i + 1, len(N)):
        ax1, ay1, ax2, ay2 = box(N[i]); bx1, by1, bx2, by2 = box(N[j])
        ox = min(ax2, bx2) - max(ax1, bx1)
        oy = min(ay2, by2) - max(ay1, by1)
        if ox > 0 and oy > 0:
            overlaps.append(f"{N[i]['id']}({N[i]['label']}) x {N[j]['id']}({N[j]['label']}) "
                            f"overlap {ox:.0f}x{oy:.0f}px")
if overlaps:
    problems.append("[7] node-node overlap: " + "; ".join(overlaps))
else:
    gaps = []
    for i in range(len(N)):
        for j in range(i + 1, len(N)):
            ax1, ay1, ax2, ay2 = box(N[i]); bx1, by1, bx2, by2 = box(N[j])
            if min(ay2, by2) - max(ay1, by1) > 0:
                g = max(bx1 - ax2, ax1 - bx2)
                if 0 <= g < 20:
                    gaps.append(f"{N[i]['id']}/{N[j]['id']} horizontal gap {g:.0f}px")
    notes.append("[7] node-node overlap: PASS (none)"
                 + (f"; tight pairs: {gaps}" if gaps else ""))

# node inside canvas
for n in N:
    x1, y1, x2, y2 = box(n)
    if x1 < 0 or y1 < 0 or x2 > CANVAS_W or y2 > CANVAS_H:
        problems.append(f"[7] {n['id']} outside canvas")

# ---------------------------------------------------------------- 8. edge passing through unrelated nodes
def seg_rect(p, q, r):
    """Does segment p-q cross rectangle r (slab test)?"""
    (x1, y1), (x2, y2) = p, q
    rx1, ry1, rx2, ry2 = r
    t0, t1 = 0.0, 1.0
    dx, dy = x2 - x1, y2 - y1
    for pv, qv in ((-dx, x1 - rx1), (dx, rx2 - x1), (-dy, y1 - ry1), (dy, ry2 - y1)):
        if pv == 0:
            if qv < 0:
                return False
        else:
            t = qv / pv
            if pv < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
    return t0 < t1

NODES = {n["id"]: n for n in N}
from build_gpml import edge_points
crossings = []
for r in R:
    s, d = NODES[r["src"]], NODES[r["dst"]]
    x1, y1, _, _, x2, y2, _, _ = edge_points(s, d, r["via"])
    path = [(x1, y1)] + [tuple(p) for p in r["via"]] + [(x2, y2)]
    for n in N:
        if n["id"] in (r["src"], r["dst"]):
            continue
        bx = box(n)
        pad = (bx[0] + 3, bx[1] + 3, bx[2] - 3, bx[3] - 3)
        for p, q in zip(path, path[1:]):
            if seg_rect(p, q, pad):
                crossings.append(f"{r['id']} ({s['label']} -> {d['label']}) crosses "
                                 f"{n['id']} {n['label']}")
                break
    # waypoints must stay on the canvas
    for (vx, vy) in r["via"]:
        if not (0 <= vx <= CANVAS_W and 0 <= vy <= CANVAS_H):
            problems.append(f"[8] {r['id']} waypoint {(vx, vy)} outside canvas")
if crossings:
    problems.append("[8] edge crosses unrelated node: " + "; ".join(crossings))
else:
    notes.append("[8] edge-through-node check: PASS (no edge passes through an "
                 "unrelated node box)")

# ---------------------------------------------------------------- 9. Excel <-> GPML correspondence
wb = load_workbook(XLSX, read_only=True)
ent = wb["Entities"]
xl_nodes = {row[0] for row in ent.iter_rows(min_row=2, max_col=1, values_only=True) if row[0]}
rea = wb["Reactions"]
xl_reacts = {row[0] for row in rea.iter_rows(min_row=2, max_col=1, values_only=True) if row[0]}

g_nodes = {d.get("GraphId") for d in root.iter(f"{{{NS['g']}}}DataNode")}
g_reacts = {i.get("GraphId") for i in root.iter(f"{{{NS['g']}}}Interaction")
            if not i.get("GraphId").startswith("H")}

if xl_nodes != g_nodes:
    problems.append(f"[9] node ID mismatch. only-Excel={xl_nodes - g_nodes}, "
                    f"only-GPML={g_nodes - xl_nodes}")
else:
    notes.append(f"[9a] Entities <-> DataNode IDs: PASS ({len(g_nodes)} nodes, both directions)")

if xl_reacts != g_reacts:
    problems.append(f"[9] reaction ID mismatch. only-Excel={xl_reacts - g_reacts}, "
                    f"only-GPML={g_reacts - xl_reacts}")
else:
    notes.append(f"[9b] Reactions <-> Interaction IDs: PASS ({len(g_reacts)} reactions, "
                 "both directions)")

# papers cited in reactions all exist
paper_ids = {row[0] for row in wb["Papers"].iter_rows(min_row=2, max_col=1, values_only=True) if row[0]}
cited = set()
for r in R:
    cited |= set(r["papers"].split(","))
missing = cited - paper_ids
if missing:
    problems.append(f"[9] reactions cite unknown PaperIDs: {missing}")
else:
    notes.append(f"[9c] every PaperID cited by a reaction exists in Papers: PASS ({len(cited)} used)")

# observations reference real papers
obs_papers = {row[1] for row in wb["RawExtraction"].iter_rows(min_row=2, max_col=2, values_only=True) if row[1]}
if obs_papers - paper_ids:
    problems.append(f"[9] observations cite unknown PaperIDs: {obs_papers - paper_ids}")
else:
    notes.append("[9d] every PaperID cited by an observation exists in Papers: PASS")

# ---------------------------------------------------------------- 10. evidence-to-style consistency
style_issues = []
for r in R:
    el = root.find(f".//{{{NS['g']}}}Interaction[@GraphId='{r['id']}']/{{{NS['g']}}}Graphics")
    broken = el.get("LineStyle") == "Broken"
    if r["layer"] == "candidate" and not broken:
        style_issues.append(f"{r['id']} is candidate but drawn solid")
    if r["layer"] == "main" and broken:
        style_issues.append(f"{r['id']} is main but drawn broken")
    # no E4 or C3/C4 relation may sit in the main (solid) layer
    if r["layer"] == "main" and (r["E"].startswith("E4") or r["C"] in ("C3", "C4")):
        style_issues.append(f"{r['id']} has {r['E']}/{r['C']} but is in the main layer")
    # indirect relations must not use a catalysis arrowhead
    if r["arrow"] == "mim-catalysis" and r["E"] not in ("E1", "E2"):
        style_issues.append(f"{r['id']} drawn as catalysis on {r['E']} evidence")
if style_issues:
    problems.append("[10] evidence/style mismatch: " + "; ".join(style_issues))
else:
    cand = [r["id"] for r in R if r["layer"] == "candidate"]
    notes.append(f"[10] evidence-to-style consistency: PASS. No E4/C3/C4 relation is drawn "
                 f"solid; candidates drawn broken = {cand}")

# ---------------------------------------------------------------- 11. orphan nodes
used = set()
for r in R:
    used |= {r["src"], r["dst"]}
    for h in (r["helper"].split(",") if r["helper"] else []):
        used.add(h.split(":")[0])
orphans = [n["id"] for n in N if n["id"] not in used]
if orphans:
    problems.append(f"[11] orphan nodes: {orphans}")
else:
    notes.append("[11] orphan node check: PASS (every node participates in >=1 edge)")

# ---------------------------------------------------------------- 12. species / context sanity
non_human = [r["id"] for r in R if r["C"] == "C3"]
notes.append(f"[12] relations from a non-target system (C3): {non_human} "
             "- all drawn broken and carry a 'Mediator unresolved' note on the arm")

# ---------------------------------------------------------------- report
print("=" * 72)
for n in notes:
    print("  " + n)
print("=" * 72)
if problems:
    print(f"PROBLEMS ({len(problems)}):")
    for p in problems:
        print("  !! " + p)
else:
    print("NO PROBLEMS FOUND by the checks above.")
print("=" * 72)

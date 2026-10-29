"""Render docs/method.md to docs/method.html using the same styling as index.html.

Run from the docs/ directory after editing method.md:
    python3 build_method_page.py
"""
import re
from pathlib import Path

import markdown

HERE = Path(__file__).parent
STYLE = re.search(r"<style>(.*?)</style>", (HERE / "index.html").read_text(), re.S).group(1)

body = markdown.markdown(
    (HERE / "method.md").read_text(),
    extensions=["tables", "fenced_code", "sane_lists"],
)

(HERE / "method.html").write_text(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Method notes &middot; Evidence-Tracked Pathway Map Prompt</title>
<style>{STYLE}</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>Method notes</h1>
  <p class="lede">Design rationale behind the template. The rules themselves live in
  <code>prompts/</code>.</p>
  <div class="btns">
    <a class="btn" href="index.html">&larr; Overview</a>
    <a class="btn" href="../prompts/pathway-map-prompt.en.md">Template (English)</a>
    <a class="btn" href="../prompts/pathway-map-prompt.ja.md">Template (日本語)</a>
  </div>
</header>
{body}
<footer><p>MIT licensed.</p></footer>
</div>
</body>
</html>
""")
print("wrote method.html")

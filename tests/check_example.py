"""Build the real Blowfish example and check the renderer's public contract."""
import html
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HUGO = os.environ.get("HUGO_BIN", "hugo")


def metadata(document, key):
    item = document.split(f'id="pub-{key}"', 1)[1].split('class="jsonresume-pub-item"', 1)[0]
    match = re.search(r'<div class="jsonresume-pub-meta">(.*?)</div>', item, re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).split()) if match else ""


with tempfile.TemporaryDirectory() as destination:
    subprocess.run([HUGO, "--source", str(ROOT / "exampleSite"), "--destination", destination], check=True)
    out = Path(destination)
    cv = (out / "cv/index.html").read_text()
    pubs = (out / "cv/publications/index.html").read_text()
    assert "Alex Example" in cv and 'id="projects-software"' in cv
    assert "Open-source software" in cv and "Example tool" in cv
    assert 'href="/cv/example-cv.pdf"' in cv and 'href="/cv/example-cv.pdf"' in pubs
    assert 'href="/cv/publications/"' in cv
    assert 'href="/cv/publications/example-pubs.bib"' in pubs
    assert "<resume>" not in cv + pubs and "&lt;resume&gt;" not in cv + pubs
    assert ">Home</span>" not in cv  # Host's semantic role exclusion.
    assert metadata(pubs, "report") == "Example Lab · Research Report R1 · 2026"
    assert metadata(pubs, "patent") == "Granted Patent EX 123 B2"
    assert metadata(pubs, "number-only") == "EX 456"
    assert metadata(pubs, "empty") == ""
    assert "Invited talk at <strong>ExampleConf</strong>" in pubs
    assert 'href="https://doi.org/10.1234%2Fexample"' in pubs
    assert 'href="https://example.org/slides/"' in pubs
    assert "UNUSED FALLBACK" not in pubs
    for part in re.findall(r'<div class="jsonresume-pub-meta">(.*?)</div>', pubs, re.S):
        text = html.unescape(re.sub(r"<[^>]+>", "", part)).strip()
        assert not text.startswith("·") and not text.endswith("·")
    css = list((out / "css").glob("jsonresume*.css"))
    assert len(css) == 3, css
    assert "Example City" in cv and "<svg" in cv  # Real Blowfish icon integration.
    print("PASS: CV/publications routes, links, groups, metadata, Markdown, icons and imported CSS")

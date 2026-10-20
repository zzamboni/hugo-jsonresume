"""Build the real Blowfish example and check the renderer's public contract."""
import html
import json
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

# Render both selection modes together to verify that the entry's section,
# rather than a global grouping flag, controls the project type subtitle.
with tempfile.TemporaryDirectory() as fixture, tempfile.TemporaryDirectory() as destination:
    data = Path(fixture) / "jsonresume"
    data.mkdir()
    resume = json.loads((ROOT / "exampleSite/data/jsonresume/resume.json").read_text())
    resume["projects"] = [
        {"name": "Typed project", "type": "Software"},
        {"name": "Untyped project"},
        {"name": "Empty type project", "type": ""},
        {"name": "Literal type project", "type": "R&D <tools> **literal**"},
    ]
    resume["work"][0]["type"] = "Not a project type"
    resume["meta"]["themeOptions"]["sections"] = ["work", "projects", "projects:Software"]
    (data / "resume.json").write_text(json.dumps(resume))
    subprocess.run([HUGO, "--source", str(ROOT / "exampleSite"),
                    "--destination", destination], check=True,
                   env={**os.environ, "HUGO_DATADIR": fixture})
    cv = (Path(destination) / "cv/index.html").read_text()
    full = cv.split('id="projects"', 1)[1].split("</section>", 1)[0]
    grouped = cv.split('id="projects-software"', 1)[1].split("</section>", 1)[0]
    assert '<p class="jsonresume-meta">Software</p>' in full
    assert '<p class="jsonresume-meta">R&amp;D &lt;tools&gt; **literal**</p>' in full
    assert full.count('class="jsonresume-meta"') == 2  # No empty subtitles.
    assert "Typed project" in grouped and 'class="jsonresume-meta"' not in grouped
    assert "Untyped project" in full and "Untyped project" not in grouped
    assert "Not a project type" not in cv
    print("PASS: project types appear only in the full section, escaped as plain text")

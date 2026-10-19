"""Exercise the same data contract with Blowfish and a theme-free host."""
import html
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HUGO = os.environ.get("HUGO_BIN", "hugo")


def metadata(document, key):
    item = document.split(f'id="pub-{key}"', 1)[1].split('class="jsonresume-pub-item"', 1)[0]
    match = re.search(r'<div class="jsonresume-pub-meta">(.*?)</div>', item, re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).split()) if match else ""


def check_contract(out, integration):
    cv = (out / "cv/index.html").read_text()
    pubs = (out / "cv/publications/index.html").read_text()
    assert "Alex Example" in cv and 'id="projects-software"' in cv
    assert "Open-source software" in cv and "Example tool" in cv
    assert 'href="/cv/example-cv.pdf"' in cv and 'href="/cv/example-cv.pdf"' in pubs
    assert 'href="/cv/publications/"' in cv
    assert 'href="/cv/publications/example-pubs.bib"' in pubs
    assert "<resume>" not in cv + pubs and "&lt;resume&gt;" not in cv + pubs
    assert ">Home</span>" not in cv
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
    assert "Example City" in cv and "<svg" in cv
    for document in (cv, pubs):
        assert len(re.findall(r"<main(?:\s|>)", document)) == 1
        assert document.count('id="TableOfContents"') == 1
    css = list((out / "css").glob("jsonresume*.css"))
    if integration == "blowfish":
        assert len(css) == 3, css
        assert "jsonresume-generic" not in cv + pubs
    else:
        assert len(css) == 1 and css[0].name.startswith("jsonresume-generic."), css
        assert "dark:prose-invert" not in cv + pubs
        assert "jsonresume-floating-links" not in cv + pubs
        # Generic profile links remain readable even without brand icons.
        assert '>GitHub</a>' in cv
        assert "assets/icons/" not in cv + pubs
        for document in (cv, pubs):
            ids = re.findall(r'\bid="([^"]+)"', document)
            assert len(ids) == len(set(ids)), "Duplicate anchor IDs"
        styles = css[0].read_text()
        assert "--color-primary" not in styles and ".dark " not in styles
    return cv, pubs


def build(source, destination, *args, check=True):
    result = subprocess.run(
        [HUGO, "--source", str(source), "--destination", str(destination), *args],
        capture_output=True, text=True,
    )
    if check and result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result


def main():
    with tempfile.TemporaryDirectory() as destination:
        out = Path(destination)
        build(ROOT / "exampleSite", out)
        check_contract(out, "blowfish")
        print("PASS: default Blowfish contract")

    with tempfile.TemporaryDirectory() as destination:
        out = Path(destination)
        build(ROOT / "exampleGeneric", out)
        shortcode_pages = check_contract(out, "generic")
        print("PASS: generic shortcodes without a theme")

    # A sibling fixture preserves the example's relative module/data paths.
    with tempfile.TemporaryDirectory(prefix="jsonresume-test-", dir=ROOT) as fixture:
        source = Path(fixture)
        shutil.copytree(ROOT / "exampleGeneric", source, dirs_exist_ok=True)
        cv = source / "content/cv/_index.md"
        pubs = source / "content/cv/publications/index.md"
        for path, shortcode, layout in ((cv, "jsonresume", "cv"), (pubs, "publications", "publications")):
            text = path.read_text().replace("{{< " + shortcode + " >}}", "")
            closing = text.index("\n+++", 4)
            text = text[:closing] + f'\ntype = "jsonresume"\nlayout = "{layout}"' + text[closing:]
            path.write_text(text)

        with tempfile.TemporaryDirectory() as destination:
            out = Path(destination)
            build(source, out)
            native_pages = check_contract(out, "generic")
            for shortcode, native in zip(shortcode_pages, native_pages):
                assert re.sub(r"\s+", " ", shortcode) == re.sub(r"\s+", " ", native)
            print("PASS: generic native layouts match shortcode output")

        # The selection fails early and clearly instead of silently picking a theme.
        config = source / "hugo.toml"
        config.write_text(config.read_text().replace('integration = "generic"', 'integration = "unknown"'))
        with tempfile.TemporaryDirectory() as destination:
            result = build(source, Path(destination), check=False)
            assert result.returncode != 0
            assert 'unknown integration "unknown"' in result.stdout + result.stderr
            print("PASS: invalid integration rejected")


if __name__ == "__main__":
    main()

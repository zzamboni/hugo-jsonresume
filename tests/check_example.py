"""Exercise the same data contract with Blowfish and a theme-free host."""
import html
import json
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
    assert "Richard Hendriks" in cv and 'id="projects-application"' in cv
    assert 'id="projects-library"' in cv
    assert "Featured Projects" in cv and "Miss Direction" in cv
    assert "Open Source" in cv and "Middle-out Compression Toolkit" in cv
    assert "See full credential list on Credly" in cv
    assert 'href="/cv/publications/"' in cv
    assert 'href="/cv/example-cv.pdf"' in pubs
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
    assert "San Francisco" in cv and "<svg" in cv
    for document in (cv, pubs):
        assert len(re.findall(r"<main(?:\s|>)", document)) == 1
        assert document.count('id="TableOfContents"') == 1
        assert document.count('class="jsonresume-attribution"') == 1
        assert 'Rendered with <a href="https://github.com/zzamboni/hugo-jsonresume"' in document
    css = list((out / "css").glob("jsonresume*.css"))
    attribution = [path for path in css if path.name.startswith("jsonresume-attribution.")]
    assert len(attribution) == 1
    assert '@media print{.jsonresume-attribution{display:none!important}}' in attribution[0].read_text()
    css = [path for path in css if path not in attribution]
    if integration == "blowfish":
        assert len(css) == 3, css
        assert "jsonresume-generic" not in cv + pubs
    else:
        assert len(css) == 1 and css[0].name.startswith("jsonresume-generic."), css
        assert "dark:prose-invert" not in cv + pubs
        assert "jsonresume-floating-links" not in cv + pubs
        # Generic profile links remain readable even without brand icons.
        assert '>Twitter</a>' in cv and '>SoundCloud</a>' in cv
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


def check_project_types(example, integration):
    # Keep relative module paths intact while giving each integration its own
    # data. The generic example normally mounts the shared exampleSite data.
    with tempfile.TemporaryDirectory(prefix="jsonresume-test-", dir=ROOT) as fixture:
        source = Path(fixture)
        shutil.copytree(ROOT / example, source, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("themes", "resources", "public"))
        config = source / "hugo.toml"
        config.write_text(config.read_text().replace('../exampleSite/data', 'data'))
        data = source / "data/jsonresume"
        data.mkdir(parents=True, exist_ok=True)
        resume = json.loads((ROOT / "exampleSite/data/jsonresume/resume.json").read_text())
        resume["projects"] = [
            {"name": "Typed project", "type": "Software"},
            {"name": "Untyped project"},
            {"name": "Empty type project", "type": ""},
            {"name": "Literal type project", "type": "R&D <tools> **literal**"},
        ]
        resume["work"][0]["type"] = "Not a project type"
        resume["meta"]["themeOptions"]["sections"] = ["work", "projects", "projects:Software"]
        # Exercise module-specific URLs/roles without altering the exported
        # Eventide sample's own links and options.
        resume["meta"]["themeOptions"]["links"] = [
            {"name": "PDF", "url": "<resume>.pdf", "icon": "download"},
            {"name": "Publications", "url": "publications/", "icon": "quote-left"},
            {"name": "Home", "url": "/", "role": "site-home"},
        ]
        (data / "resume.json").write_text(json.dumps(resume))
        with tempfile.TemporaryDirectory() as destination:
            build(source, Path(destination), "--themesDir", str(ROOT / "exampleSite/themes"))
            cv = (Path(destination) / "cv/index.html").read_text()
            full = cv.split('id="projects"', 1)[1].split("</section>", 1)[0]
            grouped = cv.split('id="projects-software"', 1)[1].split("</section>", 1)[0]
            assert '<p class="jsonresume-meta">Software</p>' in full
            assert '<p class="jsonresume-meta">R&amp;D &lt;tools&gt; **literal**</p>' in full
            assert full.count('class="jsonresume-meta"') == 2
            assert "Typed project" in grouped and 'class="jsonresume-meta"' not in grouped
            assert "Untyped project" in full and "Untyped project" not in grouped
            assert "Not a project type" not in cv
            assert 'href="/cv/example-cv.pdf"' in cv
            assert 'href="/cv/publications/"' in cv
            assert ">Home</span>" not in cv
            assert "<resume>" not in cv and "&lt;resume&gt;" not in cv
        print(f"PASS: {integration} project type subtitles, grouping and escaping")


def check_toc_settings(example, integration):
    # Each case overrides a different level, including both explicit booleans.
    # Blowfish ships an article-level false default; generic has no such default.
    cases = [
        ({}, (False, False), (True, True)),
        ({"eventide": False}, (False, False), (False, True)),
        ({"eventide": True}, (False, False), (True, True)),
        ({"article": True, "eventide": False}, (True, True), (False, True)),
        ({"article": False, "eventide": True}, (False, False), (True, True)),
        ({"module": False, "article": True, "eventide": True}, (False, False), (False, False)),
        ({"module": True, "article": False, "eventide": False}, (True, True), (True, True)),
        ({"cv": False, "pubs": True, "module": True}, (False, True), (False, True)),
        ({"cv": True, "pubs": False, "module": False}, (True, False), (True, False)),
        ({"cv": True, "pubs": True, "empty": True}, (False, False), (False, False)),
    ]
    with tempfile.TemporaryDirectory(prefix="jsonresume-test-", dir=ROOT) as fixture:
        source = Path(fixture)
        shutil.copytree(ROOT / example, source, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("themes", "resources", "public"))
        config = source / "hugo.toml"
        original_config = config.read_text().replace('../exampleSite/data', 'data')
        data = source / "data/jsonresume"
        data.mkdir(parents=True, exist_ok=True)
        pages = [source / "content/cv/_index.md", source / "content/cv/publications/index.md"]
        original_pages = [re.sub(r'^showTableOfContents = .*\n', '', p.read_text(), flags=re.M) for p in pages]
        for settings, blowfish, generic in cases:
            text = original_config
            if "module" in settings:
                text = re.sub(r'(\[params\.jsonresume\])',
                              r'\1\nshowTableOfContents = ' + str(settings['module']).lower(), text)
            if "article" in settings:
                text += '\n[params.article]\nshowTableOfContents = ' + str(settings['article']).lower() + '\n'
            config.write_text(text)
            for key, page, original in zip(("cv", "pubs"), pages, original_pages):
                setting = f'showTableOfContents = {str(settings[key]).lower()}\n' if key in settings else ''
                page.write_text(original.replace('+++\n', '+++\n' + setting, 1))
            resume = json.loads((ROOT / "exampleSite/data/jsonresume/resume.json").read_text())
            options = resume["meta"]["themeOptions"]
            options.pop("showTableOfContents", None)
            if "eventide" in settings:
                options["showTableOfContents"] = settings["eventide"]
            pubs = json.loads((ROOT / "exampleSite/data/jsonresume/publications.json").read_text())
            if settings.get("empty"):
                options["sections"] = ["projects"]
                resume["projects"] = []
                pubs["sections"] = []
            (data / "resume.json").write_text(json.dumps(resume))
            (data / "publications.json").write_text(json.dumps(pubs))
            with tempfile.TemporaryDirectory() as destination:
                out = Path(destination)
                build(source, out, "--themesDir", str(ROOT / "exampleSite/themes"))
                expected = blowfish if integration == "blowfish" else generic
                for path, enabled in zip(("cv/index.html", "cv/publications/index.html"), expected):
                    document = (out / path).read_text()
                    assert document.count('id="TableOfContents"') == int(enabled), (integration, settings, path)
                    if not enabled:
                        assert 'class="jsonresume-toc"' not in document
                        assert 'class="toc ps-5' not in document
                    if not settings.get("empty"):
                        assert ('Richard Hendriks' if path == 'cv/index.html' else 'An Example Report') in document
        print(f"PASS: {integration} TOC precedence, independent pages and empty sections")


def check_attribution_settings(example, integration):
    with tempfile.TemporaryDirectory(prefix="jsonresume-test-", dir=ROOT) as fixture:
        source = Path(fixture)
        shutil.copytree(ROOT / example, source, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("themes", "resources", "public"))
        config = source / "hugo.toml"
        original_config = config.read_text()
        pages = [source / "content/cv/_index.md", source / "content/cv/publications/index.md"]
        originals = [page.read_text() for page in pages]
        # False must survive defaulting, and either page can override the module.
        for module, cv, pubs, expected in (
            (False, None, None, (False, False)),
            (False, True, None, (True, False)),
            (True, False, True, (False, True)),
        ):
            config.write_text(re.sub(r'(\[params\.jsonresume\])',
                                    r'\1\nshowAttribution = ' + str(module).lower(), original_config))
            for page, original, setting in zip(pages, originals, (cv, pubs)):
                value = '' if setting is None else f'showAttribution = {str(setting).lower()}\n'
                page.write_text(original.replace('+++\n', '+++\n' + value, 1))
            with tempfile.TemporaryDirectory() as destination:
                out = Path(destination)
                build(source, out, "--themesDir", str(ROOT / "exampleSite/themes"))
                for path, enabled in zip(("cv/index.html", "cv/publications/index.html"), expected):
                    document = (out / path).read_text()
                    assert document.count('class="jsonresume-attribution"') == int(enabled), (integration, path, expected)
        print(f"PASS: {integration} attribution defaults, page overrides and print stylesheet")


def check_attribution_languages(example, integration):
    with tempfile.TemporaryDirectory(prefix="jsonresume-test-", dir=ROOT) as fixture:
        source = Path(fixture)
        shutil.copytree(ROOT / example, source, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("themes", "resources", "public"))
        config = source / "hugo.toml"
        config.write_text('defaultContentLanguage = "de"\n' + config.read_text()
                          .replace('locale = "en"', 'locale = "de"')
                          .replace('languageCode = "en"', 'languageCode = "de"'))
        translations = source / "i18n"
        translations.mkdir(exist_ok=True)
        for translated, prefix in ((False, "Rendered with"), (True, "Erstellt mit")):
            if translated:
                (translations / "de.yaml").write_text(
                    'jsonresume_attribution:\n  other: "Erstellt mit {{ .Module }}"\n')
            with tempfile.TemporaryDirectory() as destination:
                out = Path(destination)
                build(source, out, "--themesDir", str(ROOT / "exampleSite/themes"))
                for path in ("cv/index.html", "cv/publications/index.html"):
                    document = (out / path).read_text()
                    credit = re.search(r'<p class="jsonresume-attribution">(.*?)</p>', document, re.S)
                    assert credit and prefix in credit[1], (integration, translated, path)
                    assert 'href="https://github.com/zzamboni/hugo-jsonresume"' in credit[1]
        print(f"PASS: {integration} non-English default language fallback and host translation")


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

    for example, integration in (("exampleSite", "blowfish"), ("exampleGeneric", "generic")):
        check_project_types(example, integration)
        check_toc_settings(example, integration)
        check_attribution_settings(example, integration)
        check_attribution_languages(example, integration)

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

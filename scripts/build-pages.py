"""Build both examples into one Pages artifact, including subpath smoke checks."""
import argparse
from html.parser import HTMLParser
import os
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self, document):
        super().__init__()
        self.hrefs = []
        self.feed(document)

    def handle_starttag(self, tag, attrs):
        self.hrefs.extend(value for key, value in attrs if key == "href" and value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Pages root URL, including repository path")
    parser.add_argument("--destination", default="public", help="Output directory (must not exist)")
    args = parser.parse_args()
    base = args.base_url.rstrip("/") + "/"
    if urlsplit(base).scheme not in ("http", "https") or not urlsplit(base).netloc:
        parser.error("--base-url must be an absolute HTTP(S) URL")
    out = Path(args.destination).resolve()
    out.mkdir(parents=True, exist_ok=False)
    for integration, source in (("blowfish", "exampleSite"), ("generic", "exampleGeneric")):
        url = base + integration + "/"
        subprocess.run([
            os.environ.get("HUGO_BIN", "hugo"), "--source", str(ROOT / source),
            "--baseURL", url, "--destination", str(out / integration), "--minify",
        ], check=True, cwd=ROOT)
        prefix = urlsplit(url).path
        cv = (out / integration / "cv/index.html").read_text()
        pubs = (out / integration / "cv/publications/index.html").read_text()
        assert "Richard Hendriks" in cv and "An Example Report" in pubs
        assert f"{prefix}cv/publications/" in Links(cv).hrefs
        for document in (cv, pubs):
            assert f'{prefix}css/jsonresume' in document
            assert not any(href.startswith("/cv/") for href in Links(document).hrefs)
        if integration == "generic":
            assert prefix in Links(cv).hrefs
            assert f"{prefix}cv/" in Links(pubs).hrefs
    shutil.copyfile(ROOT / "scripts/pages-index.html", out / "index.html")
    print(f"Built and checked both examples in {out}")


if __name__ == "__main__":
    main()

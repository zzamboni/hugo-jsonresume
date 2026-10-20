# JSON Resume in Hugo

Render JSON Resume and an optional bibliography as native Hugo pages using
Blowfish's typography, icons, breadcrumbs, navigation and table of contents.
This is a **Blowfish-specific Hugo Module**, not a standalone theme.

## Requirements and installation

Tested with Hugo Extended **0.166.0**, Blowfish **v3.8.0**, and Go **1.25.1**.
Install Go to resolve Hugo Modules. Keep the host's existing Blowfish setup;
the module does not import another copy of the theme.

From a Hugo site, initialize Go module metadata if it is not already present:

```sh
hugo mod init github.com/example/my-site
```

Add to `config/_default/module.toml` (preserving existing mounts/imports):

```toml
[[imports]]
path = "github.com/zzamboni/hugo-jsonresume"
```

Then resolve a reviewed commit and commit both `go.mod` and `go.sum`:

```sh
hugo mod get github.com/zzamboni/hugo-jsonresume@COMMIT_SHA
```

The pin keeps deployments reproducible. Repeat with a new reviewed commit to
update.

## Content and data

The host chooses the public route. For example, `content/cv/_index.md`:

```toml
+++
title = "Curriculum Vitae"
type = "jsonresume"
layout = "cv"
+++
```

Create `content/cv/publications/index.md` for the optional bibliography:

```toml
+++
title = "Publications"
description = "Selected publications and talks."
type = "jsonresume"
layout = "publications"
+++
```

The publications page is a child of the CV page. This relationship resolves
CV download links from the bibliography. The layout supplies its own TOC.
The host retains control of content paths, page metadata, data snapshots,
downloaded PDFs/BibTeX, images, menus, link filtering and build workflows.

Place your JSON Resume at `data/jsonresume/resume.json`. Text fields support
Markdown. 

Many of the [Eventide theme](https://github.com/zzamboni/jsonresume-theme-eventide#options) options are supported:
Optional `meta.themeOptions` supports `sections`, `sectionLabels`,
explicit `projects:<type>` section identifiers, and
action `links` (objects with `name`, `url`, optional `icon` and `role`).
Grouped projects are selected by explicit `projects:<type>` identifiers in
`sections`.

The bibliography input is **normalized JSON**, not raw BibTeX:

```json
{
  "sections": [
    {"id": "reports", "title": "Reports", "entries": [
      {"key": "example-report", "title": "An Example Report",
       "authors": "Alex Example", "institution": "Example Lab",
       "type": "Research Report", "number": "R1", "year": 2026}
    ]}
  ],
  "links": []
}
```

Store it at `data/jsonresume/publications.json`. [resume-toolkit](https://github.com/zzamboni/resume-toolkit) can generate
this format; other producers may supply it directly. Entries support `url`,
`editor`, `doi`, `note`, and venue fields in this order: `journal`, `booktitle`,
`publisher`, `school`, `institution`, `howpublished`. `type` and `number` are
rendered together; dots separate only populated metadata parts. Keep entry
keys stable because `#pub-<key>` anchors are public permalinks.

## Configuration

In `config/_default/params.toml`:

```toml
[jsonresume]
  resumeData = "jsonresume.resume"
  publicationsData = "jsonresume.publications"
  resumeStem = "example-cv"
  # publicationsURL = "/cv/publications/"
  # publicationsDescription = "Override the page description."
  # excludeLinkRoles = ["site-home"]
```

Data paths are dot-separated keys in Hugo's data tree; their defaults are
shown above. Set `resumeStem` when links contain `<resume>`; for example,
`<resume>.pdf` becomes `/cv/example-cv.pdf`. Relative action URLs resolve from
the current page, while `<resume>` on publications resolves from its CV
parent. Put the corresponding downloads under the host's `static/` tree.
Without a stem, use explicit filenames rather than `<resume>` links.
The bibliography-note URL defaults to the CV's `publications/` child.
The publications title comes from front matter; an optional
`publicationsDescription` overrides the page description. No roles are
excluded by default. Icons use Blowfish names, with common Font Awesome
aliases and a generic-link fallback for action icons.

## Example and validation

The synthetic `exampleSite/` demonstrates `/cv/` routes, download links,
project groups, publications and fallback metadata. It deliberately includes
no personal data or generated PDFs. Replace its illustrative download URLs
with real host-owned files before publishing a site.

Clone the tested Blowfish version into the example (only needed once):

```sh
git clone --depth 1 --branch v3.8.0 https://github.com/nunocoracao/blowfish.git exampleSite/themes/blowfish
hugo server --source exampleSite
python3 tests/check_example.py
```

The example's Go replacement points to this checkout for development; it is
not mounted into consuming sites. The check builds with real Blowfish and
checks routes, section selection, action links, metadata and imported CSS.
CI runs it with the pinned theme commit and Hugo version.

## Origin and license

The profile layout adapts Blowfish's
MIT-licensed profile partial. See `LICENSE` and `NOTICE`.

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

Place your JSON Resume at `data/jsonresume/resume.json`. Descriptions,
summaries, entry titles and highlights support Markdown.
See [Eventide option compatibility](#eventide-option-compatibility) for the
supported presentation options and differences from Eventide.

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

## Eventide option compatibility

The renderer can reuse the following [Eventide options](https://github.com/zzamboni/jsonresume-theme-eventide#options)
from your JSON Resume. These settings belong under `meta.themeOptions` in
the JSON file, not in Hugo's `params.toml`. Only `sections`, `sectionLabels`
and `links` are read; the other Eventide settings are ignored.

| Eventide setting | Support in hugo-jsonresume |
| --- | --- |
| `sections` | Supported. Selects and orders CV sections, including explicit `projects:<type>` groups. Defaults differ from Eventide; see below. |
| `sectionLabels` | Supported. Changes section headings using the exact section identifier as the key. Labels support Markdown. |
| `links` | Supported with differences. Supplies labeled action links and desktop floating shortcuts. Icons and URL placeholders differ; see below. |
| `projectsByType` | Ignored. Does not automatically group projects. Use `projects:<type>` identifiers in `sections` instead. |
| `colors` | Ignored. Eventide's light/dark color pairs do not apply; colors follow the host's Blowfish palette and light/dark mode. |
| `icons` | Ignored. Does not switch between Font Awesome and Feather. Icons come from Blowfish's SVG assets. |
| `footer_left` | Ignored. Footer content comes from the host site's theme. |
| `footer_right` | Ignored. Footer content comes from the host site's theme. |
| `showTableOfContents` | Ignored, including `false`. The renderer supplies a TOC whenever it has nonempty sections. Disabling it requires a template override. |

### Section selection and labels

Without a nonempty `sections` list, the CV uses this order:

```json
["work", "education", "projects", "certificates", "awards", "publications", "skills", "languages", "references"]
```

Unlike Eventide's defaults, this omits `volunteer` and `interests`, and puts
certificates before awards. You can explicitly include `volunteer` and
`interests`; they use the shared entry renderer. A custom list replaces the
default list, so sections left out of it are omitted. Sections with no entries
are always omitted. An empty list falls back to the defaults rather than
hiding every section. Entries retain their order in the input data.

Use `sectionLabels` to rename headings. Unspecified labels are derived from
the section identifier (or the type suffix for project groups). This changes
headings only; it does not translate dates or other interface text.

For example, this selects two project groups without `projectsByType`:

```json
{
  "meta": {
    "themeOptions": {
      "sections": ["work", "projects:application", "projects:library", "skills"],
      "sectionLabels": {
        "work": "Experience",
        "projects:application": "Applications",
        "projects:library": "Libraries"
      }
    }
  }
}
```

Each `projects:<type>` group selects projects whose `type` exactly matches
the suffix, including case. Types are not discovered automatically. Projects
with other types, or no type, are omitted unless another listed section selects
them. A plain `projects` section includes **all** projects, even when explicit
groups are also listed; combining them can repeat entries. This differs from
Eventide's untyped-project catch-all when grouping is enabled.

In the full `projects` section, a project's nonempty `type` is shown as a
subtitle in plain text, like Eventide's ungrouped project metadata. Explicit
`projects:<type>` groups omit this subtitle because the section heading
already identifies the type. No `projectsByType` setting is needed.

These settings affect the CV only. The separate publications page takes its
order from the normalized bibliography's `sections` array, its headings from
each section's `title`, and its content from `entries`.

### Action links

Set `meta.themeOptions.links` to an array of objects with `name` and `url`,
plus an optional `icon`. No default download links are generated when the
array is absent or empty. Defaults that `resume-toolkit` supplies for Eventide
are not added during a Hugo build.

```json
{
  "meta": {
    "themeOptions": {
      "links": [
        {"name": "Download CV", "url": "<resume>.pdf", "icon": "fa-file-pdf"},
        {"name": "GitHub", "url": "https://github.com/example", "icon": "github"},
        {"name": "Home", "url": "/", "icon": "link", "role": "site-home"}
      ]
    }
  }
}
```

Links appear inline with their names and as icon-only floating shortcuts on
screens at least 1024px wide. The inline links remain available on smaller
screens; there is no Eventide-style mobile link overlay. Floating shortcuts
are hidden when printing.

Use a Blowfish icon name such as `github` or `download`. These exact Font
Awesome aliases are also recognized (case-insensitively):

| Eventide icon value | Blowfish icon |
| --- | --- |
| `fa-file-pdf`, `fa-regular fa-file-pdf` | `download` |
| `fa-house`, `fa-regular fa-house` | `link` |
| `fa-quote-left` | `quote-left` |
| `fa-file-lines` | `file-lines` |

This is not a general Font Awesome class parser: for example, use `github`
rather than `fa-brands fa-github`. Missing or unknown icons fall back to
`link`; they are not inferred from the link name. The corresponding SVG asset
must exist in the host's Hugo assets. Profile icons likewise use Blowfish
names derived from the lowercased profile `network`.

`<resume>` expands using the Hugo `resumeStem` setting and the CV route; see
[Configuration](#configuration). The `<publications>` placeholder that
`resume-toolkit` expands for Eventide is not expanded here. Root-relative
URLs and HTTP(S) URLs are preserved; other URLs
are prefixed with the current page route. Other schemes such as `mailto:`
are not supported in action links (use `basics.email` for the contact email).

The optional `role` is a hugo-jsonresume extension: the host can hide links
with matching roles through `excludeLinkRoles`, without changing the shared
JSON Resume. No roles are excluded by default. On the separate publications
page, action links come from the bibliography data's top-level `links` array,
not the CV's `meta.themeOptions.links`; the same icon and URL rules apply.

### Images and note entries

Eventide also supports extensions on individual entries, outside
`meta.themeOptions`:

- **Certificate badges and organization logos:** `image` works on certificate,
  work and education entries (and other entries using the shared renderer).
  It displays as a small logo beside the entry. Supply an image URL or a
  host-owned static path; the module does not copy or download images.
- **Certificate notes:** a minimal entry with `name` and `url`, without
  `issuer`, `date` or `image`, renders its name as a link and suppresses the
  additional “View certificate” link.
- **Publication notes:** minimal `name`/`url` entries render as linked titles.
  The renderer does not use Eventide's metadata-based note classification.
  A truthy `bibfiles` field marks a bibliography note, suppressing authors;
  if it has no `url`, the module adds a link to `publicationsURL` instead.
- **Project notes:** entries containing only a `description` render without
  a heading; a `type` can place them in an explicit project group.

Notes use the normal entry layout and stay in input order. In particular,
certificate and publication notes are not moved ahead of other entries as
they are in Eventide. These compatibility notes describe presentation
extensions, not complete parity with every JSON Resume field Eventide renders.

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

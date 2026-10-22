# JSON Resume in Hugo

Render JSON Resume and an optional bibliography inside a Hugo site.
**Blowfish is the default integration**, retaining its typography, icons,
breadcrumbs and table of contents. A **generic integration** supplies scoped
CSS and labeled links for other themes, without a theme-specific icon library
or Tailwind. This is a Hugo Module, not a standalone theme. It does not depend
on Eventide or execute resume-toolkit during a Hugo build.

## Requirements and installation

Tested with Hugo Extended **0.166.0**, Blowfish **v3.8.0**, and Go **1.25.1**.
Install Go to resolve Hugo Modules. Keep the host's existing theme setup;
the module does not import a theme. The generic example needs no theme installed.

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
the JSON file, not in Hugo's `params.toml`. The renderer reads `sections`,
`sectionLabels`, `links` and the CV fallback `showTableOfContents`; the other
Eventide settings are ignored.

| Eventide setting | Support in hugo-jsonresume |
| --- | --- |
| `sections` | Supported. Selects and orders CV sections, including explicit `projects:<type>` groups. Defaults differ from Eventide; see below. |
| `sectionLabels` | Supported. Changes section headings using the exact section identifier as the key. Labels support Markdown. |
| `links` | Supported with differences. Supplies labeled action links in both integrations and desktop floating shortcuts in Blowfish. Icons and URL placeholders differ; see below. |
| `projectsByType` | Ignored. Does not automatically group projects. Use `projects:<type>` identifiers in `sections` instead. |
| `colors` | Ignored. Blowfish uses the host's palette and light/dark mode; generic inherits host colors and supports its own CSS variables. |
| `icons` | Ignored. Does not switch between Font Awesome and Feather. Blowfish uses its SVG assets; generic uses a built-in link symbol and visible profile network names. |
| `footer_left` | Ignored. Footer content comes from the host site's theme. |
| `footer_right` | Ignored. Footer content comes from the host site's theme. |
| `showTableOfContents` | Supported as the CV fallback when no page, module or applicable theme setting exists. Does not control the separate publications page. See [Table of contents](#table-of-contents). |

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

Links appear inline with their names in both integrations. Blowfish also shows
icon-only floating shortcuts on screens at least 1024px wide, hidden when
printing. Generic has no floating shortcuts. The inline links remain available
on smaller screens; neither integration has Eventide's mobile link overlay.

In the Blowfish integration, use an icon name such as `github` or `download`. These exact Font
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

Generic ignores the action link's `icon` value and uses the same built-in
link symbol for every action, alongside its visible name. Profiles display
their network names rather than theme-specific icons. The same link data can
therefore be shared without installing Blowfish assets in a generic host.

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
  integration = "blowfish" # Default; choose "generic" for other themes.
  # showTableOfContents = true # Optional module-wide default for both pages.
  # showAttribution = false # Hide the module credit on both pages.
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
aliases and a generic-link fallback for action icons in the Blowfish integration.

### Attribution

CV and publications render a small “Rendered with hugo-jsonresume” link below
their content by default. It is hidden when printing, works with both
integrations and shortcodes, and leaves the host theme's footer unchanged.

To hide it on an individual page, add this to its TOML front matter:

```toml
showAttribution = false
```

The page's explicit boolean takes precedence over `[jsonresume].showAttribution`
in `params.toml` (or `[params.jsonresume]` in `hugo.toml`). The default is `true`;
the publications page does not inherit the CV's front matter. Hosts can translate
or customize the wording through the `jsonresume_attribution` i18n key, whose
`{{ .Module }}` value contains the module link.

### Table of contents

The module generates TOC links from the JSON sections because Hugo's normal
`.TableOfContents` only contains Markdown headings. Blowfish supplies its TOC
presentation; the generic integration supplies its own responsive sidebar.
For either integration, the first **present** setting below decides visibility:

1. The page's front matter `showTableOfContents`.
2. The host's `[jsonresume].showTableOfContents` in `params.toml` (or
   `[params.jsonresume]` in `hugo.toml`), applying to both CV and publications.
3. For Blowfish only, `[article].showTableOfContents` in `params.toml` (or
   `[params.article]` in `hugo.toml`), including the theme's supplied default.
4. For the CV only, `meta.themeOptions.showTableOfContents` in the resume JSON.
5. `true` when none of the above is set.

Use boolean `true` or `false`; explicit `false` is preserved at every level.
Generic does not guess other themes' TOC settings. Its host can use the module
setting or page front matter instead. Blowfish's theme default can disable
the TOC even when Eventide's option is `true`; page or module settings override
that default. No integration renders a TOC or its sidebar when sections are empty.

For example, add this to the CV or publications page's TOML front matter to
disable only that page's renderer TOC:

```toml
showTableOfContents = false
```

The publications page does not inherit the CV's front matter or Eventide option.
Both native module layouts and shortcodes use the same rules. A host theme may
also render its own TOC around a shortcode; these settings control the module's
TOC, and the host remains responsible for its outer page layout.

## Using another theme

Set `integration = "generic"` in `[params.jsonresume]` in `hugo.toml`, or
`[jsonresume]` in `config/_default/params.toml`. An omitted setting continues to
select Blowfish; unknown integration names fail with a configuration error.
The same JSON data, options, action links and publication anchors work in both
integrations.

The generic renderer has its own responsive layout and section TOC. It inherits
the host's fonts and text/link colors. It uses visible network names for social
links and a small built-in link symbol for action buttons. It does not add
breadcrumbs or floating action buttons. Light/dark appearance follows the host's
colors rather than assuming a particular dark-mode class or toggle.

The native `type = "jsonresume"` pages above work with themes whose base template
provides a `main` block. Other themes can embed the renderer in ordinary content
pages using shortcodes:

```go-html-template
{{< jsonresume >}}
```

For the publications child page, use:

```go-html-template
{{< publications >}}
```

Use `{{< ... >}}` so the generated HTML is rendered directly. For shortcode
pages, omit `type = "jsonresume"` and `layout = "cv"` / `"publications"`; the
host's normal page layout should render `.Content`. That layout owns the outer
navigation, page width and any page-title display. A theme that wraps content
in restrictive typography styles may need a small host CSS adjustment.
`exampleGeneric/` demonstrates this with minimal host templates and no theme.

Both renderers generate their TOCs from the JSON sections; these are separate
from Hugo's Markdown `.TableOfContents`. Embed one renderer per page. Keep the
publications page as a child of its CV so download URLs resolve consistently.

Optional CSS variables let the host tune generic presentation:

```css
.jsonresume-generic {
  --jsonresume-accent: #176d83;
  --jsonresume-border: rgb(128 128 128 / .35);
  --jsonresume-surface: rgb(128 128 128 / .13);
  --jsonresume-scroll-offset: 6rem;
}
```

The accent colors CV entry markers. Link colors, including hover/visited and
dark-mode states, remain controlled by the host's anchor rules. To use the accent
for links as well, explicitly opt in from your host stylesheet:

```css
.jsonresume-generic a { color: var(--jsonresume-accent); }
```

Only add that rule when defining the variable; choose an accent appropriate to
each appearance. Without overrides, the renderer uses the host's link colors
and translucent neutral borders/surfaces.

### Implementation and customization

Public partials `jsonresume/cv.html` and `jsonresume/publications.html` dispatch
to `jsonresume/integrations/<integration>/`. Each integration owns its page
markup, styling and icon behavior. The original Blowfish CSS paths remain intact;
generic pages load only `css/jsonresume-generic.css`.

Shared helpers handle data lookup (`data.html`), section selection
(`cv-sections.html`, `publication-sections.html`), dates, action URL resolution
and role filtering (`links.html`), publication metadata (`publication-meta.html`),
and TOC visibility/section links (`show-toc.html`, `toc-markup.html`). Both integrations also reuse the
existing semantic entry markup (`entry.html`, `publication-entry.html`) and
labeled action-link markup (`action-links.html`). Host overrides at these paths
continue to take precedence.

There is no theme detection or adapter registration framework. A future supported
theme can add its own integration when there is a concrete need. Generic support
is an embedding option, not a promise of automatic visual matching for all themes.

## Example and validation

The synthetic `exampleSite/` demonstrates `/cv/` routes, download links,
project groups, publications and fallback metadata. It deliberately includes
no personal data or generated PDFs. Replace its illustrative download URLs
with real host-owned files before publishing a site.

Clone the tested Blowfish version into the example (only needed once):

```sh
git clone --depth 1 --branch v3.8.0 https://github.com/nunocoracao/blowfish.git exampleSite/themes/blowfish
hugo server --source exampleSite
```

Or serve the generic example, with no theme clone required:

```sh
hugo server --source exampleGeneric
```

Both expose `/cv/` and `/cv/publications/`. Their data is shared from
`exampleSite/data/`; illustrative download links do not point to generated PDFs.

`exampleSite/data/jsonresume/resume.json` is a JSON export of Eventide's
[editor sample](https://github.com/zzamboni/jsonresume-theme-eventide/blob/main/editor/sample-resume.js)
(source blob `f11011f304dceda578b5ae7b8ec68eaff8839627`), using the
`@jsonresume/schema` **1.3.1** sample selected by Eventide's lockfile. It preserves
the editor's fictional Richard Hendriks data, remote image URLs and all
`meta.themeOptions`, including options this module ignores. Serving the example
loads those remote images in the browser. The separate normalized bibliography
remains a synthetic fixture for testing publication metadata and fallbacks.

Both examples' Go replacements point to this checkout for development; examples
are not mounted into consuming sites. Run `python3 tests/check_example.py` after
cloning Blowfish. The checks build both integrations and cover routes, sections,
action links, metadata, icons, imported CSS, generic shortcodes/native layouts
and invalid integration selection. CI runs them with the pinned Blowfish commit
and Hugo version.

## Origin and license

The profile layout adapts Blowfish's
MIT-licensed profile partial. See `LICENSE` and `NOTICE`.

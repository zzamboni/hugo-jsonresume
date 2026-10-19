# Hugo JSON Resume

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
update. Never commit a local `replace` directive into a consuming production
site. Host templates/assets at the same paths override the imported module.

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
Markdown. Optional `meta.themeOptions` supports `sections`, `sectionLabels`,
explicit `projects:<type>` section identifiers, and
action `links` (objects with `name`, `url`, optional `icon` and `role`).
Grouped projects are selected by explicit `projects:<type>` identifiers in
`sections`; the boolean `projectsByType` alone does not expand them.

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

Store it at `data/jsonresume/publications.json`. resume-toolkit can generate
this shape; other producers may supply it directly. Entries support `url`,
`editor`, `doi`, `note`, and venue fields in this order: `journal`, `booktitle`,
`publisher`, `school`, `institution`, `howpublished`. `type` and `number` are
rendered together; dots separate only populated metadata parts. Keep entry
keys stable because `#pub-<key>` anchors are public permalinks.

## Configuration

In `config/_default/params.toml`:

```toml
[jsonresume]
  integration = "blowfish" # Default; choose "generic" for other themes.
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

Set an accent appropriate to each appearance if overriding it. Without overrides,
the renderer inherits link colors and uses translucent neutral borders/surfaces.

### Implementation and customization

Public partials `jsonresume/cv.html` and `jsonresume/publications.html` dispatch
to `jsonresume/integrations/<integration>/`. Each integration owns its page
markup, styling and icon behavior. The original Blowfish CSS paths remain intact;
generic pages load only `css/jsonresume-generic.css`.

Shared helpers handle data lookup (`data.html`), section selection
(`cv-sections.html`, `publication-sections.html`), dates, action URL resolution
and role filtering (`links.html`), publication metadata (`publication-meta.html`),
and the TOC's section links (`toc-markup.html`). Both integrations also reuse the
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

Both examples' Go replacements point to this checkout for development; examples
are not mounted into consuming sites. Run `python3 tests/check_example.py` after
cloning Blowfish. The checks build both integrations and cover routes, sections,
action links, metadata, icons, imported CSS, generic shortcodes/native layouts
and invalid integration selection. CI runs them with the pinned Blowfish commit
and Hugo version.

## Origin and license

Extracted from `zzamboni/zzamboni.org` staging commit
`eb336a4b1cbbb324ada30c3b49ea9793383b8a9d`, retaining the rendering behavior
and namespaced `jsonresume-*` styles. The profile layout adapts Blowfish's
MIT-licensed profile partial. See `LICENSE` and `NOTICE`.

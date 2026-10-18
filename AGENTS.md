# Development guidance

- This is a Blowfish-specific Hugo Module. Keep the host's content, personal
  data, download filenames, routing policy and publishing workflows outside it.
- Preserve the renderer's public template paths, CSS names, data contract and
  publication anchors. Document intentional behavior changes in README.md.
- Keep exampleSite synthetic and runnable with the pinned Blowfish version.
- Run `python3 tests/check_example.py` with Hugo Extended and Go installed.
  Set HUGO_BIN to an alternate Hugo executable when necessary.
- Use ordinary descriptive commits for collaborative work. Reserve `auto:`
  for commits made by automated workflows.
- For extraction/integration changes, compare rendered CV and bibliography
  output against the consuming site before claiming compatibility.

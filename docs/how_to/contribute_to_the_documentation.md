# Contribute to the documentation

Documentation sources live in `docs/`; `mkdocs.yml` defines navigation, the
Material theme, and Markdown extensions. Work from the plugin root.

## Install documentation tools

In your development environment:

```sh
python -m pip install -e '.[dev]'
```

For documentation-only work without installing NOMAD, install the documentation
dependencies declared in that extra:

```sh
python -m pip install mkdocs 'mkdocs-material==8.1.1' pymdown-extensions mkdocs-click
```

## Preview and build

```sh
python -m mkdocs serve
```

Open the local URL printed by MkDocs. Check navigation, tables, code blocks,
and the tutorial's YAML. Stop the preview with Ctrl+C.

Before committing:

```sh
python -m mkdocs build --strict
```

The generated site goes into `site/` by default. It is build output, not source
documentation. Building does not publish the site. The repository has a separate
GitHub Actions documentation deployment workflow; review its triggers before
publishing.

## Where content belongs

| Page | Purpose |
| --- | --- |
| Home | What the plugin does and where to start |
| Tutorial | One complete path from a new archive to a refreshed plot |
| How-to guides | Installation, configuration, troubleshooting, and contribution tasks |
| Explanation | Why the components and data flows behave as they do |
| Reference | Exact names, defaults, formats, and supported interfaces |

Use relative Markdown links between pages and add any new page to `mkdocs.yml`.
Keep runnable examples self-contained. Distinguish a schema-only file from one
that also contains a `data` entry. Validate behavior against the source, and label
synthetic example measurements as such. Do not use real exported data in examples.

When adding a local asset, include the file and verify its path in the built site.
The `docs/theme` and `docs/stylesheets` directories customize appearance; ordinary
content edits belong in the Markdown pages.

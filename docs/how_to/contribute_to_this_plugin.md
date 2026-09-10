# Contribute to the plugin

## Set up a development checkout

From a standalone `qa-plotter` checkout:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

Use a NOMAD-compatible environment. Installing the package is necessary for
entry-point discovery; adding `src` to `PYTHONPATH` alone does not register the
schema and normalizer with NOMAD. NOMAD's parser tests also need its system
libraries, including libmagic, available in the test environment.

## Find the relevant code

| Area | Location under `src/qa_plotter/` |
| --- | --- |
| Source requests, validation, timestamps, CSV command | `scraper.py` |
| Automatic fetching and connection configuration | `normalizers/` |
| Archive structures and fallback figure | `schema_packages/schema_package.py` |
| CSV recognition and grouped import | `parsers/` |
| Example YAML archive | `example_uploads/manati_qa/mri_qa.archive.yaml` |

The package also contains generated template features, including a greeting API
and greeting schema. They are not part of the MANATI scraping path. Do not assume
the template API is an endpoint for triggering QA refreshes.

## Verify changes

Run commands from the plugin root:

```sh
python -m pytest tests/test_scraper.py tests/parsers tests/normalizers -q
python -m pytest tests -q
ruff check .
ruff format . --check
```

The focused QA tests cover timestamp conversion, scanner filtering, missing QA
results, request failures, CSV validation and replacement, archive grouping,
normalizer selection, refresh behavior, and default/custom figures. Fetches are
mocked; these tests do not contact MANATI or prove live network connectivity.
The full suite also includes generated template tests.

For changes affecting normalization, test both direct `MRIQAPlot` entries and
YAML-derived schemas. Check that unrelated entries do not fetch, failures do not
partially assign source results, and reprocessing does not duplicate arrays or
figures. Backend figure checks do not replace browser verification for GUI changes.

Update the [reference](../reference/references.md) when changing defaults, command
options, or quantities, and build the documentation before submitting changes.

## Package and deploy

Declare runtime dependencies in `pyproject.toml`. The parent deployment installs
plugins with `--no-deps`, so new runtime dependencies also need to be available
in its NOMAD image. Example YAML files under `src/qa_plotter/example_uploads` are
included by `MANIFEST.in`.

Commit and push the plugin first, then commit its new submodule revision in the
parent distribution repository. See [Installation](install_this_plugin.md) for
the deployment sequence. Do not commit generated documentation output, exported
MANATI measurements, or a local virtual environment.

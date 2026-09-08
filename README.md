# qa-plotter

A plotter for the mri qa data containing the scraping

This `nomad` plugin was generated with `Cookiecutter` along with `@nomad`'s [`cookiecutter-nomad-plugin`](https://github.com/FAIRmat-NFDI/cookiecutter-nomad-plugin) template.

## Fetch MANATI data during normalization (no CSV required)

Use the ready-to-upload schema and entry in
[`mri_qa.archive.yaml`](src/qa_plotter/example_uploads/manati_qa/mri_qa.archive.yaml).
After deploying the updated plugin, upload that file once and process it.
Reprocess the entry whenever you want to fetch current MANATI data and refresh
its plot. This is triggered by normalization, not by opening the plot, and is
not a scheduled background scraper.

For an existing YAML plotting schema, replace its `base_sections` with:

```yaml
base_sections:
  - qa_plotter.schema_packages.schema_package.MRIQAPlot
```

Remove `data_file`, `TableData`, and the `tabular`/`tabular_parser` annotations.
The new base already supplies `EntryData`, `PlotSection`, and the four array
quantities `datetime`, `roi_snr`, `description`, and `coil`. Keep your existing
`plotly_graph_object` annotation referencing `#datetime` and `#roi_snr`.
Without a custom plotting annotation, the base generates an open ROI SNR over
time figure automatically. This also works for entries created directly from
`MRIQAPlot`. Existing entries must be reprocessed after updating the plugin.
The supplied example also includes `data: {m_def: MRI_QA}` to create an entry
using its embedded schema; a schema definition alone does not fetch data.

The plugin normalizer runs before NOMAD's metainfo/plot normalization. It fetches
all matching measurements, sorts them by acquisition time, and replaces the four
aligned arrays. It only handles entries derived from `MRIQAPlot`; other entries
and CSV imports do not trigger MANATI requests. Failed fetches raise a processing
error without replacing the current in-memory arrays. An empty successful fetch
clears them. The plot retains your single-trace design, including measurements
from different descriptions and coils.

The default connection matches the original script. To override it, configure
the plugin in the deployment's NOMAD configuration (and preserve this in the
configuration template used by your deployment script):

```yaml
plugins:
  entry_points:
    options:
      'qa_plotter.normalizers:normalizer_entry_point':
        base_url: 'http://manati:3000'
        scanner: 'MAGNETOM Terra.X'
        collection: 'QA_7T'
        timeout: 30
```

The NOMAD processing worker must be able to resolve and reach `manati:3000`.
Commit and push the plugin changes, then the distribution's submodule revision,
and run `deploy.sh update` before using this schema.

## MANATI QA export and NOMAD import

Install the plugin into your Python environment (`pip install .` from this folder).
Run the scraper on a machine that can reach MANATI:

```sh
qa-plotter-scrape --output mri_qa.csv
```

The defaults match the original script: `http://manati:3000`, scanner
`MAGNETOM Terra.X`, and collection `QA_7T`. Override them when needed:

```sh
qa-plotter-scrape --base-url http://manati:3000 \
  --scanner "MAGNETOM Terra.X" --collection QA_7T \
  --timeout 30 --output mri_qa.csv
```

`python -m qa_plotter.scraper` accepts the same options. The command reads the
MANATI API; it does not modify MANATI or automatically upload data to NOMAD.
Each invocation exports all matching measurements, sorted by acquisition time,
and replaces the output file only after a successful export. It does not append
or deduplicate measurements. A missing QA collection (HTTP 404) is skipped;
other HTTP errors, timeouts, and malformed measurements fail the command.
An empty result produces a header-only CSV. The timeout applies to each request.

Upload `mri_qa.csv` through NOMAD's upload interface and process the upload.
With this plugin installed, NOMAD recognizes CSV files with this exact header:

```csv
datetime,ROI_SNR,Description,Coil
```

The entry's `data` contains `source_file`, `measurement_count`, and repeated
`series` sections, one per `(Description, Coil)` pair. Each series stores
`description`, `coil`, and aligned arrays `datetime` and `roi_snr`, ordered by
time. These CSV-import arrays are available for subsequent plotting. For automatic
fetching and a plot, use the normalization workflow above. Timestamps are ISO strings in MANATI's local
time, without an inferred timezone, and SNR is dimensionless. The original
four-column CSV format is retained, so scanner and collection are not embedded
in the file: use separate exports for different scanner/collection selections.

After modifying this submodule, commit and push it first, then commit and push
the updated `packages/qa-plotter` revision in the distribution repository.
Run `deploy.sh update` to rebuild the image with the new scraper and parser.

## Development

If you want to develop locally this plugin, clone the project and in the plugin folder, create a virtual environment (you can use Python 3.10, 3.11 or 3.12):
```sh
git clone https://github.com/PTiringer/qa-plotter.git
cd qa-plotter
python3.11 -m venv .pyenv
. .pyenv/bin/activate
```

Make sure to have `pip` upgraded:
```sh
pip install --upgrade pip
```

We recommend installing `uv` for fast pip installation of the packages:
```sh
pip install uv
```

Install the `nomad-lab` package:
```sh
uv pip install -e '.[dev]'
```

### Run the tests

You can run locally the tests:
```sh
python -m pytest -sv tests
```

where the `-s` and `-v` options toggle the output verbosity.

Our CI/CD pipeline produces a more comprehensive test report using the `pytest-cov` package. You can generate a local coverage report:
```sh
uv pip install pytest-cov
python -m pytest --cov=src tests
```

### Run linting and auto-formatting

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting the code. Ruff auto-formatting is also a part of the GitHub workflow actions. You can run locally:
```sh
ruff check .
ruff format . --check
```

### Debugging

For interactive debugging of the tests, use `pytest` with the `--pdb` flag. We recommend using an IDE for debugging, e.g., _VSCode_. If that is the case, add the following snippet to your `.vscode/launch.json`:
```json
{
  "configurations": [
      {
        "name": "<descriptive tag>",
        "type": "debugpy",
        "request": "launch",
        "cwd": "${workspaceFolder}",
        "program": "${workspaceFolder}/.pyenv/bin/pytest",
        "justMyCode": true,
        "env": {
            "_PYTEST_RAISE": "1"
        },
        "args": [
            "-sv",
            "--pdb",
            "<path-to-plugin-tests>",
        ]
    }
  ]
}
```

where `<path-to-plugin-tests>` must be changed to the local path to the test module to be debugged.

The settings configuration file `.vscode/settings.json` automatically applies the linting and formatting upon saving the modified file.

### Documentation on Github pages

To view the documentation locally, install the related packages using:
```sh
uv pip install -r requirements_docs.txt
```

Run the documentation server:
```sh
mkdocs serve
```

## Adding this plugin to NOMAD

Currently, NOMAD has two distinct flavors that are relevant depending on your role as an user:
1. [A NOMAD Oasis](#adding-this-plugin-in-your-nomad-oasis): any user with a NOMAD Oasis instance.
2. [Local NOMAD installation and the source code of NOMAD](#adding-this-plugin-in-your-local-nomad-installation-and-the-source-code-of-nomad): internal developers.

### Adding this plugin in your NOMAD Oasis

Read the [NOMAD plugin documentation](https://nomad-lab.eu/prod/v1/staging/docs/howto/oasis/plugins_install.html) for all details on how to deploy the plugin on your NOMAD instance.

### Adding this plugin in your local NOMAD installation and the source code of NOMAD

We now recommend using the dedicated [`nomad-distro-dev`](https://github.com/FAIRmat-NFDI/nomad-distro-dev) repository to simplify the process. Please refer to that repository for detailed instructions.

## Publish note
In the [GitHub actions workflow](./.github/workflows/publish.yml) for publishing the qa-plotter plugin to PyPI, we commented out the `deploy` job . If you want to publish the plugin to `PyPI`, you need to set up your project in `PyPI`. There are several online tutorials on publishing a Python package to PyPI, e.g., [How to Publish a Python Package to PyPI](https://realpython.com/pypi-publish-python-package/). After that, you can uncomment the `deploy` job in the workflow file and push the changes to GitHub. The workflow will be triggered and the package will be published to `PyPI` when you create a new release on GitHub.

### Template update

We use [`cruft`](https://github.com/cruft/cruft) to update the project based on template changes. To run the check for updates locally, run `cruft update` in the root of the project. More details see the instructions on [`cruft` website](https://cruft.github.io/cruft/#updating-a-project).

## Main contributors
| Name | E-mail     |
|------|------------|
| Peter Tiringer | [peter.tiringer@gmail.com](mailto:peter.tiringer@gmail.com)

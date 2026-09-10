# Reference

## Normalizer configuration

Configuration entry-point ID:

```text
qa_plotter.normalizers:normalizer_entry_point
```

| Setting | Default | Meaning |
| --- | --- | --- |
| `base_url` | `http://manati:3000` | Server root; the scraper adds `/api/...` |
| `scanner` | `MAGNETOM Terra.X` | Exact study scanner name |
| `collection` | `QA_7T` | Series QA collection |
| `timeout` | `30.0` | Positive finite seconds per request |
| `level` | `-1` | Run before metainfo normalization; preserve this ordering |

See the [configuration example](../how_to/use_this_plugin.md#configure-manati).
There are no plugin configuration fields for authentication, retries, scheduling,
or per-entry scanner selection.

## Archive schemas

All classes below are defined in `qa_plotter.schema_packages.schema_package`.

### `MRIQAPlot`

Automatic-fetching base, inheriting NOMAD `EntryData` and `PlotSection`.

| Quantity | Type and shape | Meaning |
| --- | --- | --- |
| `datetime` | string array | ISO local acquisition times |
| `roi_snr` | floating-point array | Dimensionless ROI SNR |
| `description` | string array | Series descriptions |
| `coil` | string array | Coil identifiers |
| `figures` | repeated `PlotlyFigure` subsection | Inherited plotting output |

The normalizer populates the four arrays in matching order. The default figure
is labelled `ROI SNR over time`, opens automatically, and contains a single
`scatter` trace with `lines+markers` and a date x-axis.

Custom `plotly_graph_object`, `plotly_express`, and `plotly_subplots` annotations
are delegated to NOMAD. This plugin does not define a separate annotation syntax.
For the single-trace YAML example, see [Usage](../how_to/use_this_plugin.md#define-a-custom-figure).

### `MRIQA` and `MRISeries`

The CSV parser writes `MRIQA`, not `MRIQAPlot`:

| Field | Meaning |
| --- | --- |
| `MRIQA.source_file` | Input file basename |
| `MRIQA.measurement_count` | Number of imported rows |
| `MRIQA.series` | Repeated `MRISeries`, grouped by description and coil |
| `MRISeries.description` | Group description string |
| `MRISeries.coil` | Group coil string |
| `MRISeries.datetime` | Chronologically ordered timestamp array |
| `MRISeries.roi_snr` | Corresponding SNR array |

These imports do not automatically fetch MANATI data or generate the default QA
plot. `NewSchemaPackage` is a retained greeting example, not a QA schema.

## Command-line interface

```sh
qa-plotter-scrape [--base-url URL] [--scanner NAME] [--collection NAME] \
  [--timeout SECONDS] [--output PATH]
```

Equivalent module invocation: `python -m qa_plotter.scraper`.

| Option | Default | Meaning |
| --- | --- | --- |
| `--base-url` | `http://manati:3000` | MANATI server root |
| `--scanner` | `MAGNETOM Terra.X` | Exact scanner match |
| `--collection` | `QA_7T` | QA collection |
| `--timeout` | `30.0` | Per-request timeout in seconds |
| `--output` | `mri_qa.csv` | Destination file; parent directory must exist |
| `-h`, `--help` | — | Print usage without fetching |

Success prints the number of exported measurements and up to five rows. Handled
request, validation, and file errors print `QA export failed: ...` and exit with
status 1. Argument syntax errors are handled by Python's argument parser.

## CSV format

The parser recognizes `.csv` filenames with the exact header:

```csv
datetime,ROI_SNR,Description,Coil
```

A synthetic example row:

```csv
2025-03-05T10:41:19.703000,42.5,QA scan,Head coil
```

Use UTF-8; the reader also accepts a UTF-8 byte-order mark. The header order is
significant. Fields containing commas must be CSV-quoted. Missing/extra columns,
unparseable timestamps, and non-finite SNR values fail validation. An empty
export consists of the header and imports as zero measurements.

Exports are written to a temporary file in the destination directory and then
replace the destination. They are sorted by timestamp and contain no scanner,
collection, study ID, series ID, or fetch timestamp columns.

## MANATI endpoints and expected fields

| Request | Expected JSON |
| --- | --- |
| `GET /api/studies` | List of studies with `Scanner` and, for selected studies, `id` |
| `GET /api/studies/{id}/series` | List of series with `id`, `Date`, `Time`, `Description`, `Coil` |
| `GET /api/series/{id}/col/{collection}` | Object containing `ROI_SNR`, or HTTP 404 if absent |

Identifiers and collection names are URL-encoded as path segments. Only a QA
request's HTTP 404 is skipped. Study-list errors, series-list errors, other QA
errors, and invalid JSON/data are raised.

## Python helpers

Defined in `qa_plotter.scraper`:

| Object | Purpose |
| --- | --- |
| `Measurement(timestamp, roi_snr, description, coil)` | Immutable validated measurement record |
| `combine_date_time(date_value, time_value)` | Convert MANATI date/time to an ISO local timestamp |
| `fetch_measurements(base_url, scanner, collection, timeout, session)` | Fetch sorted measurements; optional injected HTTP session for testing |
| `write_csv(measurements, output_file)` | Sort and atomically replace a CSV export |
| `read_csv(mainfile)` | Validate and sort an export |
| `main()` | Console command implementation |

## Registered NOMAD components

| Entry point | Role |
| --- | --- |
| `qa_plotter.normalizers:normalizer_entry_point` | Automatic MANATI fetching |
| `qa_plotter.schema_packages:schema_package_entry_point` | QA and retained example schemas |
| `qa_plotter.parsers:parser_entry_point` | CSV parser |
| `qa_plotter.example_uploads:example_upload_entry_point` | Retained generated example upload |
| `qa_plotter.apis:api_entry_point` | Retained greeting API, not a scraping endpoint |

The MANATI example archive is shipped under
`src/qa_plotter/example_uploads/manati_qa/mri_qa.archive.yaml`. The registered
template example-upload entry point still targets `getting_started`; it is not
the MANATI example selector.

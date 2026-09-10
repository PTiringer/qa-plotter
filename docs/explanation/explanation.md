# How the plugin works

## Two paths through the data

The primary path is:

```text
MRIQAPlot entry
  → MRIQANormalizer
  → MANATI HTTP API
  → sorted Measurement objects
  → four aligned archive arrays
  → schema normalization
  → Plotly figure in data.figures
  → NOMAD interface
```

The optional file path is:

```text
MANATI API → scraper command → CSV → MRIQAParser → MRIQA with grouped MRISeries
```

Both paths reuse the same scraper and measurement validation. They produce
separate archive structures because a flat plotting entry and a grouped CSV
import serve different purposes.

## Normalization and entry selection

NOMAD discovers the normalizer through the package's `nomad.plugin` entry point.
Its configured level is `-1`, so it runs before the metainfo normalizer that
invokes schema normalization and creates figures.

The normalizer examines `archive.data` and resolves its base-section definitions.
Only `MRIQAPlot` and schemas derived from it trigger requests. Resolving the bases
also supports YAML-defined schemas, whose base references can be proxies.

The normalizer fetches and validates the complete result before assigning the
arrays. Fetch failures leave the current in-memory arrays untouched and raise an
error to the caller. This does not promise that a failed NOMAD reprocessing job
preserves a previously persisted archive; archive persistence is managed by NOMAD.

## Source traversal and validation

The scraper requests studies, selects the configured scanner, requests its series,
and then requests the configured QA collection for each series. Only HTTP 404
on an individual QA request is treated as a missing measurement. Errors from the
study or series endpoints are not skipped.

SNR values are converted to floats and must be finite. Description and coil must
be strings. MANATI dates and times are combined into ISO timestamps; shortened
numeric times are left-padded to six digits. Fractional seconds are padded or
truncated to six digits. Invalid calendar dates and clock times fail validation.

Timestamps have no inferred timezone. The source date/time values are treated as
local acquisition times, not converted to UTC. Measurements are sorted by the
resulting ISO timestamp.

## Refresh semantics

Every successful normalization fetches the full matching source dataset and
replaces all four arrays. Nothing is appended, and existing source duplicates
are not removed. A successful empty result clears the arrays.

Requests are sequential. There is no retry policy implemented by the scraper,
no pagination handling, no incremental cursor, and no background scheduler.
The study and series endpoints are expected to return JSON lists directly.
Large datasets therefore require one study-list request, one series-list request
per selected study, and one QA request per series.

## Plot generation and display

`MRIQAPlot` inherits from NOMAD's `EntryData` and `PlotSection`. After the fetch,
its schema normalization either uses custom NOMAD plotting annotations or writes
one default `PlotlyFigure` with an open flag and explicit x/y values. Repeated
normalization replaces this default figure instead of accumulating figures.

The default trace uses all timestamps and SNR values with lines and markers.
It does not distinguish coils or series descriptions, perform statistical quality
control, calculate thresholds, or alter measurements.

NOMAD's GUI renders `figures`. Figure placement relative to quantities is a GUI
concern; the project's plot-first overview change is in the `nomad-FAIR` submodule.

## Data provenance limits

The plotting arrays and four-column CSV store time, SNR, description, and coil.
They do not store MANATI study/series IDs, the selected scanner or collection,
the server URL, or a fetch timestamp. Keep track of the deployment configuration
when interpreting an entry. Source settings are shared by the normalizer, so a
configuration change affects the next refresh of every matching entry.

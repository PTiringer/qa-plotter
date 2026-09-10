# Use the plugin

## Configure MANATI

Add the following to the NOMAD configuration used by the processing services:

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

These are the defaults. The scanner name is matched exactly. `timeout` is a
positive, finite number of seconds per HTTP request, not a limit on the entire
normalization run. These settings apply to all automatic QA entries handled by
this normalizer; there are no per-entry source overrides.

In this project's deployment, preserve changes in the configuration template and
in any script that regenerates it. Editing only a generated `nomad.yaml` can lose
the settings on the next deployment. Restart the affected services after changing
configuration, then reprocess the entry.

## Convert an existing CSV plotting schema

Replace its bases with:

```yaml
base_sections:
  - qa_plotter.schema_packages.schema_package.MRIQAPlot
```

Remove `data_file`, `TableData`, and the CSV-specific `tabular` and
`tabular_parser` annotations. The base already supplies all four arrays and
NOMAD plotting support. Retain any other quantities your schema needs.

Keep an existing Plotly annotation if you want a custom figure. Without one,
the base creates an open SNR-over-time plot automatically.

## Define a custom figure

This complete archive retains the original single-trace plot design:

```yaml
definitions:
  name: MRI QA plotting schema
  sections:
    MRI_QA:
      base_sections:
        - qa_plotter.schema_packages.schema_package.MRIQAPlot
      m_annotations:
        plotly_graph_object:
          label: ROI SNR over time
          open: true
          data:
            type: scatter
            mode: lines+markers
            x: '#datetime'
            y: '#roi_snr'
          layout:
            title: ROI SNR over time
            xaxis:
              title: Measurement time
            yaxis:
              title: ROI SNR

data:
  m_def: MRI_QA
```

Custom `plotly_graph_object`, `plotly_express`, or `plotly_subplots` annotations
are handled by NOMAD's `PlotSection` and suppress the plugin's fallback figure.
If a custom annotation is invalid, correct or remove it; the fallback is not
used to recover from an invalid custom plot.

## Export a CSV

On a machine that can reach MANATI, run:

```sh
qa-plotter-scrape --base-url http://manati:3000 \
  --scanner "MAGNETOM Terra.X" --collection QA_7T \
  --timeout 30 --output mri_qa.csv
```

`python -m qa_plotter.scraper` accepts the same arguments. The command prints the
measurement count and up to five rows. It replaces the destination after a
successful export, rather than appending. The destination directory must exist.
This command neither uploads data to NOMAD nor changes MANATI.

Upload the CSV to NOMAD if you want a stored import. The CSV parser creates an
`MRIQA` archive with grouped `series`; it does not create an automatically
refreshing `MRIQAPlot` entry or its default figure. For that workflow use the
[tutorial](../tutorial/tutorial.md).

## Troubleshooting

| Symptom | Check or action |
| --- | --- |
| Unknown `MRIQAPlot` schema | Install the updated plugin into the running image and restart services. |
| No data fetched | Confirm the entry has a `data` section derived from `MRIQAPlot`, then process it. A schema definition alone is insufficient. |
| Connection or DNS failure | Check access to the configured host and port from the processing worker. |
| Empty arrays after successful processing | Check exact scanner spelling, available series, and the selected QA collection. Missing QA records return HTTP 404 and are skipped. |
| Four arrays but no plot | Deploy the version with the default figure, reprocess the entry, and check processing logs and custom plotting annotations. |
| Old values after reopening the page | Reprocess the entry; viewing it does not refresh the source. |
| Quantities appear above the plot | Deploy the project's `nomad-FAIR` GUI change with a full image build. This is an overview layout change outside the plugin. |
| CSV not recognized | Use a `.csv` filename and the exact header shown in the reference. |
| Authentication or server error | HTTP errors other than a missing QA record are raised. There is no built-in login/token configuration. |

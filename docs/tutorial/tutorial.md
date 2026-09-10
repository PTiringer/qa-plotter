# Create a QA entry and plot

This tutorial uses the automatic fetching workflow. You need a NOMAD installation
with the current plugin installed, permission to create an upload, and a processing
worker with access to MANATI. See [Installation](../how_to/install_this_plugin.md)
if the plugin is not yet deployed.

## 1. Create an archive file

Save the following as `mri_qa.archive.yaml`:

```yaml
definitions:
  name: MRI QA plotting schema
  sections:
    MRI_QA:
      base_sections:
        - qa_plotter.schema_packages.schema_package.MRIQAPlot

data:
  m_def: MRI_QA
```

The `definitions` block creates a schema derived from the plugin's plotting base.
The `data` block creates an entry using that schema. A schema definition alone
does not fetch measurements.

You do not need to declare the four measurement quantities or supply a data file.
The base supplies them and creates a default SNR-over-time figure.

## 2. Upload and process

Create a NOMAD upload and add `mri_qa.archive.yaml`. Let NOMAD process the file.
During normalization the plugin selects the configured scanner's studies, reads
their series, and retrieves QA results. It converts the timestamps, sorts the
measurements, and fills the entry's arrays before generating the plot.

## 3. Inspect the result

Open the entry's Overview page. You should see a figure named **ROI SNR over time**
and the `datetime`, `roi_snr`, `description`, and `coil` arrays. Array elements at
the same position belong to the same measurement.

The default figure connects all measurements in one trace, even when descriptions
or coils differ. It is not a separate curve for each coil. Timestamp values are
MANATI local times, without an inferred timezone.

The project-specific NOMAD GUI change places plots before quantities. Other
NOMAD installations may show quantities first; that ordering is controlled by the
GUI, not by this plugin's schema.

## 4. Refresh the entry

Reprocess the entry or its upload when MANATI has new measurements. The plugin
fetches the full matching dataset and replaces the arrays. Reprocessing does not
append another copy of the previous data. Reloading the browser page alone does
not fetch anything.

A successful fetch with no measurements produces empty arrays and an empty default
plot. A failed request raises an error; inspect the processing log before treating
the displayed data as current.

## Next steps

Use the [usage guide](../how_to/use_this_plugin.md) to change connection settings,
add a custom plotting annotation, or diagnose missing data or figures.

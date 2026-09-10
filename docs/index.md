# MRI QA data and plots in NOMAD

`qa-plotter` reads MRI quality-assurance measurements from MANATI and displays
ROI signal-to-noise ratio (SNR) over time in NOMAD. Create a QA entry once, then
process or reprocess it to retrieve the current measurements. No CSV upload is
required for this workflow.

The default source is `http://manati:3000`, scanner `MAGNETOM Terra.X`, and
collection `QA_7T`. Your NOMAD processing worker must be able to reach that server.

## Choose your workflow

| Workflow | Input | Result |
| --- | --- | --- |
| Automatic fetching and plotting | An entry based on `MRIQAPlot` | Four measurement arrays and a figure, refreshed during normalization |
| Command-line export | MANATI connection settings | A chronologically sorted CSV |
| CSV import | An exported CSV uploaded to NOMAD | A structured archive grouped by description and coil |

Opening an entry does not refresh MANATI data. There is no scheduled scraper,
incremental synchronization, or automatic CSV uploader.

## Start here

- [Tutorial](tutorial/tutorial.md): create your first entry and refresh its plot.
- [Installation](how_to/install_this_plugin.md): install the plugin and deploy updates.
- [Usage](how_to/use_this_plugin.md): configure MANATI, customize plots, export CSV, and troubleshoot.
- [Explanation](explanation/explanation.md): understand normalization, data handling, and plotting.
- [Reference](reference/references.md): quantities, settings, commands, and source modules.
- [Code contributions](how_to/contribute_to_this_plugin.md): development and verification.
- [Documentation contributions](how_to/contribute_to_the_documentation.md): preview and build this site.
